"""Run the LangChain agent tests directly using pytest."""
import sys
import os
import pytest

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

if __name__ == '__main__':
    # Run the tests with verbose output and show print statements
    test_path = 'tests/unit/services/langchain/test_agent.py'
    sys.exit(pytest.main([test_path, '-v', '-s', '--tb=short']))
