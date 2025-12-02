from .productions import *
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scanner'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'codegen'))
from scanner.scanner import Scanner
from codegen.codegen import CodeGen
from codegen.semantic_exception import SemanticException

previous_token = None
current_token = None
errors = []
semantic_errors = []
file_ended = False

class Token:
    def __init__(self, token_type, lexeme, lineno):
        self.token_type = token_type
        self.lexeme = lexeme
        self.lineno = lineno


class ParseNode:
    def __init__(self, production=Program, label="Program", parent=None):
        self.production = production
        self.label = label
        self.parent = parent
        self.children = []

    def add_child(self, child: "ParseNode"):
        child.parent = self
        self.children.append(child)

    def get_name(self):
        if type(self.production) == str:
            return self.production
        return self.production.name

def get_next_valid_token(scanner):
    token = scanner.get_next_token()
    if token is None:
        return Token(END_TOKEN, "$", scanner.line)
    
    token_type, token_value = token
    skip_states = PANIC_STATES + [WHITESPACE, COMMENT]
    while token_type in skip_states:
        token = scanner.get_next_token()
        if token is None:
            return Token(END_TOKEN, "$", scanner.line)
        token_type, token_value = token
    
    return Token(token_type, token_value, scanner.line)


class Parser:
    def __init__(self, input_file):
        self.scanner = Scanner(input_file)
        self.codegen = CodeGen()

    def parse(self):
        global current_token, previous_token, errors, file_ended, semantic_errors
        errors = []
        semantic_errors = []
        file_ended = False
        previous_token = current_token
        current_token = get_next_valid_token(self.scanner)
        root_parser = ProductionParser(Program, self.scanner, self.codegen)
        root = root_parser.parse()
        return root, errors, self.codegen.program, semantic_errors

class ProductionParser:
    def __init__(self, production, scanner, codegen):
        self.production = production
        self.scanner = scanner
        self.current_state = None
        self.codegen = codegen
        self.errors = []
        if type(production) == Production:
            self.current_state = parser_states_dict[production]

    def parse(self):
        global current_token, previous_token, errors, file_ended, semantic_errors
        if self.current_state is None:
            if current_token.token_type == END_TOKEN:
                node = ParseNode(self.production, self.production)
            else:
                node = ParseNode(f'({current_token.token_type}, {current_token.lexeme})',
                                 f'({current_token.token_type}, {current_token.lexeme})')
            previous_token = current_token
            current_token = get_next_valid_token(self.scanner)
            return node
        current_node = ParseNode(self.production, label=self.production.name)
        while not self.current_state.is_final:

            epsilon_state = None
            error_edge = None
            is_nonterminal_missing = False
            is_token_illegal = False
            is_NUM_or_ID_missing = False
            is_KEYWORD_or_SYMBOL_missing = False

            for edge in self.current_state.edges:
                is_in_first = False
                is_in_follow = False
                if edge.edge_type == PRODUCTION_PARSER_EDGE:
                    is_in_first = current_token.lexeme in edge.label.first or current_token.token_type in edge.label.first
                    is_in_follow = current_token.lexeme in edge.label.follow or current_token.token_type in edge.label.follow

                is_action_code = edge.edge_type == ACTION_PARSER_EDGE
                is_valid_NUM_or_ID = edge.edge_type == NUM_ID_PARSER_EDGE and current_token.token_type == edge.label
                is_valid_KEYWORD_or_SYMBOL = edge.edge_type == KEYWORD_SYMBOL_PARSER_EDGE and current_token.lexeme == edge.label
                is_valid_Nonterminal = edge.edge_type == PRODUCTION_PARSER_EDGE and is_in_first
                is_valid_epsilon_nonterminal = edge.edge_type == PRODUCTION_PARSER_EDGE and edge.label.first_has_epsilon and is_in_follow

                if is_action_code:
                    try:
                        self.codegen.act(edge.label, previous_token, current_token)
                    except SemanticException as e:
                        semantic_errors.append(str(e))
                    except:
                        pass
                    self.current_state = edge.destination
                    error_edge = None
                    break

                elif is_valid_NUM_or_ID or is_valid_KEYWORD_or_SYMBOL:
                    epsilon_state = None
                    next_node = ProductionParser(edge.label, self.scanner, self.codegen).parse()
                    current_node.add_child(next_node)
                    if file_ended:
                        return current_node
                    self.current_state = edge.destination
                    error_edge = None
                    break

                elif is_valid_Nonterminal or is_valid_epsilon_nonterminal:
                    epsilon_state = None
                    next_node = ProductionParser(edge.label, self.scanner, self.codegen).parse()
                    current_node.add_child(next_node)
                    if file_ended:
                        return current_node
                    self.current_state = edge.destination
                    error_edge = None
                    break

                elif edge.edge_type == EPSILON_PARSER_EDGE:
                    epsilon_state = edge.destination
                else:
                    is_nonterminal_missing = edge.edge_type == PRODUCTION_PARSER_EDGE and not is_in_first and is_in_follow
                    is_token_illegal = edge.edge_type == PRODUCTION_PARSER_EDGE and not is_in_first and not is_in_follow
                    is_NUM_or_ID_missing = edge.edge_type == NUM_ID_PARSER_EDGE and not current_token.token_type == edge.label
                    is_KEYWORD_or_SYMBOL_missing = edge.edge_type == KEYWORD_SYMBOL_PARSER_EDGE and not current_token.lexeme == edge.label
                    error_edge = edge

            if epsilon_state:
                next_node = ParseNode(EPSILON, EPSILON)
                current_node.add_child(next_node)
                if file_ended:
                    return current_node
                self.current_state = epsilon_state
            elif error_edge:
                try:
                    self.generate_panic(error_edge, is_KEYWORD_or_SYMBOL_missing, is_NUM_or_ID_missing,
                                        is_nonterminal_missing, is_token_illegal)
                except Exception as e:
                    should_continue = ProductionParser.handle_panic_error_message(e)
                    if should_continue:
                        continue
                    break

        return current_node

    @staticmethod
    def handle_panic_error_message(e: Exception) -> bool:
        global file_ended
        message = e.args[0]
        lexeme = e.args[1]
        token: Token = e.args[2]
        error_message = f"#{token.lineno} : syntax error, {message} {lexeme}"
        if token.lexeme == "$":
            message = "Unexpected EOF"
            error_message = f"#{token.lineno} : syntax error, {message}"
            file_ended = True
            errors.append(error_message)
            return False
        errors.append(error_message)
        return True

    def generate_panic(self, error_edge, is_KEYWORD_or_SYMBOL_missing, is_NUM_or_ID_missing, is_nonterminal_missing,
                       is_token_illegal):
        global current_token, previous_token
        if is_nonterminal_missing:
            self.current_state = error_edge.destination
            raise Exception("missing", error_edge.label.name, current_token)

        elif is_NUM_or_ID_missing or is_KEYWORD_or_SYMBOL_missing:
            self.current_state = error_edge.destination
            raise Exception("missing", error_edge.label, current_token)

        elif is_token_illegal:
            illegal_token = current_token
            previous_token = current_token
            current_token = get_next_valid_token(self.scanner)
            illegal_lexeme = illegal_token.lexeme
            if illegal_token.token_type in [ID, NUM]:
                illegal_lexeme = illegal_token.token_type
            raise Exception("illegal", illegal_lexeme, illegal_token)

def build_parse_tree_string(node, prefix="", is_last=True, is_root=False):
    """
    Build a formatted string representation of the parse tree.
    
    This function creates a visual representation of the parse tree using
    ASCII art with proper indentation and tree connectors. The output
    follows a standard tree format that clearly shows the hierarchical
    structure of the parsed program.
    
    The function uses recursive traversal to build the tree representation:
    - Root node appears at the top level
    - Child nodes are indented and connected with tree lines
    - Last children use "└──" connector, others use "├──"
    - Proper spacing maintains tree structure alignment
    
    Args:
        node (ParseNode): The current node to process
        prefix (str): Current indentation prefix for tree formatting
        is_last (bool): Whether this node is the last child of its parent
        is_root (bool): Whether this node is the root of the tree
        
    Returns:
        list: List of strings, each representing one line of the tree
        
    Example Output:
        Program
        └── Declaration-list
            ├── Declaration
            │   ├── Declaration-initial
            │   │   ├── Type-specifier
            │   │   │   └── (KEYWORD, int)
            │   │   └── (ID, main)
            │   └── Declaration-prime
            │       └── Fun-declaration-prime
            └── epsilon
    """
    if node is None:
        return []
    
    lines = []
    
    # Add current node with appropriate formatting
    if is_root:
        lines.append(node.get_name())
    else:
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + node.get_name())
    
    # Recursively add children with proper indentation
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        if is_root:
            child_lines = build_parse_tree_string(child, "", is_last_child, False)
        else:
            child_prefix = prefix + ("    " if is_last else "│   ")
            child_lines = build_parse_tree_string(child, child_prefix, is_last_child, False)
        lines.extend(child_lines)
    
    return lines

def main():
    """
    Main function that demonstrates the parser usage.
    
    This function provides a complete example of how to use the parser:
    1. Creates a Parser instance with an input file
    2. Parses the input and gets results
    3. Writes the parse tree to a file
    4. Writes syntax errors to a file
    5. Provides console feedback about the parsing results
    
    Output Files:
    - parse_tree.txt: Visual representation of the parse tree
    - syntax_errors.txt: List of syntax errors or success message
    
    The function handles both successful parsing (no errors) and
    error cases (syntax errors found), providing appropriate output
    in both scenarios.
    """
    input_file = '../scanner/input.txt'
    parser = Parser(input_file)
    
    # Parse the input file
    root, errors = parser.parse()
    
    # Write parse tree to file
    tree_lines = build_parse_tree_string(root, "", True, True)
    with open('parse_tree.txt', 'w', encoding='utf-8') as f:
        for line in tree_lines:
            f.write(line + '\n')
    
    # Write syntax errors to file
    with open('syntax_errors.txt', 'w', encoding='utf-8') as f:
        if errors:
            for error in errors:
                f.write(error + '\n')
        else:
            f.write("There is no syntax error.\n")
    
    print("Parsing complete. Output files generated:")
    print("- parse_tree.txt")
    print("- syntax_errors.txt")
    print(f"Total errors: {len(errors)}")

if __name__ == '__main__':
    main() 
