import sys
from codegen.three_address_generator import *
from parser.parser import Parser
from codegen.constants import DEBUG

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    parser = Parser(input_file)
    initial_node, errors, program, semantic_errors = parser.parse()
    if len(semantic_errors) == 0:
        result_program = generate_code(program)
        semantic_errors = ["The input program is semantically correct."]
    else:
        result_program = "The output code has not been generated."
    with open("output.txt", "w", encoding="utf-8") as f:
        print(result_program, file=f)
    with open("semantic_errors.txt", "w", encoding="utf-8") as f:
        print("\n".join(semantic_errors), file=f)

    if DEBUG:
        with open("debug.txt", "w", encoding="utf-8") as f:
            for line in parser.codegen.line_map:
                ptoken = line[1][0]
                ntoken = line[1][1]
                if ptoken:
                    f.write(f"{line[0]} -> {ptoken.lexeme}, {ptoken.lineno}\n")
