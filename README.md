# Pixel Art Generator — CS4031 Compiler Construction

**Team Members:**
- Murtaza (23K-0589)
- Muhammad Hassan Khan (23K-0565)
- Muhammad Uzair Uddin Khan (23K-0665)

---

## What is this?

This is a small domain-specific language (DSL) that lets you write simple scripts to create pixel art images. You write commands in a `.pix` file, run the compiler, and it produces a PNG image.

---

## Setup

No external libraries needed. Just Python 3.

```bash
python --version   # make sure it's Python 3.x
```

All files should be in the same folder:
```
lexer.py
parser.py
semantic.py
ir_generator.py
optimizer.py
codegen.py
compiler.py
```

---

## How to Use

**Compile a `.pix` file:**
```bash
python compiler.py my_art.pix
```

**Specify output filename:**
```bash
python compiler.py my_art.pix -o result.png
```

**Debug mode (shows all phases):**
```bash
python compiler.py my_art.pix --debug
```

**Interactive / REPL mode:**
```bash
python compiler.py --interactive
```

---

## Language Reference

### Canvas Setup
Must be the first command. Defines the grid size.
```
CANVAS <width> <height>
```
Example: `CANVAS 20 20`

### Set Color
Sets the drawing color for all following DRAW commands.
```
COLOR <color_name>
```
Available colors: `RED`, `GREEN`, `BLUE`, `BLACK`, `WHITE`, `YELLOW`, `CYAN`, `MAGENTA`, `ORANGE`, `PURPLE`

### Draw Commands
```
DRAW PIXEL <x> <y>             # draw one pixel
DRAW RECT  <x1> <y1> <x2> <y2> # fill a rectangle
DRAW LINE  <x1> <y1> <x2> <y2> # draw a straight line
```
Coordinates start at (0,0) = top-left corner.

### Repeat Loop
```
REPEAT <count> {
    <statements>
}
```

### Comments
Lines starting with `#` are ignored.

---

## Example Programs

### Example 1 — Simple shapes
```
CANVAS 20 20
COLOR RED
DRAW RECT 2 2 8 8
COLOR BLUE
DRAW PIXEL 10 10
COLOR GREEN
DRAW LINE 0 19 19 0
```

### Example 2 — Checkerboard pattern
```
CANVAS 10 10
COLOR BLACK
DRAW PIXEL 0 0
DRAW PIXEL 2 0
DRAW PIXEL 4 0
DRAW PIXEL 1 1
DRAW PIXEL 3 1
DRAW PIXEL 0 2
DRAW PIXEL 2 2
```

### Example 3 — Repeat loop
```
CANVAS 15 15
COLOR YELLOW
REPEAT 5 {
    DRAW PIXEL 7 7
}
COLOR RED
DRAW RECT 3 3 11 11
```

### Example 4 — Border frame
```
CANVAS 16 16
COLOR PURPLE
DRAW RECT 0 0 15 0
DRAW RECT 0 15 15 15
DRAW RECT 0 0 0 15
DRAW RECT 15 0 15 15
COLOR CYAN
DRAW PIXEL 7 7
```

### Example 5 — Diagonal cross
```
CANVAS 20 20
COLOR ORANGE
DRAW LINE 0 0 19 19
COLOR MAGENTA
DRAW LINE 0 19 19 0
```

---

## Compiler Phases

| Phase | File | What it does |
|-------|------|-------------|
| Lexical Analysis | `lexer.py` | Breaks source into tokens |
| Syntax Analysis | `parser.py` | Builds AST from tokens |
| Semantic Analysis | `semantic.py` | Checks for logical errors |
| IR Generation | `ir_generator.py` | Converts AST to flat instructions |
| Optimization | `optimizer.py` | Removes redundant instructions |
| Code Generation | `codegen.py` | Renders PNG from IR |

---

## Error Reporting

Errors include the line number and a clear message. Examples:

```
[Lexer Error] Line 3, Col 7: Unexpected character: '@'
[Parser Error] Line 5, Col 1: Expected an integer but got 'RED'
[Semantic Error] Line 4: DRAW PIXEL (25, 5) is outside the canvas (20x20).
```

---

## File Extensions

Source files use the `.pix` extension.

---

## Known Limitations

- No variables or arithmetic expressions
- REPEAT loops cannot be nested more than one level deep (works but not tested beyond that)
- Maximum canvas size is 512x512
