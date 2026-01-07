#!/usr/bin/env python3
"""
Test runner script for the Telegram Finance Bot.

This script provides an easy way to run the test suite with proper environment setup.
"""

import subprocess
import sys
import os

def run_tests():
    """Run the pytest test suite."""
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    # Activate virtual environment and run tests
    cmd = [
        'bash', '-c',
        'source venv/bin/activate && python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing'
    ]

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    print("Running Telegram Finance Bot Tests...")
    print("=" * 50)

    success = run_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)