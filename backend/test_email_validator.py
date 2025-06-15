import sys
import importlib.metadata

try:
    # Method 1: Using importlib.metadata (Python 3.8+)
    version = importlib.metadata.version('email-validator')
    print(f"Method 1 - importlib.metadata: {version}")
except Exception as e:
    print(f"Method 1 failed: {e}", file=sys.stderr)

try:
    # Method 2: Using pkg_resources
    import pkg_resources
    version = pkg_resources.get_distribution('email-validator').version
    print(f"Method 2 - pkg_resources: {version}")
except Exception as e:
    print(f"Method 2 failed: {e}", file=sys.stderr)

try:
    # Method 3: Direct import and check version
    import email_validator
    print(f"Method 3 - Direct import: {email_validator.__version__}")
except Exception as e:
    print(f"Method 3 failed: {e}", file=sys.stderr)
