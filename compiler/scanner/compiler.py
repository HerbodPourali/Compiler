from scanner import Scanner
from compare_tokens import Check


def main():
    input_file = 'compiler3/scanner/input.txt'
    scanner = Scanner(input_file)

    tokens_by_line = {}

    while not scanner.end_of_file:
        token = scanner.get_next_token()
        
        if token is None:
            # Error encountered, skip but don't stop
            continue
        
        token_type, token_str = token
        line_num = scanner.line

        if line_num not in tokens_by_line:
            tokens_by_line[line_num] = []
        
        tokens_by_line[line_num].append((token_type, token_str))


    # Write tokens.txt
    with open('tokens.txt', 'w', encoding='utf-8') as f:
        for line_num in sorted(tokens_by_line.keys()):
            tokens = tokens_by_line[line_num]
            token_strs = ' '.join(f'({t[0]}, {t[1]})' for t in tokens)
            f.write(f"{line_num}. {token_strs}\n")

    # Write lexical_errors.txt
    with open('lexical_errors.txt', 'w', encoding='utf-8') as f:
        if scanner.lexical_errors:
            for err in scanner.lexical_errors:
                f.write(err + '\n')
        else:
            f.write("There is no lexical error.\n")

    with open('symbol_table.txt', 'w', encoding='utf-8') as f:
        # Sort by stored index value
        for symbol, idx in sorted(scanner.symbol_table.items(), key=lambda item: item[1]):
            f.write(f"{idx}. {symbol}\n")
    
    scanner.close()
    print("Scanning complete. Output files generated.")
 
if __name__ == '__main__':
    main()

    check = False
    if check == True:
        manual_tokens_file = 'tokens.txt'
        antlr_tokens_file = 'ANTLR_p1.txt'
        
        similarity = Check(manual_tokens_file, antlr_tokens_file)
        print(f"Tokens similarity percentage: {similarity:.2f}%")
