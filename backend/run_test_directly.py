"""Run the test directly without using pytest."""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the test functions
from tests.unit.services.langchain.test_agent import (
    test_travel_agent_initialization,
    test_process_message_empty_input,
    test_process_message_valid_input,
    test_process_message_exception_handling,
    test_singleton_instance
)

def run_tests():
    """Run all test functions and report results."""
    tests = [
        ("test_travel_agent_initialization", test_travel_agent_initialization),
        ("test_process_message_empty_input", test_process_message_empty_input),
        ("test_process_message_valid_input", test_process_message_valid_input),
        ("test_process_message_exception_handling", test_process_message_exception_handling),
        ("test_singleton_instance", test_singleton_instance),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"Running {name}...")
        try:
            test_func()
            print(f"  ✅ {name} passed")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\nTest results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(run_tests())
