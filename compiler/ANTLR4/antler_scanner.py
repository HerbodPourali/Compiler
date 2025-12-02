from antlr4 import FileStream, CommonTokenStream, InputStream
from CMinusLexer import CMinusLexer
from CMinusParser import CMinusParser
from CMinusListener import CMinusListener
from antlr_error_listener import CMinusErrorListener
from tree_printer import save_detailed_tree

def run_antlr_lexer(input_path, output_path):
    """Run the lexer and output tokens"""
    # Load input file
    input_stream = FileStream(input_path, encoding='utf-8')

    # Create lexer instance
    lexer = CMinusLexer(input_stream)

    # Get all tokens
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()

    with open(output_path, 'w', encoding='utf-8') as out_file:
        for token in token_stream.tokens:
            # Skip EOF token
            if token.type == -1:
                continue
            token_name = lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else f"UNKNOWN_{token.type}"
            token_text = token.text
            out_file.write(f"({token_name}, {token_text})\n")

def run_antlr_parser(input_path, parse_tree_output=None, errors_output=None):
    """Run the complete parser and return results"""
    try:
        # Load input file
        input_stream = FileStream(input_path, encoding='utf-8')
        
        # Create lexer
        lexer = CMinusLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        
        # Create parser
        parser = CMinusParser(token_stream)
        
        # Add custom error listener
        error_listener = CMinusErrorListener()
        parser.removeErrorListeners()  # Remove default error listeners
        parser.addErrorListener(error_listener)
        
        # Parse starting from program rule
        tree = parser.program()
        
        # Get errors from our custom listener
        errors = error_listener.get_errors()
        error_count = len(errors)
        
        # Write detailed parse tree if requested
        if parse_tree_output:
            save_detailed_tree(tree, parser, parse_tree_output)
        
        # Write errors if requested  
        if errors_output:
            with open(errors_output, 'w', encoding='utf-8') as f:
                if error_count == 0:
                    f.write("No syntax errors found.\n")
                else:
                    f.write(f"Total syntax errors: {error_count}\n\n")
                    for i, error in enumerate(errors, 1):
                        f.write(f"Error #{error['line']}: {error['message']}\n")
        
        return error_count, tree
        
    except Exception as e:
        print(f"Error during parsing: {e}")
        return -1, None

if __name__ == '__main__':
    input_file = '../../Test cases/Phase 2/T2/input.txt'
    
    # Test lexer
    print("Testing lexer...")
    run_antlr_lexer(input_file, 'ANTLR_tokens.txt')
    print("Tokens written to ANTLR_tokens.txt")
    
    # Test parser
    print("Testing parser...")
    error_count, tree = run_antlr_parser(input_file, 'ANTLR_parse_tree.txt', 'ANTLR_errors.txt')
    print(f"Parser completed with {error_count} errors")
    print("Detailed parse tree written to ANTLR_parse_tree.txt")
    print("Errors written to ANTLR_errors.txt")
