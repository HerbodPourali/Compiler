# C-minus Compiler

A complete **single-pass compiler** for the C-minus language, implemented in **Python**, consisting of:

- **Phase 1:** Lexical Analysis (Scanner)  
- **Phase 2:** Parser  
- **Phase 3:** Intermediate Code Generation  

This compiler follows the official three-phase project specification for the C-minus language and produces output compatible with the provided Tester tool.

---

## Project Overview

This compiler performs all steps of a classical compiler front-end:

1. **Scanning**  
   Reads source code character-by-character and produces a stream of tokens.

2. **Parsing**  
   Uses a deterministic **state-machine LL(1)-compatible parser** to validate syntax and build a parse tree.

3. **Semantic Analysis + TAC Generation**  
   Performs type checking, scope validation, argument checking, and generates **Three-Address Code (TAC)** in a single pass.

The compiler is fully integrated: the parser triggers semantic actions during parsing, producing TAC.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
