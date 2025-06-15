#!/usr/bin/env python3
"""
Patch Pydantic's email validator to work around import issues.
"""
import sys
import importlib

# Import the email_validator module first
import email_validator

# Now patch pydantic.networks
import pydantic.networks

# Store the original function
original_import_email_validator = pydantic.networks.import_email_validator

def patched_import_email_validator():
    """Return the email_validator module directly"""
    return email_validator

# Apply the patch
pydantic.networks.import_email_validator = patched_import_email_validator

# Also set the email_validator module directly
pydantic.networks.email_validator = email_validator

# Now patch the validate_email function
original_validate_email = pydantic.networks.validate_email

def patched_validate_email(*args, **kwargs):
    """Patched version of validate_email that ensures email_validator is available"""
    # Make sure email_validator is set
    if not hasattr(pydantic.networks, 'email_validator') or pydantic.networks.email_validator is None:
        pydantic.networks.email_validator = email_validator
    return original_validate_email(*args, **kwargs)

pydantic.networks.validate_email = patched_validate_email

print("Successfully patched pydantic.networks email validation")

# Now import and run the test script
if __name__ == "__main__":
    # Import the test module after patching
    from test_init import test_init
    import asyncio
    
    print("Running tests with patched email validation...")
    asyncio.run(test_init())
