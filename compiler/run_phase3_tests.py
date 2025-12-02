#!/usr/bin/env python3
"""
Script to run all Phase 3 test cases for the C-minus compiler.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_test_case(test_dir, test_name):
    """
    Run a single test case.
    
    Args:
        test_dir (str): Path to the test case directory
        test_name (str): Name of the test case (e.g., 'T1', 'T2')
    
    Returns:
        dict: Results of the test case
    """
    print(f"\n{'='*50}")
    print(f"Running {test_name}")
    print(f"{'='*50}")
    
    # Get the absolute paths
    test_path = Path(test_dir)
    input_file = test_path / "input.txt"
    expected_output = test_path / "output.txt"
    expected_semantic_errors = test_path / "semantic_errors.txt"
    
    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return {
            'test_name': test_name,
            'status': 'FAILED',
            'error': 'Input file not found'
        }
    
    # Copy input file to current directory
    shutil.copy(input_file, "input.txt")
    
    try:
        # Run the compiler
        print(f"Running compiler on {input_file}...")
        result = subprocess.run([sys.executable, "compiler.py"], 
                              capture_output=True, text=True, timeout=30)
        
        # Check if compilation was successful
        if result.returncode != 0:
            print(f"❌ Compiler failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return {
                'test_name': test_name,
                'status': 'FAILED',
                'error': f'Compiler failed with return code {result.returncode}'
            }
        
        # Read generated output files
        output_content = ""
        semantic_errors_content = ""
        
        if os.path.exists("output.txt"):
            with open("output.txt", "r", encoding="utf-8") as f:
                output_content = f.read()
        
        if os.path.exists("semantic_errors.txt"):
            with open("semantic_errors.txt", "r", encoding="utf-8") as f:
                semantic_errors_content = f.read()
        
        # Compare with expected results
        expected_output_content = ""
        expected_semantic_errors_content = ""
        
        if expected_output.exists():
            with open(expected_output, "r", encoding="utf-8") as f:
                expected_output_content = f.read()
        
        if expected_semantic_errors.exists():
            with open(expected_semantic_errors, "r", encoding="utf-8") as f:
                expected_semantic_errors_content = f.read()
        
        # Check if results match
        output_match = output_content.strip() == expected_output_content.strip()
        semantic_errors_match = semantic_errors_content.strip() == expected_semantic_errors_content.strip()
        
        if output_match and semantic_errors_match:
            print(f"✅ {test_name} PASSED")
            print(f"Output matches expected result")
            return {
                'test_name': test_name,
                'status': 'PASSED',
                'output_match': True,
                'semantic_errors_match': True
            }
        else:
            print(f"❌ {test_name} FAILED")
            if not output_match:
                print("Output mismatch:")
                print(f"Expected: {repr(expected_output_content)}")
                print(f"Got: {repr(output_content)}")
            if not semantic_errors_match:
                print("Semantic errors mismatch:")
                print(f"Expected: {repr(expected_semantic_errors_content)}")
                print(f"Got: {repr(semantic_errors_content)}")
            
            return {
                'test_name': test_name,
                'status': 'FAILED',
                'output_match': output_match,
                'semantic_errors_match': semantic_errors_match,
                'expected_output': expected_output_content,
                'actual_output': output_content,
                'expected_semantic_errors': expected_semantic_errors_content,
                'actual_semantic_errors': semantic_errors_content
            }
    
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} TIMEOUT")
        return {
            'test_name': test_name,
            'status': 'TIMEOUT',
            'error': 'Test case timed out'
        }
    except Exception as e:
        print(f"❌ {test_name} ERROR: {e}")
        return {
            'test_name': test_name,
            'status': 'ERROR',
            'error': str(e)
        }
    finally:
        # Clean up generated files
        for file in ["input.txt", "output.txt", "semantic_errors.txt", "debug.txt"]:
            if os.path.exists(file):
                os.remove(file)

def main():
    """Run all Phase 3 test cases."""
    # Get the path to Phase 3 test cases
    phase3_dir = Path("../Test cases/Phase 3")
    
    if not phase3_dir.exists():
        print(f"❌ Phase 3 directory not found: {phase3_dir}")
        return
    
    # Get all test case directories
    test_dirs = [d for d in phase3_dir.iterdir() if d.is_dir() and d.name.startswith('T')]
    test_dirs.sort(key=lambda x: int(x.name[1:]))  # Sort by test number
    
    print(f"Found {len(test_dirs)} test cases in Phase 3")
    
    results = []
    passed = 0
    failed = 0
    
    for test_dir in test_dirs:
        test_name = test_dir.name
        result = run_test_case(test_dir, test_name)
        results.append(result)
        
        if result['status'] == 'PASSED':
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(results)*100:.1f}%")
    
    # Print failed tests
    if failed > 0:
        print(f"\nFailed tests:")
        for result in results:
            if result['status'] != 'PASSED':
                print(f"  - {result['test_name']}: {result['status']}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")

if __name__ == "__main__":
    main() 