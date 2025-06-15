import sys
import importlib.metadata

def patch_pydantic_networks():
    """Patch pydantic.networks to fix email-validator version check"""
    import pydantic.networks
    
    def patched_import_email_validator():
        global email_validator
        try:
            import email_validator
            # Use importlib.metadata to check version
            version = importlib.metadata.version('email-validator')
            if not version.startswith('2.'):
                raise ImportError('email-validator version >= 2.0 required, run pip install -U email-validator')
        except ImportError as e:
            if 'email-validator' in str(e):
                raise ImportError('email-validator is not installed, run `pip install pydantic[email]`') from e
            raise
    
    # Apply the patch
    pydantic.networks.import_email_validator = patched_import_email_validator
    
    print("Successfully patched pydantic.networks.import_email_validator")

if __name__ == "__main__":
    patch_pydantic_networks()
