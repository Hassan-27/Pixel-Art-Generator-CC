import struct
import zlib
import os

from ir_generator import IRGenerator, print_ir
from parser import Parser
from lexer import Lexer

COLOR_MAP = {
    'RED'     : (220,  50,  50),
    'GREEN'   : ( 50, 200,  50),
    'BLUE'    : ( 50,  50, 220),
    'BLACK'   : (  0,   0,   0),
    'WHITE'   : (255, 255, 255),
    'YELLOW'  : (255, 220,   0),
    'CYAN'    : (  0, 210, 210),
    'MAGENTA' : (200,   0, 200),
    'ORANGE'  : (255, 140,   0),
    'PURPLE'  : (128,   0, 128),
}

# How many screen pixels each "art pixel" takes up in the PNG
PIXEL_SIZE = 12

def _png_chunk(chunk_type, data):
    # Build a PNG chunk: length + type + data + CRC
    c = chunk_type + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

def save_png(pixels, width, height, output_path):
    # Save a 2D pixel array as a PNG file.
    # pixels[y][x] = (R, G, B)
  
    # PNG signature
    sig = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk: image header
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = _png_chunk(b'IHDR', ihdr_data)

    # IDAT chunk: compressed image data
    raw_rows = []
    for row in pixels:
        row_bytes = b'\x00'   # filter type 0 (None)
        for (r, g, b) in row:
            row_bytes += bytes([r, g, b])
        raw_rows.append(row_bytes)

    raw_data   = b''.join(raw_rows)
    compressed = zlib.compress(raw_data, 9)
    idat = _png_chunk(b'IDAT', compressed)

    # IEND chunk
    iend = _png_chunk(b'IEND', b'')

    with open(output_path, 'wb') as f:
        f.write(sig + ihdr + idat + iend)

class CodeGenerator:
    def __init__(self, instructions):
        self.instructions  = instructions
        self.canvas_w      = 0
        self.canvas_h      = 0
        self.current_color = (0, 0, 0)
        self.grid          = []   # 2D list of (R,G,B)

    def _init_grid(self):
        # Fill the canvas with WHITE background
        bg = COLOR_MAP['WHITE']
        self.grid = [[bg] * self.canvas_w for _ in range(self.canvas_h)]

    def _set_pixel(self, x, y, color):
        # Set a single art-pixel (bounds-checked)
        if 0 <= x < self.canvas_w and 0 <= y < self.canvas_h:
            self.grid[y][x] = color

    def _draw_rect(self, x1, y1, x2, y2, color):
        # FIll the rectangle with the given color
        for row in range(y1, y2 + 1):
            for col in range(x1, x2 + 1):
                self._set_pixel(col, row, color)

    def _draw_line(self, x1, y1, x2, y2, color):
        # Bresenham's line algorithm — draws a straight line between two points pixel by pixel
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self._set_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1  += sx
            if e2 < dx:
                err += dx
                y1  += sy

    def _scale_grid(self):
        # Scale up each art-pixel to PIXEL_SIZE x PIXEL_SIZE screen pixels
        # so the PNG is big enough to see clearly
        scaled_h = self.canvas_h * PIXEL_SIZE
        scaled_w = self.canvas_w * PIXEL_SIZE
        scaled   = [[(0,0,0)] * scaled_w for _ in range(scaled_h)]

        for row in range(self.canvas_h):
            for col in range(self.canvas_w):
                color = self.grid[row][col]
                for dy in range(PIXEL_SIZE):
                    for dx in range(PIXEL_SIZE):
                        scaled[row * PIXEL_SIZE + dy][col * PIXEL_SIZE + dx] = color

        return scaled, scaled_w, scaled_h

    def run(self, output_path='output.png'):
        # Execute the IR instructions and save the result as a PNG
        for instr in self.instructions:
            op = instr.op

            if op == 'CANVAS':
                self.canvas_w = instr.arg1
                self.canvas_h = instr.arg2
                self._init_grid()

            elif op == 'SET_COLOR':
                self.current_color = COLOR_MAP.get(instr.arg1, (0, 0, 0))

            elif op == 'DRAW_PIXEL':
                self._set_pixel(instr.arg1, instr.arg2, self.current_color)

            elif op == 'DRAW_RECT':
                x2, y2 = instr.arg3
                self._draw_rect(instr.arg1, instr.arg2, x2, y2, self.current_color)

            elif op == 'DRAW_LINE':
                x2, y2 = instr.arg3
                self._draw_line(instr.arg1, instr.arg2, x2, y2, self.current_color)

        # Scale up and write PNG
        scaled_pixels, w, h = self._scale_grid()
        save_png(scaled_pixels, w, h, output_path)
        print(f"[CodeGen] Image saved: {output_path}  ({w}x{h} px)")


if __name__ == '__main__':
    source = """
CANVAS 20 20
COLOR WHITE
DRAW RECT 0 0 19 19
COLOR RED
DRAW RECT 2 2 8 8
COLOR BLUE
DRAW PIXEL 10 10
COLOR GREEN
DRAW LINE 0 0 19 19
"""
    lexer   = Lexer(source)
    tokens  = lexer.tokenize()
    parser  = Parser(tokens)
    ast     = parser.parse()

    from ir_generator import IRGenerator
    ir_gen  = IRGenerator(ast)
    ir_code = ir_gen.generate()

    cg = CodeGenerator(ir_code)
    cg.run('test_output.png')
    print("Done. Open test_output.png to view the result.")
