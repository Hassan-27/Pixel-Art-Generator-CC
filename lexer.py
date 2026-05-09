import re

KEYWORDS = {
    'CANVAS', 'COLOR', 'DRAW', 'REPEAT',
    'PIXEL', 'RECT', 'LINE',
    'RED', 'GREEN', 'BLUE', 'BLACK', 'WHITE',
    'YELLOW', 'CYAN', 'MAGENTA', 'ORANGE', 'PURPLE'
}

TT_KEYWORD   = 'KEYWORD'
TT_INT       = 'INT'
TT_IDENT     = 'IDENT'
TT_LBRACE    = 'LBRACE'    
TT_RBRACE    = 'RBRACE'    
TT_NEWLINE   = 'NEWLINE'
TT_EOF       = 'EOF'

class Token:
    def __init__(self, type_, value, line, col):
        self.type  = type_
        self.value = value
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, col={self.col})'

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.pos    = 0          # current character position
        self.line   = 1          # current line number
        self.col    = 1          # current column number
        self.tokens = []

    def error(self, msg):
        raise SyntaxError(f"[Lexer Error] Line {self.line}, Col {self.col}: {msg}")

    def current_char(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def advance(self):
        # Move to the next character, tracking line and column
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_whitespace(self):
        # Skip spaces and tabs, but NOT newlines (they are tokens)
        while self.current_char() in (' ', '\t'):
            self.advance()

    def skip_comment(self):
        # Skip single-line comments that start with '#'
        while self.current_char() is not None and self.current_char() != '\n':
            self.advance()

    def read_number(self):
        # Read a sequence of digits and return an INT token
        start_col = self.col
        num_str = ''
        while self.current_char() is not None and self.current_char().isdigit():
            num_str += self.advance()
        return Token(TT_INT, int(num_str), self.line, start_col)

    def read_word(self):
        # Read a keyword or identifier
        start_col = self.col
        word = ''
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
            word += self.advance()

        # Check if it is a reserved keyword
        if word.upper() in KEYWORDS:
            return Token(TT_KEYWORD, word.upper(), self.line, start_col)
        else:
            return Token(TT_IDENT, word, self.line, start_col)

    def tokenize(self):
        # Walks through the source and produces a list of tokens.

        while self.pos < len(self.source):
            ch = self.current_char()

            # Skip spaces and tabs
            if ch in (' ', '\t'):
                self.skip_whitespace()

            # Skip comments
            elif ch == '#':
                self.skip_comment()

            # Newlines are significant (end of a statement)
            elif ch == '\n':
                self.tokens.append(Token(TT_NEWLINE, '\\n', self.line, self.col))
                self.advance()

            # Opening brace for REPEAT block
            elif ch == '{':
                self.tokens.append(Token(TT_LBRACE, '{', self.line, self.col))
                self.advance()

            # Closing brace for REPEAT block
            elif ch == '}':
                self.tokens.append(Token(TT_RBRACE, '}', self.line, self.col))
                self.advance()

            # Integer literals
            elif ch.isdigit():
                self.tokens.append(self.read_number())

            # Keywords and identifiers
            elif ch.isalpha() or ch == '_':
                self.tokens.append(self.read_word())

            # Carriage return (Windows line ending) - just skip
            elif ch == '\r':
                self.advance()

            else:
                self.error(f"Unexpected character: '{ch}'")

        # Always end with an EOF token
        self.tokens.append(Token(TT_EOF, None, self.line, self.col))
        return self.tokens

if __name__ == '__main__':
    sample = """
CANVAS 20 20
COLOR RED
DRAW RECT 2 2 5 5
COLOR BLUE
DRAW PIXEL 10 10
REPEAT 5 {
    DRAW PIXEL 3 3
}
"""
    lexer = Lexer(sample)
    tokens = lexer.tokenize()
    for tok in tokens:
        if tok.type != 'NEWLINE':   # skip newlines for cleaner output
            print(tok)