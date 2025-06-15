"""Test imports for the LangChain agent tests."""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Try to import the agent module
try:
    from app.services.langchain.agent import TravelAgent
    print("Successfully imported TravelAgent")
except ImportError as e:
    print(f"Failed to import TravelAgent: {e}")

# Try to import the test module
try:
    from tests.unit.services.langchain import test_agent
    print("Successfully imported test_agent"
    print(f"Test functions: {[f for f in dir(test_agent) if f.startswith('test_')]}")
except ImportError as e:
    print(f"Failed to import test_agent: {e}")

# Try to import pytest
try:
    import pytest
    print(f"Pytest version: {pytest.__version__}")
except ImportError as e:
    print(f"Failed to import pytest: {e}")
