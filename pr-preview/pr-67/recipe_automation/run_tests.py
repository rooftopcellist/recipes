#!/usr/bin/env python3
"""
Test runner script for the recipe automation.
"""

import os
import sys
import unittest
import importlib.util
import time

def load_tests_from_file(file_path):
    """Load tests from a file."""
    module_name = os.path.basename(file_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find all test functions in the module
    test_functions = []
    for name in dir(module):
        if name.startswith('test_'):
            test_functions.append(getattr(module, name))
    
    return test_functions

def run_tests():
    """Run all tests in the current directory."""
    # Find all test files
    test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.py')]
    test_files.sort()
    
    # Skip this file
    if 'run_tests.py' in test_files:
        test_files.remove('run_tests.py')
    
    # Run each test file
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_file in test_files:
        print(f"\n{'='*80}")
        print(f"Running tests from {test_file}...")
        print(f"{'='*80}")
        
        try:
            test_functions = load_tests_from_file(test_file)
            for test_function in test_functions:
                total_tests += 1
                print(f"\nRunning {test_function.__name__}...")
                start_time = time.time()
                try:
                    test_function()
                    end_time = time.time()
                    print(f"✅ {test_function.__name__} passed in {end_time - start_time:.2f} seconds")
                    passed_tests += 1
                except Exception as e:
                    end_time = time.time()
                    print(f"❌ {test_function.__name__} failed in {end_time - start_time:.2f} seconds: {e}")
                    failed_tests.append((test_file, test_function.__name__, str(e)))
        except Exception as e:
            print(f"❌ Failed to load tests from {test_file}: {e}")
            failed_tests.append((test_file, "load_tests", str(e)))
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"Test Summary: {passed_tests}/{total_tests} tests passed")
    print(f"{'='*80}")
    
    if failed_tests:
        print("\nFailed tests:")
        for test_file, test_name, error in failed_tests:
            print(f"❌ {test_file}:{test_name} - {error}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(run_tests())
