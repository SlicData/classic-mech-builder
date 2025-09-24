#!/usr/bin/env python3
"""Quick cleanup of remaining files"""

import shutil
from pathlib import Path

base = Path('/Users/justi/classic-mech-builder')

# Move remaining test/dev files to temp
temp_files = [
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
    'test_runner.py',
    'test_seeder.py',
    'test_step1_fix.py'
]

for file in temp_files:
    src = base / file
    dst = base / 'temp' / file
    if src.exists():
        print(f"Moving {file} to temp/")
        shutil.move(str(src), str(dst))

print("Cleanup complete!")
