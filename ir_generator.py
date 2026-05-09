from parser import (
    Parser, ProgramNode, CanvasNode, ColorNode,
    DrawPixelNode, DrawRectNode, DrawLineNode, RepeatNode
)
from lexer import Lexer

class IRInstruction:
    def __init__(self, op, arg1=None, arg2=None, arg3=None):
        self.op   = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def __repr__(self):
        parts = [self.op]
        for a in [self.arg1, self.arg2, self.arg3]:
            if a is not None:
                parts.append(str(a))
        return '  ' + ' '.join(parts)

class IRGenerator:
    def __init__(self, ast):
        self.ast          = ast
        self.instructions = []   # the final flat IR list

    def generate(self):
        # Walk the AST and emit IR instructions
        self.visit_program(self.ast)
        return self.instructions

    def emit(self, op, arg1=None, arg2=None, arg3=None):
        # Add one instruction to the IR list
        self.instructions.append(IRInstruction(op, arg1, arg2, arg3))

    def visit_program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit(self, node):
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

    # Emit Methods
    def visit_canvas(self, node):
        self.emit('CANVAS', node.width, node.height)

    def visit_color(self, node):
        self.emit('SET_COLOR', node.color)

    def visit_draw_pixel(self, node):
        self.emit('DRAW_PIXEL', node.x, node.y)

    def visit_draw_rect(self, node):
        # Store as DRAW_RECT x1 y1 x2 y2
        self.emit('DRAW_RECT', node.x1, node.y1, (node.x2, node.y2))

    def visit_draw_line(self, node):
        self.emit('DRAW_LINE', node.x1, node.y1, (node.x2, node.y2))

    def visit_repeat(self, node):
        # Unroll the loop: just emit the body N times
        for _ in range(node.count):
            for stmt in node.body:
                self.visit(stmt)

def print_ir(instructions):
    print("\nIntermediate Representation (TAC)")
    for i, instr in enumerate(instructions):
        print(f"[{i:02d}] {instr}")
    print(f"Total: {len(instructions)} instruction(s)")

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

    ir_gen   = IRGenerator(ast)
    ir_code  = ir_gen.generate()
    print_ir(ir_code)
