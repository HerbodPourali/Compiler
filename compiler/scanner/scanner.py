import re
from .tokens_definitions import KEYWORDS, SYMBOLS

class Scanner:
    def __init__(self, input_filename):
        self.input_filename = input_filename
        self.file = open(input_filename, 'r', encoding='utf-8')
        self.line = 1
        self.column = 0
        self.current_char = ''
        self.buffer = ''
        self.symbol_table = {kw: i+1 for i, kw in enumerate(KEYWORDS)}
        self.lexical_errors = []
        self.end_of_file = False
        self.eof_token_sent = False
        
        self._read_char()

    def _read_char(self):
        """Read next character from file and update line and column."""
        prev_char = self.current_char
        self.current_char = self.file.read(1)
        if self.current_char == '':
            self.end_of_file = True
        else:
            if prev_char == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1

    def _peek_char(self):
        """Peek one character ahead without advancing."""
        pos = self.file.tell()
        ch = self.file.read(1)
        self.file.seek(pos)
        return ch

    def _add_to_symbol_table(self, token_str):
        if token_str not in self.symbol_table:
            self.symbol_table[token_str] = max(self.symbol_table.values(), default=0) + 1

    def get_next_token(self):
        """Return next token as (TokenType, TokenString)."""
        # Return $ token at EOF
        if self.end_of_file and not self.eof_token_sent:
            self.eof_token_sent = True
            return ("$", "$")
        elif self.eof_token_sent:
            return None
            
        # Skip whitespace and advance to next non-whitespace character
        while not self.end_of_file and self.current_char in (' ', '\t', '\n', '\r', '\v', '\f'):
            self._read_char()
        
        # If we reached EOF after skipping whitespace, return $ token
        if self.end_of_file:
            if not self.eof_token_sent:
                self.eof_token_sent = True
                return ("$", "$")
            return None
        
        # Handle comments /* ... */
        if self.current_char == '/':
            next_ch = self._peek_char()
            if next_ch == '*':
                self._read_char()  # consume '/'
                self._read_char()  # consume '*'
                if not self._consume_comment():
                    return None
                # After comment, recursively get next token
                return self.get_next_token()

        # NUM token
        if self.current_char.isdigit():
            return self._number()

        # ID or KEYWORD
        if self.current_char.isalpha():
            return self._identifier_or_keyword()

        # SYMBOL token
        if self.current_char in ''.join(SYMBOLS):
            return self._symbol_or_error()

        # Invalid character - skip it and get next token
        invalid_char = self.current_char
        self._read_char()
        self._report_error(invalid_char, "Invalid input")
        return self.get_next_token()

    def _consume_comment(self):
        start_line = self.line  # record line where comment starts
        comment_content = '/*'  # include opening symbols

        while not self.end_of_file:
            self._read_char()  # move forward first
            ch = self.current_char
            comment_content += ch if ch else ''

            if ch == '*':
                next_ch = self._peek_char()
                if next_ch == '/':
                    self._read_char()  # consume '*'
                    self._read_char()  # consume '/'
                    return True  # comment closed

        # EOF reached, unclosed comment
        preview_len = 7
        preview = (comment_content[:preview_len - 1] + '...') if len(comment_content) > preview_len else comment_content

        self._report_error(preview, "Unclosed comment", line=start_line)
        return False

    def _number(self):
        num_str = ''

        # Read all digits first
        while not self.end_of_file and self.current_char.isdigit():
            num_str += self.current_char
            self._read_char()

        # If next character is a letter, start collecting the rest of the invalid number
        if not self.end_of_file and self.current_char.isalpha():
            # Consume all alphanumerics to complete the invalid token
            while not self.end_of_file and self.current_char.isalnum():
                num_str += self.current_char
                self._read_char()
            self._report_error(num_str, "Invalid number")
            self._read_char()  # Advance after error
            return None

        token = ("NUM", num_str)
        # Advance to next character for next token if not already at EOF
        if not self.end_of_file:
            # Only advance if not already advanced by the loop
            pass
        return token

    def _identifier_or_keyword(self):
        id_str = ''

        # Start with a letter
        if not self.current_char.isalpha():
            return None

        while not self.end_of_file:
            ch = self.current_char
            if ch.isalnum():
                id_str += ch
                self._read_char()
            elif ch in SYMBOLS or ch.isspace():
                # Valid end of identifier
                break
            else:
                # Stop current ID, then handle invalid character separately
                if id_str:
                    self._add_to_symbol_table(id_str)
                    token = ("ID", id_str)
                else:
                    token = None

                invalid_char = self.current_char
                self._read_char()
                self._report_error(invalid_char, "Invalid input")

                self._read_char()  # Advance after error
                return token
        if id_str in KEYWORDS:
            token = ("KEYWORD", id_str)
        else:
            self._add_to_symbol_table(id_str)
            token = ("ID", id_str)
        # Advance to next character for next token if not already at EOF
        if not self.end_of_file:
            pass
        return token

    def _symbol_or_error(self):
        ch = self.current_char
        # Handle '==' lookahead
        if ch == '=':
            next_ch = self._peek_char()
            if next_ch == '=':
                self._read_char()
                self._read_char()
                return ("SYMBOL", "==")
            else:
                self._read_char()  # just consume '='
                return ("SYMBOL", "=")

        else:
            if ch == '*':
                next_ch = self._peek_char()
                if next_ch == '/':
                    self._report_error("*/", "Unmatched comment")
                    self._read_char()
                    self._read_char()
                    return None

            if ch in SYMBOLS:
                self._read_char()
                return ("SYMBOL", ch)

            # Unexpected character
            self._report_error(ch, "Invalid input")
            self._read_char()
            self._read_char()  # Advance after error
            return None

    def _report_error(self, string, message, line=None):
        error_line = line if line is not None else self.line
        error_msg = f"Line {error_line}: ({string}, {message})"
        self.lexical_errors.append(error_msg)

    def close(self):
        self.file.close()
