#!/usr/bin/env python3

import os
import sys
from parser import Parser, build_parse_tree_string

def test_case(test_num):
    """Test a specific test case and compare with expected output."""
    test_dir = f'/Users/saeed/Desktop/C-minus-Compiler/Test cases/Phase 2/T{test_num}'
    input_file = os.path.join(test_dir, 'input.txt')
    expected_errors_file = os.path.join(test_dir, 'syntax_errors.txt')
    expected_tree_file = os.path.join(test_dir, 'parse_tree.txt')
    
    if not os.path.exists(input_file):
        print(f"T{test_num}: Input file not found")
        return
    
    # Parse the input
    parser = Parser(input_file)
    root, errors = parser.parse()
    
    with open(f'syntax_errors_{test_num}.txt', 'w', encoding='utf-8') as f:
        if errors:
            for error in errors:
                f.write(error + '\n')
        else:
            f.write("There is no syntax error.\n")
    
    tree_lines = build_parse_tree_string(root, "", True, True)
    with open(f'parse_tree_{test_num}.txt', 'w', encoding='utf-8') as f:
        for line in tree_lines:
            f.write(line + '\n')
    
    
    # Count errors
    error_count = len(errors)
    
    # Read expected error count
    expected_error_count = 0
    if os.path.exists(expected_errors_file):
        with open(expected_errors_file, 'r') as f:
            content = f.read().strip()
            if content != "There is no syntax error.":
                expected_error_count = len([line for line in content.split('\n') if line.strip()])
    
    # Print results
    print(f"T{test_num}: {error_count} errors (expected {expected_error_count})")
    
    if error_count == expected_error_count:
        print(f"  ✅ Error count matches!")
    else:
        print(f"  ❌ Error count mismatch")
    
    return error_count == expected_error_count

def main():
    print("Testing parser on all test cases...")
    print("=" * 50)
    
    all_passed = True
    for i in range(1, 6):
        passed = test_case(i)
        all_passed = all_passed and passed
        print()
    
    if all_passed:
        print("🎉 All test cases passed!")
    else:
        print("❌ Some test cases failed")

if __name__ == '__main__':
    main() 