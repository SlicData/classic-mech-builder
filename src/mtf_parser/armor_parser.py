#!/usr/bin/env python3
"""
Armor Parser - CMB-20 Step 3
Enhanced armor parsing with validation and comprehensive location support
"""

import re
import logging
from typing import List, Dict, Tuple
from .utils import ArmorData, calc_internal_structure

class ArmorParser:
    """Parser for BattleMech armor values with comprehensive location support"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.location_patterns = self._build_location_patterns()
        self.armor_types = self._build_armor_types()
    
    def parse_armor(self, content: str, tonnage: int = 0) -> Tuple[List[ArmorData], str]:
        """
        Parse all armor values from MTF content
        Returns (armor_data_list, armor_type)
        """
        armor_data = []
        armor_type = self._parse_armor_type(content)
        
        # Parse all armor locations
        for location, patterns in self.location_patterns.items():
            armor_values = self._parse_location_armor(content, location, patterns)
            if armor_values:
                armor_data.append(armor_values)
        
        # Validate armor totals if tonnage provided
        if tonnage > 0:
            self._validate_armor_totals(armor_data, tonnage, armor_type)
        
        return armor_data, armor_type
    
    def _parse_location_armor(self, content: str, location: str, patterns: List[str]) -> ArmorData:
        """Parse armor values for a specific location"""
        armor_front = 0
        armor_rear = None
        
        # Try each pattern for this location
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                armor_front = int(match.group(1))
                break
        
        # Check for rear armor (torso locations only)
        if location in ['CT', 'LT', 'RT']:
            rear_patterns = [
                rf'{location}R armor:\s*(\d+)',
                rf'R{location} armor:\s*(\d+)',
                rf'{location} rear armor:\s*(\d+)'
            ]
            
            for pattern in rear_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    armor_rear = int(match.group(1))
                    break
        
        if armor_front > 0:
            return ArmorData(
                location=location,
                armor_front=armor_front,
                armor_rear=armor_rear,
                internal=calc_internal_structure(location)
            )
        
        return None
    
    def _parse_armor_type(self, content: str) -> str:
        """Parse armor type from MTF content"""
        patterns = [
            r'Armor:\s*(.+?)(?:\(|$)',
            r'armor type:\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                armor_type_raw = match.group(1).strip()
                return self._normalize_armor_type(armor_type_raw)
        
        return 'Standard'  # Default
    
    def _normalize_armor_type(self, armor_type: str) -> str:
        """Normalize armor type names"""
        armor_type_lower = armor_type.lower()
        
        if 'ferro' in armor_type_lower:
            return 'Ferro-Fibrous'
        elif 'stealth' in armor_type_lower:
            return 'Stealth'
        elif 'hardened' in armor_type_lower:
            return 'Hardened'
        elif 'reactive' in armor_type_lower:
            return 'Reactive'
        elif 'reflective' in armor_type_lower:
            return 'Reflective'
        else:
            return 'Standard'
    
    def _validate_armor_totals(self, armor_data: List[ArmorData], tonnage: int, armor_type: str):
        """Validate armor totals against mech tonnage"""
        total_armor = sum(
            (armor.armor_front or 0) + (armor.armor_rear or 0) 
            for armor in armor_data if armor
        )
        
        # Calculate maximum possible armor for this tonnage
        max_armor = self._calculate_max_armor(tonnage, armor_type)
        
        if total_armor > max_armor:
            self.logger.warning(f"Armor total ({total_armor}) exceeds maximum for {tonnage}t mech ({max_armor})")
        elif total_armor == 0:
            self.logger.error(f"No armor values found - this may indicate parsing failure")
        else:
            self.logger.debug(f"Armor total: {total_armor}/{max_armor} points")
    
    def _calculate_max_armor(self, tonnage: int, armor_type: str) -> int:
        """Calculate maximum armor for tonnage and type"""
        # Basic BattleTech armor calculation
        # Standard: tonnage * 18.5 (rounded down)
        # Ferro-Fibrous: tonnage * 19.5 (rounded down) 
        
        if armor_type == 'Ferro-Fibrous':
            return int(tonnage * 19.5)
        elif armor_type == 'Hardened':
            return int(tonnage * 12)  # Hardened armor is heavier but stronger
        else:
            return int(tonnage * 18.5)  # Standard armor
    
    def _build_location_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for all armor locations"""
        return {
            'HD': [
                r'HD armor:\s*(\d+)',
                r'Head armor:\s*(\d+)',
                r'H armor:\s*(\d+)'
            ],
            'CT': [
                r'CT armor:\s*(\d+)', 
                r'Center Torso armor:\s*(\d+)',
                r'Centre Torso armor:\s*(\d+)'
            ],
            'LT': [
                r'LT armor:\s*(\d+)',
                r'Left Torso armor:\s*(\d+)'
            ],
            'RT': [
                r'RT armor:\s*(\d+)',
                r'Right Torso armor:\s*(\d+)'
            ],
            'LA': [
                r'LA armor:\s*(\d+)',
                r'Left Arm armor:\s*(\d+)'
            ],
            'RA': [
                r'RA armor:\s*(\d+)',
                r'Right Arm armor:\s*(\d+)'
            ],
            'LL': [
                r'LL armor:\s*(\d+)',
                r'Left Leg armor:\s*(\d+)'
            ],
            'RL': [
                r'RL armor:\s*(\d+)',
                r'Right Leg armor:\s*(\d+)'
            ]
        }
    
    def _build_armor_types(self) -> List[str]:
        """List of supported armor types"""
        return [
            'Standard',
            'Ferro-Fibrous', 
            'Stealth',
            'Hardened',
            'Reactive',
            'Reflective'
        ]
    
    def get_armor_summary(self, armor_data: List[ArmorData]) -> Dict[str, int]:
        """Generate armor summary statistics"""
        total_front = sum((armor.armor_front or 0) for armor in armor_data if armor)
        total_rear = sum((armor.armor_rear or 0) for armor in armor_data if armor)
        total_internal = sum((armor.internal or 0) for armor in armor_data if armor)
        
        return {
            'total_armor': total_front + total_rear,
            'front_armor': total_front,
            'rear_armor': total_rear,
            'total_internal': total_internal,
            'locations_with_armor': len([a for a in armor_data if a and a.armor_front > 0])
        }
