#!/usr/bin/env python3
"""
Cleanup script to reorganize classic-mech-builder directory
"""

import shutil
import os
from pathlib import Path

# Base directory
base_dir = Path('/Users/justi/classic-mech-builder')

# Test files to move
test_files = [
    'fix_insert_method.py', 
    'movement_parsing_fix.py',
    'seeder_helper_methods.py',
    'simple_movement_test.py',
    'simple_mtf_test.py',
    'step1_final_fix.py',
    'step1_movement_fix.py',
    'step2_weapon_parsing.py',
    'test_complete.py',
    'test_complete_seeder.py',
    'test_enhanced_parsing.py',
    'test_movement_parsing.py',
    'test_parser.py',
    'test_queries.sql',
    'test_runner.py',
    'test_seeder.py',
    'test_step1_fix.py',
    'test_steps_1_2.py'
]

def cleanup_directory():
    """Move files to appropriate subdirectories"""
    
    print("=== Cleaning up classic-mech-builder directory ===")
    
    # Move test files
    tests_dir = base_dir / 'tests'
    for file_name in test_files:
        src = base_dir / file_name
        dst = tests_dir / file_name
        
        if src.exists():
            print(f"Moving {file_name} -> tests/")
            shutil.move(str(src), str(dst))
        else:
            print(f"⚠️  {file_name} not found")
    
    print("\n=== Directory cleanup complete ===")
    print("New structure:")
    print("├── src/        # Main application code")
    print("├── tests/      # All test files")  
    print("├── scripts/    # Utility scripts")
    print("├── docs/       # Documentation")
    print("├── data/       # MegaMek data")
    print("├── db/         # Database migrations and seeds")
    print("└── temp/       # Temporary development files")

if __name__ == "__main__":
    cleanup_directory()
