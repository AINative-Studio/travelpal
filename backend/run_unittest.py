"""Run tests using Python's unittest module."""
import unittest
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the test module
from tests.unit.services.langchain import test_agent

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases from the test module
    for test_case in unittest.defaultTestLoader.loadTestsFromModule(test_agent):
        test_suite.addTest(test_case)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
