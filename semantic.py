from parser import (
    Parser, ProgramNode, CanvasNode, ColorNode,
    DrawPixelNode, DrawRectNode, DrawLineNode, RepeatNode
)
from lexer import Lexer

class SymbolTable:
    def __init__(self):
        self.canvas_width  = None
        self.canvas_height = None
        self.current_color = None
        self.canvas_defined = False
        self.color_defined  = False

    def set_canvas(self, w, h):
        self.canvas_width   = w
        self.canvas_height  = h
        self.canvas_defined = True

    def set_color(self, color):
        self.current_color = color
        self.color_defined = True

    def in_bounds(self, x, y):
        # Check if (x, y) is within the canvas
        return (0 <= x < self.canvas_width) and (0 <= y < self.canvas_height)

    def __repr__(self):
        return (f"SymbolTable(canvas={self.canvas_width}x{self.canvas_height}, "
                f"color={self.current_color})")

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast    = ast
        self.table  = SymbolTable()
        self.errors = []   # collect all errors instead of stopping at first

    def error(self, msg, line=None):
        location = f"Line {line}: " if line else ""
        self.errors.append(f"[Semantic Error] {location}{msg}")

    def analyze(self):
        # Walk the AST and run all checks
        self.visit_program(self.ast)

        if self.errors:
            print("\nSemantic Errors")
            for e in self.errors:
                print(e)
            raise Exception(f"Semantic analysis failed with {len(self.errors)} error(s).")

        print("[Semantic Analysis] OK - No errors found.")
        print(f"Canvas : {self.table.canvas_width} x {self.table.canvas_height}")
        print(f"Final color in use: {self.table.current_color}")
        return self.table   # return the symbol table for later phases

    def visit_program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit(self, node):
        # Dispatch to the correct visit method based on node type
        if isinstance(node, CanvasNode):
            self.visit_canvas(node)
        elif isinstance(node, ColorNode):
            self.visit_color(node)
        elif isinstance(node, DrawPixelNode):
            self.visit_draw_pixel(node)
        elif isinstance(node, DrawRectNode):
            self.visit_draw_rect(node)
        elif isinstance(node, DrawLineNode):
            self.visit_draw_line(node)
        elif isinstance(node, RepeatNode):
            self.visit_repeat(node)
        else:
            self.error(f"Unknown node type: {type(node).__name__}")

    def visit_canvas(self, node):
        if node.width <= 0 or node.height <= 0:
            self.error("Canvas dimensions must be greater than 0.", node.line)
            return
        if node.width > 512 or node.height > 512:
            self.error("Canvas dimensions cannot exceed 512x512.", node.line)
            return
        self.table.set_canvas(node.width, node.height)

    def visit_color(self, node):
        # Color names are already validated by the parser (only keywords pass)
        self.table.set_color(node.color)

    def visit_draw_pixel(self, node):
        if not self.table.canvas_defined:
            self.error("DRAW used before CANVAS is defined.", node.line)
            return
        if not self.table.color_defined:
            self.error("DRAW used before COLOR is set.", node.line)
            return
        if not self.table.in_bounds(node.x, node.y):
            self.error(
                f"DRAW PIXEL ({node.x}, {node.y}) is outside the canvas "
                f"({self.table.canvas_width}x{self.table.canvas_height}).",
                node.line
            )

    def visit_draw_rect(self, node):
        if not self.table.canvas_defined:
            self.error("DRAW used before CANVAS is defined.", node.line)
            return
        if not self.table.color_defined:
            self.error("DRAW used before COLOR is set.", node.line)
            return
        # Check all four corners
        for (x, y) in [(node.x1, node.y1), (node.x2, node.y2)]:
            if not self.table.in_bounds(x, y):
                self.error(
                    f"DRAW RECT corner ({x}, {y}) is outside the canvas "
                    f"({self.table.canvas_width}x{self.table.canvas_height}).",
                    node.line
                )
        if node.x1 > node.x2 or node.y1 > node.y2:
            self.error(
                f"DRAW RECT: top-left ({node.x1},{node.y1}) must be "
                f"above/left of bottom-right ({node.x2},{node.y2}).",
                node.line
            )

    def visit_draw_line(self, node):
        if not self.table.canvas_defined:
            self.error("DRAW used before CANVAS is defined.", node.line)
            return
        if not self.table.color_defined:
            self.error("DRAW used before COLOR is set.", node.line)
            return
        for (x, y) in [(node.x1, node.y1), (node.x2, node.y2)]:
            if not self.table.in_bounds(x, y):
                self.error(
                    f"DRAW LINE endpoint ({x}, {y}) is outside the canvas "
                    f"({self.table.canvas_width}x{self.table.canvas_height}).",
                    node.line
                )

    def visit_repeat(self, node):
        if node.count < 1:
            self.error(f"REPEAT count must be at least 1, got {node.count}.", node.line)
            return
        # Visit each statement in the repeat body
        for stmt in node.body:
            self.visit(stmt)

if __name__ == '__main__':
    source = """
CANVAS 20 20
COLOR RED
DRAW RECT 2 2 5 5
COLOR BLUE
DRAW PIXEL 10 10
REPEAT 3 {
    DRAW PIXEL 3 3
}
"""
    lexer    = Lexer(source)
    tokens   = lexer.tokenize()
    parser   = Parser(tokens)
    ast      = parser.parse()

    analyzer = SemanticAnalyzer(ast)
    table    = analyzer.analyze()
    print("\nFinal Symbol Table:", table)