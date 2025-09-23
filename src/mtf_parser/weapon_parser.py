#!/usr/bin/env python3
"""
Weapon Parser - CMB-20 Step 2
Enhanced weapon parsing with normalization and classification
"""

import re
import logging
from typing import Dict, List, Optional
from .utils import WeaponData, normalize_location

class WeaponParser:
    """Parser for BattleMech weapons with normalization and classification"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.weapon_aliases = self._build_weapon_aliases()
    
    def parse_weapons(self, content: str) -> List[WeaponData]:
        """Enhanced weapon parsing with normalization and classification"""
        weapons = []
        
        # Find weapons count line
        weapons_match = re.search(r'^Weapons:\s*(\d+)', content, re.MULTILINE | re.IGNORECASE)
        if not weapons_match:
            return weapons
        
        weapon_count = int(weapons_match.group(1))
        
        lines = content.split('\n')
        in_weapons = False
        weapons_parsed = 0
        
        for line in lines:
            line = line.strip()
            
            if re.match(r'^Weapons:\s*\d+', line, re.IGNORECASE):
                in_weapons = True
                continue
            
            if in_weapons:
                # Stop at next section or when we've found all weapons
                if not line or re.match(r'^[A-Z][A-Za-z\s]+:', line) or weapons_parsed >= weapon_count:
                    break
                
                # Parse weapon entry patterns:
                # "Autocannon/20, Left Arm"
                # "2 Medium Laser, Right Torso" 
                weapon_data = self._parse_weapon_line(line)
                if weapon_data:
                    weapons.append(weapon_data)
                    weapons_parsed += weapon_data.count
        
        return weapons
    
    def _parse_weapon_line(self, line: str) -> Optional[WeaponData]:
        """Parse individual weapon line"""
        
        # Pattern 1: "Count WeaponName, Location" (e.g., "2 Medium Laser, Right Torso")
        count_pattern = r'^(\d+)\s+(.+?),\s*(.+)$'
        match = re.match(count_pattern, line)
        if match:
            count = int(match.group(1))
            weapon_name = self._normalize_weapon_name(match.group(2).strip())
            location = normalize_location(match.group(3).strip())
            
            return WeaponData(
                name=weapon_name,
                location=location,
                count=count
            )
        
        # Pattern 2: "WeaponName, Location" (e.g., "Autocannon/20, Left Arm")
        standard_pattern = r'^(.+?),\s*(.+)$'
        match = re.match(standard_pattern, line)
        if match:
            weapon_name = self._normalize_weapon_name(match.group(1).strip())
            location = normalize_location(match.group(2).strip())
            
            return WeaponData(
                name=weapon_name,
                location=location,
                count=1
            )
        
        return None
    
    def _normalize_weapon_name(self, name: str) -> str:
        """Normalize weapon names using alias mapping"""
        name_lower = name.lower().strip()
        return self.weapon_aliases.get(name_lower, name.strip())
    
    def _build_weapon_aliases(self) -> Dict[str, str]:
        """Build comprehensive weapon name alias mapping"""
        return {
            # Autocannons
            'ac/2': 'Autocannon/2', 'ac/5': 'Autocannon/5', 
            'ac/10': 'Autocannon/10', 'ac/20': 'Autocannon/20',
            'autocannon/2': 'Autocannon/2', 'autocannon/5': 'Autocannon/5',
            'autocannon/10': 'Autocannon/10', 'autocannon/20': 'Autocannon/20',
            
            # Lasers
            'small laser': 'Small Laser', 'medium laser': 'Medium Laser',
            'large laser': 'Large Laser', 'er small laser': 'ER Small Laser',
            'er medium laser': 'ER Medium Laser', 'er large laser': 'ER Large Laser',
            
            # PPCs
            'ppc': 'PPC', 'er ppc': 'ER PPC',
            
            # Missiles
            'lrm 5': 'LRM 5', 'lrm 10': 'LRM 10', 'lrm 15': 'LRM 15', 'lrm 20': 'LRM 20',
            'lrm-5': 'LRM 5', 'lrm-10': 'LRM 10', 'lrm-15': 'LRM 15', 'lrm-20': 'LRM 20',
            'srm 2': 'SRM 2', 'srm 4': 'SRM 4', 'srm 6': 'SRM 6',
            'srm-2': 'SRM 2', 'srm-4': 'SRM 4', 'srm-6': 'SRM 6',
            
            # Other weapons
            'machine gun': 'Machine Gun', 'flamer': 'Flamer', 'gauss rifle': 'Gauss Rifle',
        }
    
    def classify_weapon_type(self, weapon_name: str) -> str:
        """Classify weapon by type for database storage"""
        name_lower = weapon_name.lower()
        
        if any(word in name_lower for word in ['laser', 'ppc']):
            return 'energy'
        elif any(word in name_lower for word in ['lrm', 'srm', 'missile']):
            return 'missile'
        elif any(word in name_lower for word in ['autocannon', 'machine gun', 'gauss', 'ac/']):
            return 'ballistic'
        else:
            return 'ballistic'  # default
    
    def determine_tech_base(self, weapon_name: str) -> str:
        """Determine if weapon is Inner Sphere or Clan"""
        name_lower = weapon_name.lower()
        if weapon_name.upper().startswith('CL') or 'clan' in name_lower:
            return 'clan'
        return 'inner_sphere'
