#!/usr/bin/env python3
"""
CMB-20 Step 2: Enhanced Weapon Parsing
Improved weapon detection and catalog population
"""

import re
from typing import Dict, List, Tuple

class WeaponParser:
    """Enhanced weapon parsing with normalization and classification"""
    
    def __init__(self):
        self.weapon_aliases = self._build_weapon_aliases()
        self.weapon_classes = self._build_weapon_classes()
        self.location_map = self._build_location_map()
    
    def parse_weapons_enhanced(self, content: str) -> List[dict]:
        """
        Enhanced weapon parsing from MTF Weapons section
        Returns list of weapon data with name, location, count
        """
        weapons = []
        
        # Find the weapons section
        weapons_match = re.search(r'^Weapons:\s*(\d+)', content, re.MULTILINE | re.IGNORECASE)
        if not weapons_match:
            return weapons
        
        weapon_count = int(weapons_match.group(1))
        
        # Parse weapons section line by line
        lines = content.split('\n')
        in_weapons_section = False
        weapons_parsed = 0
        
        for line in lines:
            line = line.strip()
            
            # Start of weapons section
            if re.match(r'^Weapons:\s*\d+', line, re.IGNORECASE):
                in_weapons_section = True
                continue
            
            if in_weapons_section:
                # Stop at next section or when we've found all weapons
                if not line or re.match(r'^[A-Z][A-Za-z\s]+:', line) or weapons_parsed >= weapon_count:
                    break
                
                # Parse weapon entry patterns:
                # "Autocannon/20, Left Arm"
                # "2 Medium Laser, Right Torso" 
                # "LRM 15, Left Torso"
                weapon_data = self._parse_weapon_line(line)
                if weapon_data:
                    weapons.append(weapon_data)
                    weapons_parsed += weapon_data['count']
        
        return weapons
    
    def _parse_weapon_line(self, line: str) -> dict:
        """Parse individual weapon line"""
        
        # Pattern 1: "Count WeaponName, Location" (e.g., "2 Medium Laser, Right Torso")
        count_pattern = r'^(\d+)\s+(.+?),\s*(.+)$'
        match = re.match(count_pattern, line)
        if match:
            count = int(match.group(1))
            weapon_name = match.group(2).strip()
            location = match.group(3).strip()
            
            return {
                'name': self._normalize_weapon_name(weapon_name),
                'raw_name': weapon_name,
                'location': self._normalize_location(location),
                'count': count
            }
        
        # Pattern 2: "WeaponName, Location" (e.g., "Autocannon/20, Left Arm")
        standard_pattern = r'^(.+?),\s*(.+)$'
        match = re.match(standard_pattern, line)
        if match:
            weapon_name = match.group(1).strip()
            location = match.group(2).strip()
            
            return {
                'name': self._normalize_weapon_name(weapon_name),
                'raw_name': weapon_name,
                'location': self._normalize_location(location),
                'count': 1
            }
        
        return None
    
    def _normalize_weapon_name(self, name: str) -> str:
        """Normalize weapon names using alias mapping"""
        name_lower = name.lower().strip()
        return self.weapon_aliases.get(name_lower, name.strip())
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location names"""
        location_lower = location.lower().strip()
        return self.location_map.get(location_lower, location.upper())
    
    def _classify_weapon(self, weapon_name: str) -> dict:
        """Classify weapon and return catalog data"""
        name_lower = weapon_name.lower()
        
        # Determine weapon class
        weapon_class = 'ballistic'  # default
        for class_name, keywords in self.weapon_classes.items():
            if any(keyword in name_lower for keyword in keywords):
                weapon_class = class_name
                break
        
        # Determine tech base
        tech_base = 'inner_sphere'  # default
        if name_lower.startswith('cl ') or 'clan' in name_lower:
            tech_base = 'clan'
        
        # Basic stats (could be enhanced with real weapon data)
        stats = self._get_basic_weapon_stats(weapon_name, weapon_class)
        
        return {
            'name': weapon_name,
            'class': weapon_class,
            'tech_base': tech_base,
            **stats
        }
    
    def _get_basic_weapon_stats(self, name: str, weapon_class: str) -> dict:
        """Get basic weapon statistics (simplified)"""
        name_lower = name.lower()
        
        # Basic heat values by weapon type
        heat_map = {
            'small laser': 1, 'medium laser': 3, 'large laser': 8,
            'er small laser': 2, 'er medium laser': 5, 'er large laser': 12,
            'ppc': 10, 'er ppc': 15,
            'autocannon/2': 1, 'autocannon/5': 1, 'autocannon/10': 3, 'autocannon/20': 7,
            'lrm 5': 2, 'lrm 10': 4, 'lrm 15': 5, 'lrm 20': 6,
            'srm 2': 2, 'srm 4': 3, 'srm 6': 4,
            'machine gun': 0
        }
        
        heat = heat_map.get(name_lower, 0)
        
        # Basic range/damage (simplified)
        if 'laser' in name_lower:
            if 'small' in name_lower:
                return {'heat': heat, 'short_range': 1, 'med_range': 2, 'long_range': 3, 'dmg_short': 3}
            elif 'medium' in name_lower:
                return {'heat': heat, 'short_range': 3, 'med_range': 6, 'long_range': 9, 'dmg_short': 5}
            elif 'large' in name_lower:
                return {'heat': heat, 'short_range': 5, 'med_range': 10, 'long_range': 15, 'dmg_short': 8}
        
        return {'heat': heat, 'short_range': 0, 'med_range': 0, 'long_range': 0, 'dmg_short': 0}
    
    def _build_weapon_aliases(self) -> Dict[str, str]:
        """Build comprehensive weapon name alias mapping"""
        return {
            # Autocannons
            'ac/2': 'Autocannon/2',
            'ac/5': 'Autocannon/5', 
            'ac/10': 'Autocannon/10',
            'ac/20': 'Autocannon/20',
            'autocannon/2': 'Autocannon/2',
            'autocannon/5': 'Autocannon/5',
            'autocannon/10': 'Autocannon/10',
            'autocannon/20': 'Autocannon/20',
            
            # Lasers
            'small laser': 'Small Laser',
            'medium laser': 'Medium Laser',
            'large laser': 'Large Laser',
            'er small laser': 'ER Small Laser',
            'er medium laser': 'ER Medium Laser', 
            'er large laser': 'ER Large Laser',
            'extended range small laser': 'ER Small Laser',
            'extended range medium laser': 'ER Medium Laser',
            'extended range large laser': 'ER Large Laser',
            
            # PPCs
            'ppc': 'PPC',
            'er ppc': 'ER PPC',
            'extended range ppc': 'ER PPC',
            
            # Missiles
            'lrm 5': 'LRM 5',
            'lrm 10': 'LRM 10',
            'lrm 15': 'LRM 15',
            'lrm 20': 'LRM 20',
            'lrm-5': 'LRM 5',
            'lrm-10': 'LRM 10',
            'lrm-15': 'LRM 15',
            'lrm-20': 'LRM 20',
            'srm 2': 'SRM 2',
            'srm 4': 'SRM 4',
            'srm 6': 'SRM 6',
            'srm-2': 'SRM 2',
            'srm-4': 'SRM 4',
            'srm-6': 'SRM 6',
            
            # Other weapons
            'machine gun': 'Machine Gun',
            'mg': 'Machine Gun',
            'flamer': 'Flamer',
            'gauss rifle': 'Gauss Rifle',
        }
    
    def _build_weapon_classes(self) -> Dict[str, List[str]]:
        """Build weapon classification mapping"""
        return {
            'energy': ['laser', 'ppc', 'flamer'],
            'ballistic': ['autocannon', 'machine gun', 'gauss', 'ac/'],
            'missile': ['lrm', 'srm', 'missile'],
            'support': ['tag', 'narc', 'artillery']
        }
    
    def _build_location_map(self) -> Dict[str, str]:
        """Build location mapping for normalization"""
        return {
            'head': 'HD',
            'center torso': 'CT',
            'left torso': 'LT',
            'right torso': 'RT', 
            'left arm': 'LA',
            'right arm': 'RA',
            'left leg': 'LL',
            'right leg': 'RL',
            # Variations
            'hd': 'HD', 'ct': 'CT', 'lt': 'LT', 'rt': 'RT',
            'la': 'LA', 'ra': 'RA', 'll': 'LL', 'rl': 'RL'
        }

def test_weapon_parsing():
    """Test the enhanced weapon parsing"""
    
    print("=== CMB-20 Step 2: Enhanced Weapon Parsing Test ===")
    
    # Sample King Crab weapons section
    king_crab_sample = """
Weapons:4
Autocannon/20, Left Arm
Autocannon/20, Right Arm
Large Laser, Right Torso
LRM 15, Left Torso
"""
    
    # Sample with count format
    multi_weapon_sample = """
Weapons:5
2 Medium Laser, Right Arm
Machine Gun, Left Arm
PPC, Right Torso
SRM 4, Left Torso
Small Laser, Head
"""
    
    parser = WeaponParser()
    
    # Test King Crab format
    print("\n--- King Crab Format ---")
    weapons = parser.parse_weapons_enhanced(king_crab_sample)
    for weapon in weapons:
        print(f"  {weapon['name']} x{weapon['count']} in {weapon['location']}")
        catalog_data = parser._classify_weapon(weapon['name'])
        print(f"    Class: {catalog_data['class']}, Tech: {catalog_data['tech_base']}, Heat: {catalog_data['heat']}")
    
    # Test multi-weapon format
    print("\n--- Multi-Weapon Format ---")
    weapons = parser.parse_weapons_enhanced(multi_weapon_sample)
    for weapon in weapons:
        print(f"  {weapon['name']} x{weapon['count']} in {weapon['location']}")
        catalog_data = parser._classify_weapon(weapon['name'])
        print(f"    Class: {catalog_data['class']}, Tech: {catalog_data['tech_base']}, Heat: {catalog_data['heat']}")

if __name__ == "__main__":
    test_weapon_parsing()
