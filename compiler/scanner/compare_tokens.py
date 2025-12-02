import os
import re

def Check(manual_tokens_file, antlr_tokens_file, max_skip=3):
    def load_tokens(file_path):
        tokens = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if '.' in line and line[0].isdigit():
                    parts = line.split('. ', 1)
                    if len(parts) < 2:
                        continue
                    tokens_part = parts[1]
                    found_tokens = re.findall(r'\(([^,]+), ([^\)]+)\)', tokens_part)
                    tokens.extend([(t[0].strip(), t[1].strip()) for t in found_tokens])
                else:
                    if line.startswith('(') and line.endswith(')'):
                        content = line[1:-1]
                        if ',' in content:
                            t_type, t_text = content.split(',', 1)
                            tokens.append((t_type.strip(), t_text.strip()))
        return tokens

    def load_lexical_errors(file_path):
        errors = set()
        if not os.path.exists(file_path):
            print("[Warning] lexical_errors.txt not found.")
            return errors
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r'\(([^,]+),', line)
                if match:
                    errors.add(match.group(1).strip())
        return errors

    def token_full(t):
        return t  # Compare full (TYPE, VALUE) tuple

    manual_tokens = load_tokens(manual_tokens_file)
    antlr_tokens = load_tokens(antlr_tokens_file)

    errors_file = os.path.join(os.path.dirname(antlr_tokens_file), 'lexical_errors.txt')
    lexical_errors = load_lexical_errors(errors_file)
    antlr_tokens = [t for t in antlr_tokens if t[1] not in lexical_errors]

    print(f"Manual tokens loaded: {len(manual_tokens)}")
    print(f"ANTLR tokens loaded (after filtering): {len(antlr_tokens)}")
    print("-" * 60)

    i, j = 0, 0
    matches = 0
    mismatches = []

    while i < len(manual_tokens) and j < len(antlr_tokens):
        m_tok = manual_tokens[i]
        a_tok = antlr_tokens[j]

        if token_full(m_tok) == token_full(a_tok):
            print(f"[Match at {i},{j}] {m_tok}")
            matches += 1
            i += 1
            j += 1
            continue

        # Try lookahead to find near matches
        if i + 1 < len(manual_tokens) and token_full(manual_tokens[i + 1]) == token_full(a_tok):
            print(f"[Next match in manual, advancing 1] {a_tok}")
            i += 1
            continue
        if j + 1 < len(antlr_tokens) and token_full(antlr_tokens[j + 1]) == token_full(m_tok):
            print(f"[Next match in ANTLR, advancing 1] {m_tok}")
            j += 1
            continue

        # Wider lookahead up to max_skip
        found = False
        for skip in range(2, max_skip + 1):
            if i + skip < len(manual_tokens) and token_full(manual_tokens[i + skip]) == token_full(a_tok):
                print(f"[Skip in manual: skipping {skip} to match {a_tok}]")
                i += skip
                found = True
                break
            if j + skip < len(antlr_tokens) and token_full(antlr_tokens[j + skip]) == token_full(m_tok):
                print(f"[Skip in ANTLR: skipping {skip} to match {m_tok}]")
                j += skip
                found = True
                break

        if not found:
            mismatches.append((i, m_tok, a_tok))
            print(f"[Mismatch near {i},{j}] Manual: {m_tok} vs ANTLR: {a_tok}")
            i += 1
            j += 1

    total = len(manual_tokens)  # Use only manual tokens for similarity metric
    similarity = (matches / total) * 100 if total > 0 else 100.0

    print("-" * 60)
    print(f"Matched tokens: {matches} / {total}")
    print(f"Similarity: {similarity:.2f}%")

    return similarity
