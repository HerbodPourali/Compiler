from antlr4.error.ErrorListener import ErrorListener

class CMinusErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_msg = f"Syntax Error at line {line}:{column} - {msg}"
        self.errors.append({
            'line': line,
            'column': column,
            'message': msg,
            'symbol': offendingSymbol.text if offendingSymbol else 'EOF'
        })
        print(error_msg)
    
    def get_errors(self):
        return self.errors
    
    def get_error_count(self):
        return len(self.errors) 