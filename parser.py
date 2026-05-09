from lexer import Lexer, TT_KEYWORD, TT_INT, TT_LBRACE, TT_RBRACE, TT_NEWLINE, TT_EOF


class ProgramNode:
    # Root node (holds all statements in the program)
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f'ProgramNode({self.statements})'


class CanvasNode:
    # CANVAS width height
    def __init__(self, width, height, line):
        self.width = width
        self.height = height
        self.line = line

    def __repr__(self):
        return f'CanvasNode(width={self.width}, height={self.height})'


class ColorNode:
    # COLOR color_name
    def __init__(self, color, line):
        self.color = color
        self.line = line

    def __repr__(self):
        return f'ColorNode(color={self.color})'


class DrawPixelNode:
    # DRAW PIXEL x y
    def __init__(self, x, y, line):
        self.x = x
        self.y = y
        self.line = line

    def __repr__(self):
        return f'DrawPixelNode(x={self.x}, y={self.y})'


class DrawRectNode:
    # DRAW RECT x1 y1 x2 y2
    def __init__(self, x1, y1, x2, y2, line):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.line = line

    def __repr__(self):
        return f'DrawRectNode(x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2})'


class DrawLineNode:
    # DRAW LINE x1 y1 x2 y2
    def __init__(self, x1, y1, x2, y2, line):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.line = line

    def __repr__(self):
        return f'DrawLineNode(x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2})'


class RepeatNode:
    # REPEAT count { statements }
    def __init__(self, count, body, line):
        self.count = count   # how many times to repeat
        self.body = body    # list of statements inside { }
        self.line = line

    def __repr__(self):
        return f'RepeatNode(count={self.count}, body={self.body})'


# Colors that are valid after a COLOR command
VALID_COLORS = {
    'RED', 'GREEN', 'BLUE', 'BLACK', 'WHITE',
    'YELLOW', 'CYAN', 'MAGENTA', 'ORANGE', 'PURPLE'
}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def error(self, msg):
        tok = self.current()
        raise SyntaxError(
            f"[Parser Error] Line {tok.line}, Col {tok.col}: {msg}")

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # return EOF

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect_keyword(self, value):
        # Consume a keyword token with a specific value, or raise error
        tok = self.current()
        if tok.type == TT_KEYWORD and tok.value == value:
            return self.advance()
        self.error(
            f"Expected keyword '{value}' but got '{tok.value}' ({tok.type})")

    def expect_int(self):
        # Consume an integer token, or raise error
        tok = self.current()
        if tok.type == TT_INT:
            return self.advance()
        self.error(f"Expected an integer but got '{tok.value}' ({tok.type})")

    def skip_newlines(self):
        # Skip over any newline tokens
        while self.current().type == TT_NEWLINE:
            self.advance()

    def parse(self):
        # Entry point: parse the full program
        statements = []
        self.skip_newlines()

        while self.current().type != TT_EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()

        return ProgramNode(statements)

    def parse_statement(self):
        # Decide which statement type we're looking at
        tok = self.current()

        if tok.type == TT_KEYWORD:
            if tok.value == 'CANVAS':
                return self.parse_canvas()
            elif tok.value == 'COLOR':
                return self.parse_color()
            elif tok.value == 'DRAW':
                return self.parse_draw()
            elif tok.value == 'REPEAT':
                return self.parse_repeat()
            else:
                self.error(f"Unexpected keyword '{tok.value}'")
        elif tok.type == TT_NEWLINE:
            self.advance()
            return None
        else:
            self.error(f"Unexpected token '{tok.value}' of type {tok.type}")

    def parse_canvas(self):
        line = self.current().line
        self.expect_keyword('CANVAS')
        width = self.expect_int().value
        height = self.expect_int().value
        return CanvasNode(width, height, line)

    def parse_color(self):
        line = self.current().line
        self.expect_keyword('COLOR')
        tok = self.current()
        if tok.type == TT_KEYWORD and tok.value in VALID_COLORS:
            self.advance()
            return ColorNode(tok.value, line)
        self.error(
            f"Expected a color name (e.g. RED, BLUE) but got '{tok.value}'")

    def parse_draw(self):
        line = self.current().line
        self.expect_keyword('DRAW')
        tok = self.current()

        if tok.type != TT_KEYWORD:
            self.error(f"Expected PIXEL, RECT, or LINE after DRAW")

        if tok.value == 'PIXEL':
            self.advance()
            x = self.expect_int().value
            y = self.expect_int().value
            return DrawPixelNode(x, y, line)

        elif tok.value == 'RECT':
            self.advance()
            x1 = self.expect_int().value
            y1 = self.expect_int().value
            x2 = self.expect_int().value
            y2 = self.expect_int().value
            return DrawRectNode(x1, y1, x2, y2, line)

        elif tok.value == 'LINE':
            self.advance()
            x1 = self.expect_int().value
            y1 = self.expect_int().value
            x2 = self.expect_int().value
            y2 = self.expect_int().value
            return DrawLineNode(x1, y1, x2, y2, line)

        else:
            self.error(
                f"Unknown draw command '{tok.value}'. Expected PIXEL, RECT, or LINE.")

    def parse_repeat(self):
        line = self.current().line
        self.expect_keyword('REPEAT')
        count = self.expect_int().value

        self.skip_newlines()

        # Expect opening brace
        if self.current().type != TT_LBRACE:
            self.error(f"Expected '{{' after REPEAT {count}")
        self.advance()  # consume {

        self.skip_newlines()

        # Parse statements inside the block
        body = []
        while self.current().type != TT_RBRACE:
            if self.current().type == TT_EOF:
                self.error(
                    "Unexpected end of file inside REPEAT block (missing '}')")
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.skip_newlines()

        self.advance()  # consume }
        return RepeatNode(count, body, line)


if __name__ == '__main__':
    source = """
CANVAS 20 20
COLOR RED
DRAW RECT 2 2 5 5
COLOR BLUE
DRAW PIXEL 10 10
REPEAT 5 {
    DRAW PIXEL 3 3
}
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    print("=== AST ===")
    for node in ast.statements:
        print(node)
