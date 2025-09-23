#!/usr/bin/env python3
"""
CMB-20 Step 1: Fix Movement Parsing with Error Handling
Updated movement parsing methods with validation
"""

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

def _parse_run_mp(self, content: str) -> int:
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
    walk_mp = self._parse_walk_mp(content)
    if walk_mp > 0:
        return int(walk_mp * 1.5)
    else:
        self.logger.error(f"Cannot calculate run MP: walk MP is {walk_mp}")
        return 0

# Also update the main parsing method to validate movement
def parse_mtf_file(self, file_path: Path) -> Optional[MechData]:
    """Parse MTF file with movement validation"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        chassis_model = self._extract_chassis_model(content)
        if not chassis_model:
            return None
        chassis, model = chassis_model
        
        # Parse movement with validation
        walk_mp = self._parse_walk_mp(content)
        run_mp = self._parse_run_mp(content)
        jump_mp = self._parse_jump_mp(content)
        
        # Validate movement - all functional mechs should have walk MP > 0
        if walk_mp == 0:
            self.logger.error(f"Movement parsing failed for {chassis} {model}: walk_mp = 0")
            self.logger.debug(f"Dumping movement-related lines from {file_path.name}:")
            for line_num, line in enumerate(content.split('\n'), 1):
                if any(word in line.lower() for word in ['walk', 'jump', 'movement']):
                    self.logger.debug(f"  Line {line_num}: {line.strip()}")
            # Continue parsing but mark as problematic
        
        return MechData(
            chassis=chassis, model=model,
            tech_base=self._parse_tech_base(content),
            era=self._parse_era(content),
            rules_level=self._parse_rules_level(content),
            tonnage=self._parse_tonnage(content),
            battle_value=self._calculate_battle_value(content),
            walk_mp=walk_mp,
            run_mp=run_mp,
            jump_mp=jump_mp,
            engine_type=self._parse_engine_type(content),
            engine_rating=self._parse_engine_rating(content),
            heat_sinks=self._parse_heat_sinks(content),
            armor_type=self._parse_armor_type(content),
            role=self._parse_role(content),
            year=self._parse_year(content),
            source=self._parse_source(content),
            cost_cbill=self._parse_cost(content),
            weapons=self._parse_weapons(content),
            armor=self._parse_armor_values(content),
            equipment=self._parse_equipment(content),
            crit_slots=self._parse_crit_slots(content),
            quirks=self._parse_quirks(content)
        )
    except Exception as e:
        self.logger.error(f"Error parsing {file_path}: {e}")
        return None

print("""
=== CMB-20 Step 1: Movement Parsing Fix ===

Key improvements:
1. ✅ Fixed regex patterns to match MTF format (Walk MP: vs walk mp:)
2. ✅ Added validation - walk MP should be > 0 for functional mechs  
3. ✅ Enhanced error logging to debug parsing failures
4. ✅ Added debug output for movement-related lines when parsing fails
5. ✅ Proper handling of jump MP = 0 (legitimate for non-jump mechs)

This fix should resolve the issue where walk_mp, run_mp, jump_mp read as 0.
""")
