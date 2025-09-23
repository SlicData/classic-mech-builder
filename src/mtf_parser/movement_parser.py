#!/usr/bin/env python3
"""
Movement Parser - CMB-20 Step 1
Enhanced movement parsing with validation and error handling
"""

import re
import logging
from typing import Tuple

class MovementParser:
    """Parser for BattleMech movement values (Walk MP, Run MP, Jump MP)"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def parse_movement(self, content: str) -> Tuple[int, int, int]:
        """
        Parse all movement values from MTF content
        Returns (walk_mp, run_mp, jump_mp)
        """
        walk_mp = self._parse_walk_mp(content)
        run_mp = self._parse_run_mp(content, walk_mp)
        jump_mp = self._parse_jump_mp(content)
        
        return walk_mp, run_mp, jump_mp
    
    def _parse_walk_mp(self, content: str) -> int:
        """Parse walk MP with validation - all mechs should have walk MP > 0"""
        patterns = [
            r'^Walk\s*MP:\s*(\d+)',     # "Walk MP: 8" - primary MTF format
            r'walk\s*mp:\s*(\d+)',      # fallback for variations
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                walk_mp = int(match.group(1))
                if walk_mp > 0:
                    return walk_mp
                else:
                    self.logger.warning(f"Found walk MP = 0, which is invalid for functional mechs")
                    return walk_mp  # Return it anyway for debugging
        
        # If we get here, parsing failed completely
        self.logger.error(f"Failed to parse walk MP from MTF content")
        return 0
    
    def _parse_run_mp(self, content: str, walk_mp: int = None) -> int:
        """Parse run MP - calculate from walk if not explicit"""
        # Try explicit run MP first
        patterns = [
            r'^Run\s*MP:\s*(\d+)',
            r'run\s*mp:\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Calculate from walk MP (standard BattleTech rule: Run = Walk * 1.5)
        if walk_mp is None:
            walk_mp = self._parse_walk_mp(content)
        
        if walk_mp > 0:
            return int(walk_mp * 1.5)
        else:
            self.logger.error(f"Cannot calculate run MP: walk MP is {walk_mp}")
            return 0
    
    def _parse_jump_mp(self, content: str) -> int:
        """Parse jump MP - can legitimately be 0 for non-jump mechs"""
        patterns = [
            r'^Jump\s*MP:\s*(\d+)',     # "Jump MP: 6" - primary MTF format  
            r'jump\s*mp:\s*(\d+)',      # fallback for variations
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        self.logger.debug(f"No jump MP found, defaulting to 0")
        return 0
    
    def validate_movement(self, walk_mp: int, run_mp: int, jump_mp: int, 
                         chassis: str, model: str, file_name: str, content: str) -> bool:
        """Validate movement values and log debugging info if needed"""
        if walk_mp == 0:
            self.logger.error(f"Movement parsing failed for {chassis} {model}: walk_mp = 0")
            self.logger.debug(f"Dumping movement-related lines from {file_name}:")
            for line_num, line in enumerate(content.split('\n'), 1):
                if any(word in line.lower() for word in ['walk', 'jump', 'movement']):
                    self.logger.debug(f"  Line {line_num}: {line.strip()}")
            return False
        
        # Validate run MP calculation
        expected_run = int(walk_mp * 1.5)
        if run_mp != expected_run and run_mp != 0:
            self.logger.debug(f"Run MP {run_mp} doesn't match expected {expected_run} for {chassis} {model}")
        
        return True
