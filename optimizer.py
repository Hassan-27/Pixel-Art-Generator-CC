from ir_generator import IRGenerator, IRInstruction, print_ir
from parser import Parser
from lexer import Lexer


class Optimizer:
    def __init__(self, instructions):
        self.instructions = instructions  # original IR list

    def optimize(self):
        # Run all optimizations in sequence and return cleaned IR
        ir = self.instructions

        before_count = len(ir)

        ir = self.remove_redundant_colors(ir)
        ir = self.remove_duplicate_pixels(ir)

        after_count = len(ir)
        removed = before_count - after_count

        print(
            f"[Optimizer] {before_count} instruction(s) before optimization.")
        print(f"[Optimizer] {after_count} instruction(s) after optimization.")
        print(f"[Optimizer] {removed} instruction(s) removed.")

        return ir

    def remove_redundant_colors(self, instructions):
        result = []
        active_color = None

        for i, instr in enumerate(instructions):
            if instr.op == 'SET_COLOR':
                new_color = instr.arg1

                # Case (a): same color as already active -> skip
                if new_color == active_color:
                    continue

                # Case (b): look ahead — if the next non-CANVAS instruction
                # is also a SET_COLOR, this one is useless
                next_draw = self._next_relevant(instructions, i + 1)
                if next_draw is not None and next_draw.op == 'SET_COLOR':
                    continue  # this color is overwritten before any draw

                active_color = new_color
                result.append(instr)

            elif instr.op in ('DRAW_PIXEL', 'DRAW_RECT', 'DRAW_LINE'):
                result.append(instr)
            else:
                result.append(instr)

        return result

    def _next_relevant(self, instructions, start):
        # Return the next instruction that is not CANVAS
        for j in range(start, len(instructions)):
            if instructions[j].op != 'CANVAS':
                return instructions[j]
        return None

    def remove_duplicate_pixels(self, instructions):
        result = []
        drawn_pixels = set()   # stores (color, x, y) tuples already drawn
        active_color = None

        for instr in instructions:
            if instr.op == 'SET_COLOR':
                active_color = instr.arg1
                result.append(instr)

            elif instr.op == 'DRAW_PIXEL':
                key = (active_color, instr.arg1, instr.arg2)
                if key in drawn_pixels:
                    continue   # skip duplicate
                drawn_pixels.add(key)
                result.append(instr)

            else:
                result.append(instr)

        return result


if __name__ == '__main__':
    source = """
CANVAS 20 20
COLOR RED
COLOR RED
DRAW PIXEL 5 5
REPEAT 4 {
    DRAW PIXEL 5 5
}
COLOR BLUE
COLOR GREEN
DRAW RECT 1 1 8 8
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    from ir_generator import IRGenerator
    ir_gen = IRGenerator(ast)
    ir_code = ir_gen.generate()

    print("\nBefore Optimization")
    print_ir(ir_code)

    print()
    optimizer = Optimizer(ir_code)
    optimized_ir = optimizer.optimize()

    print()
    print("After Optimization")
    print_ir(optimized_ir)
