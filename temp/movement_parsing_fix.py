#!/usr/bin/env python3
"""
Movement Parsing Fix for MTF Parser - CMB-20 Step 1
Fixed patterns to correctly parse Walk MP, Run MP, and Jump MP from MTF files
"""

import re
from pathlib import Path
from typing import Tuple

class MovementParserFix:
    """Enhanced movement parsing with robust pattern matching"""
    
    def __init__(self):
        pass
    
    def parse_movement_comprehensive(self, content: str) -> Tuple[int, int, int]:
        """
        Enhanced movement parsing with multiple pattern support.
        Returns (walk_mp, run_mp, jump_mp)
        """
        walk_mp = run_mp = jump_mp = 0
        
        # Pattern 1: Individual MP lines (most common in MTF files)
        walk_patterns = [
            r'^Walk\s*MP:\s*(\d+)',           # "Walk MP: 8" - primary MTF format
            r'^Walk:\s*(\d+)',                # "Walk: 8" - alternative format
            r'walk\s*mp:\s*(\d+)',            # Original fallback (case insensitive)
        ]
        
        for pattern in walk_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                walk_mp = int(match.group(1))
                break
        
        jump_patterns = [
            r'^Jump\s*MP:\s*(\d+)',           # "Jump MP: 6" - primary MTF format
            r'^Jump:\s*(\d+)',                # "Jump: 6" - alternative format
            r'jump\s*mp:\s*(\d+)',            # Original fallback
        ]
        
        for pattern in jump_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                jump_mp = int(match.group(1))
                break
        
        # Pattern 2: Combined movement line (less common but should support)
        movement_patterns = [
            r'Movement:\s*Walk(?:\s*MP)?:\s*(\d+),\s*Run(?:\s*MP)?:\s*(\d+)(?:,\s*Jump(?:\s*MP)?:\s*(\d+))?',
            r'Walk\s*MP:\s*(\d+).*?Run\s*MP:\s*(\d+).*?(?:Jump\s*MP:\s*(\d+))?',
        ]
        
        for pattern in movement_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if match:
                walk_mp = int(match.group(1)) if match.group(1) else walk_mp
                run_mp = int(match.group(2)) if match.group(2) else run_mp
                if match.group(3):
                    jump_mp = int(match.group(3))
                break
        
        # Calculate run_mp if not found but walk_mp exists (standard BattleTech rules)
        if walk_mp > 0 and run_mp == 0:
            run_mp = int(walk_mp * 1.5)
        
        return walk_mp, run_mp, jump_mp

def test_movement_parsing_fix():
    """Test the movement parsing fix against sample MTF content"""
    
    print("=== Movement Parsing Fix Test ===")
    
    # Test cases with different MTF formats
    test_cases = [
        ("Locust Format", """
chassis:Locust
model:LCT-1V

Mass:20
Engine:160 Fusion Engine
Heat Sinks:10 Single
Walk MP:8
Jump MP:0
"""),
        ("Phoenix Hawk Format", """
chassis:Phoenix Hawk
model:PXH-1

Mass:45
Engine:270 Fusion Engine
Heat Sinks:10 Single
Walk MP:6
Jump MP:6
"""),
        ("King Crab Format", """
chassis:King Crab
model:KGC-0000

Mass:100
Engine:300 Fusion Engine
Heat Sinks:15 Single
Walk MP:3
Jump MP:0
"""),
        ("Combined Format", """
chassis:Test Mech
model:TEST-1

Movement: Walk MP: 4, Run MP: 6, Jump MP: 4
"""),
        ("Alternative Format", """
chassis:Alt Mech
model:ALT-1

Walk: 5
Jump: 3
""")
    ]
    
    parser = MovementParserFix()
    
    for name, content in test_cases:
        print(f"\n{name}:")
        print("  Input lines:")
        for line in content.split('\n'):
            if any(word in line.lower() for word in ['walk', 'jump', 'movement']):
                print(f"    {line.strip()}")
        
        walk, run, jump = parser.parse_movement_comprehensive(content)
        print(f"  Parsed: Walk={walk}, Run={run}, Jump={jump}")
        
        # Validate results
        expected_run = int(walk * 1.5) if walk > 0 else 0
        if run != expected_run and run == 0:
            print(f"  Note: Run MP calculated as {expected_run} (Walk * 1.5)")

# Now create the actual fix by updating the MTF parser methods
def create_updated_parser_methods():
    """Generate the updated parser methods to replace the broken ones"""
    
    print("\n=== Updated Parser Methods ===")
    print("Replace these methods in MTFParser class:")
    
    updated_methods = '''
    def _parse_walk_mp(self, content: str) -> int:
        """Fixed walk MP parsing with multiple patterns"""
        walk_patterns = [
            r'^Walk\\s*MP:\\s*(\\d+)',           # "Walk MP: 8" - primary MTF format
            r'^Walk:\\s*(\\d+)',                # "Walk: 8" - alternative format
            r'walk\\s*mp:\\s*(\\d+)',            # Original fallback (case insensitive)
        ]
        
        for pattern in walk_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0
    
    def _parse_run_mp(self, content: str) -> int:
        """Fixed run MP parsing - calculate from walk if not explicit"""
        # First try to find explicit run MP
        run_patterns = [
            r'^Run\\s*MP:\\s*(\\d+)',
            r'^Run:\\s*(\\d+)',
            r'run\\s*mp:\\s*(\\d+)',
        ]
        
        for pattern in run_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Calculate from walk MP if not found (standard BattleTech rule)
        walk_mp = self._parse_walk_mp(content)
        return int(walk_mp * 1.5) if walk_mp > 0 else 0
    
    def _parse_jump_mp(self, content: str) -> int:
        """Fixed jump MP parsing with multiple patterns"""
        jump_patterns = [
            r'^Jump\\s*MP:\\s*(\\d+)',           # "Jump MP: 6" - primary MTF format
            r'^Jump:\\s*(\\d+)',                # "Jump: 6" - alternative format
            r'jump\\s*mp:\\s*(\\d+)',            # Original fallback
        ]
        
        for pattern in jump_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0
'''
    
    print(updated_methods)

if __name__ == "__main__":
    test_movement_parsing_fix()
    create_updated_parser_methods()
