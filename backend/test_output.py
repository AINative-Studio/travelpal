"""Test script to verify output handling."""
import sys

def main():
    print("This is a test message to stdout")
    print("This is another test message to stdout", file=sys.stdout)
    print("This is a test message to stderr", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
