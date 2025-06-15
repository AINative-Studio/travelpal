"""Script to check test setup and imports."""
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Try to import necessary modules
try:
    import pytest
    print("pytest version:", pytest.__version__)
except ImportError as e:
    print("Error importing pytest:", e)

try:
    from app.services.langchain.agent import TravelAgent, LANGCHAIN_AVAILABLE
    print("Successfully imported TravelAgent")
    print(f"LangChain available: {LANGCHAIN_AVAILABLE}")
except ImportError as e:
    print("Error importing TravelAgent:", e)

# Try to discover and run tests
if __name__ == "__main__":
    print("\nRunning test discovery...")
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    if os.path.exists(test_dir):
        print(f"Test directory exists: {test_dir}")
        
        # Try to list test files
        for root, dirs, files in os.walk(test_dir):
            print(f"\nFound test directory: {root}")
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    print(f"  - {file}")
    else:
        print(f"Test directory not found: {test_dir}")
