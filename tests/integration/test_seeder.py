#!/usr/bin/env python3
"""
Test the MTF seeder with dry run
"""

import sys
import os
import subprocess
from pathlib import Path

def test_parser():
    """Test the MTF parser with a single file"""
    # Change to the project directory
    os.chdir('/Users/justi/classic-mech-builder')
    
    # Run the seeder with dry-run on the test file
    cmd = [
        'python3', 'db/seeds/mtf_seeder.py',
        '--megamek-path', './data',
        '--limit', '1',
        '--dry-run'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

if __name__ == "__main__":
    success = test_parser()
    if success:
        print("✓ Test completed successfully")
    else:
        print("✗ Test failed")
