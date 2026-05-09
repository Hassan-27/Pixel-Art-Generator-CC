import sys
import os

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from ir_generator import IRGenerator, print_ir
from optimizer import Optimizer
from codegen import CodeGenerator

def compile_source(source_code, output_path='output.png', debug=False):
    # Run the full compilation pipeline on source_code string.
    # Returns True on success, False on failure.
    try:
        # Phase 1: Lexical Analysis
        if debug:
            print("\nPhase 1: Lexical Analysis")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        if debug:
            for tok in tokens:
                if tok.type not in ('NEWLINE', 'EOF'):
                    print(f"{tok}")

        # Phase 2: Syntax Analysis
        if debug:
            print("\nPhase 2: Syntax Analysis (Parsing)")
        parser = Parser(tokens)
        ast = parser.parse()
        if debug:
            print("AST nodes:")
            for node in ast.statements:
                print(f"{node}")

        # Phase 3: Semantic Analysis
        if debug:
            print("\nPhase 3: Semantic Analysis")
        analyzer = SemanticAnalyzer(ast)
        table = analyzer.analyze()
        if debug:
            print(f"Symbol Table: {table}")

        # Phase 4: IR Generation
        if debug:
            print("\nPhase 4: IR Generation")
        ir_gen = IRGenerator(ast)
        ir_code = ir_gen.generate()
        if debug:
            print_ir(ir_code)

        # Phase 5: Optimization
        if debug:
            print("\nPhase 5: Optimization")
        optimizer = Optimizer(ir_code)
        optimized_ir = optimizer.optimize()
        if debug:
            print("\nOptimized IR:")
            print_ir(optimized_ir)

        # Phase 6: Code Generation
        if debug:
            print("\nPhase 6: Code Generation")
        codegen = CodeGenerator(optimized_ir)
        codegen.run(output_path)

        return True

    except SyntaxError as e:
        print(f"\n{e}")
        return False
    except Exception as e:
        print(f"\n{e}")
        return False

def run_repl():
    # Interactive REPL: user types a full program line by line,
    # then enters a blank line to compile and run it.
    
    print("=== Pixel Art Generator - Interactive Mode ===")
    print("Type your program line by line.")
    print("Press ENTER on an empty line to compile and run.")
    print("Type 'exit' to quit.\n")

    session = 0

    while True:
        lines = []
        print(">>> ", end='', flush=True)

        while True:
            try:
                line = input()
            except EOFError:
                print("\nExiting.")
                return

            if line.strip().lower() == 'exit':
                print("Goodbye!")
                return

            if line.strip() == '':
                break   # end of input, compile now

            lines.append(line)
            print("... ", end='', flush=True)

        if not lines:
            continue

        source   = '\n'.join(lines)
        session += 1
        out_file = f'repl_output_{session}.png'

        print(f"\nCompiling... -> {out_file}")
        success = compile_source(source, output_path=out_file, debug=False)

        if success:
            print(f"Done! Open '{out_file}' to see your pixel art.\n")
        else:
            print("Compilation failed. Fix the errors and try again.\n")


# CLI

def print_usage():
    print("Pixel Art Generator Compiler")
    print()
    print("Usage:")
    print("python compiler.py <input.pix> Compile a .pix file")
    print("python compiler.py <input.pix> -o <out.png> Specify output filename")
    print("python compiler.py <input.pix> --debug Show all compilation phases")
    print("python compiler.py --interactive Start interactive REPL mode")
    print()
    print("Example:")
    print("python compiler.py my_art.pix -o my_art.png")


def main():
    args = sys.argv[1:]

    # No arguments
    if len(args) == 0:
        print_usage()
        sys.exit(0)

    # Interactive / REPL mode
    if '--interactive' in args:
        run_repl()
        return

    # Get source file
    src_file = args[0]

    if not os.path.exists(src_file):
        print(f"Error: File '{src_file}' not found.")
        sys.exit(1)

    if not src_file.endswith('.pix'):
        print(f"Warning: '{src_file}' does not have a .pix extension.")

    # Parse optional flags
    debug = '--debug' in args
    output_file = 'output.png'

    if '-o' in args:
        idx = args.index('-o')
        if idx + 1 < len(args):
            output_file = args[idx + 1]
        else:
            print("Error: '-o' flag requires an output filename.")
            sys.exit(1)
    else:
        # Default: same name as input but .png
        base = os.path.splitext(src_file)[0]
        output_file = base + '.png'

    # Read source
    with open(src_file, 'r') as f:
        source_code = f.read()

    print(f"Compiling '{src_file}' -> '{output_file}' ...")
    success = compile_source(source_code, output_path=output_file, debug=debug)

    if success:
        print(f"\nSuccess! Pixel art saved to '{output_file}'.")
        sys.exit(0)
    else:
        print("\nCompilation failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
