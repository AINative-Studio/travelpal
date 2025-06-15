"""Detailed test script to debug test execution."""
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
backend_path = os.path.abspath('.')
sys.path.insert(0, backend_path)
logger.info(f"Added to path: {backend_path}")

def main():
    logger.info("Starting test execution...")
    
    # Try to import the test module
    try:
        logger.info("Attempting to import test module...")
        from tests.unit.services.langchain import test_agent
        logger.info("Successfully imported test module")
        
        # List all test functions
        test_functions = [
            func for func in dir(test_agent) 
            if func.startswith('test_') and callable(getattr(test_agent, func))
        ]
        logger.info(f"Found test functions: {test_functions}")
        
        # Run each test function
        for func_name in test_functions:
            logger.info(f"Running test: {func_name}")
            try:
                func = getattr(test_agent, func_name)
                func()
                logger.info(f"Test {func_name} completed successfully")
            except Exception as e:
                logger.error(f"Test {func_name} failed: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to import or run tests: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
