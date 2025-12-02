from antlr4.tree.Tree import TerminalNode

def print_tree(tree, parser, indent=0):
    """Print a detailed parse tree with proper formatting"""
    spaces = "  " * indent
    
    if isinstance(tree, TerminalNode):
        # Terminal node (token)
        token = tree.getSymbol()
        token_name = parser.symbolicNames[token.type] if token.type < len(parser.symbolicNames) else f"TOKEN_{token.type}"
        return f"{spaces}{token_name}: '{token.text}'"
    else:
        # Non-terminal node (rule)
        rule_name = parser.ruleNames[tree.getRuleIndex()]
        result = f"{spaces}{rule_name}"
        
        # Add children
        children = []
        for i in range(tree.getChildCount()):
            child_str = print_tree(tree.getChild(i), parser, indent + 1)
            children.append(child_str)
        
        if children:
            result += "\n" + "\n".join(children)
        
        return result

def save_detailed_tree(tree, parser, filename):
    """Save a detailed parse tree to file"""
    tree_str = print_tree(tree, parser)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(tree_str)
    return tree_str 