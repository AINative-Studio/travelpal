#!/usr/bin/env python3
"""
Run tests with patched pydantic.networks to fix email-validator version check.
"""
import sys
import os
import logging
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Apply the patch before importing anything that might use pydantic.networks
import importlib.metadata

def patch_pydantic_networks():
    """Patch pydantic.networks to fix email-validator version check and validation"""
    import pydantic.networks
    import email_validator
    
    # Store the original function
    original_import_email_validator = pydantic.networks.import_email_validator
    
    def patched_import_email_validator():
        try:
            # Return the actual email_validator module
            return email_validator
        except ImportError as e:
            if 'email-validator' in str(e):
                raise ImportError('email-validator is not installed, run `pip install pydantic[email]`') from e
            raise
    
    # Patch the function to return our module
    pydantic.networks.import_email_validator = patched_import_email_validator
    
    # Also patch the validate_email function to ensure it uses our module
    original_validate_email = pydantic.networks.validate_email
    
    def patched_validate_email(*args, **kwargs):
        try:
            return original_validate_email(*args, **kwargs)
        except AttributeError as e:
            if 'NoneType' in str(e) and 'validate_email' in str(e):
                # If we get here, the email_validator module wasn't properly imported
                # Try to import it directly
                import email_validator
                # Update the global email_validator in pydantic.networks
                pydantic.networks.email_validator = email_validator
                # Try again
                return original_validate_email(*args, **kwargs)
            raise
    
    pydantic.networks.validate_email = patched_validate_email
    logger.info("Successfully patched pydantic.networks email validation")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Apply the patch
patch_pydantic_networks()

# Now import the test module
from test_init import test_init

if __name__ == "__main__":
    logger.info("Starting tests with patched pydantic.networks...")
    asyncio.run(test_init())
