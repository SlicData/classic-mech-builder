#!/usr/bin/env python3
"""
Critical Slot Parser - CMB-20 Step 5 - MINIMAL IMPLEMENTATION
🟢 GREEN PHASE: Just enough code to make tests pass
"""

import re
import logging
from typing import List, Optional

from .utils import CritSlotData, normalize_location

class CritSlotParser:
    """Minimal critical slot parser to make tests pass"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.max_slots = {
            'HD': 6, 'CT': 12, 'LT': 12, 'RT': 12,
            'LA': 12, 'RA': 12, 'LL': 6, 'RL': 6
        }
    
    def parse_critical_slots(self, content: str) -> List[CritSlotData]:
        """Parse critical slot data from MTF content"""
        crit_slots = []
        lines = content.split('\n')
        current_location = None
        slot_number = 1
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a location header
            if self._is_location_header(line):
                current_location = self._normalize_location(line)
                slot_number = 1
                continue
            
            # If we're in a location and line has equipment
            if current_location and line and not line.startswith('#'):
                equipment_name = line.strip()
                equipment_type = self.classify_equipment(equipment_name)
                
                crit_slots.append(CritSlotData(
                    location=current_location,
                    slot_index=slot_number,
                    item_type=equipment_type,
                    display_name=equipment_name
                ))
                slot_number += 1
        
        return crit_slots
    
    def validate_critical_slots(self, location: str, slots: List[dict]) -> bool:
        """Validate critical slots for a location"""
        max_slots = self.get_max_slots_for_location(location)
        return len(slots) <= max_slots
    
    def classify_equipment(self, equipment_name: str) -> str:
        """Classify equipment by type using valid database enum values"""
        equipment_lower = equipment_name.lower()
        
        if equipment_name == "-Empty-" or equipment_name == "Empty":
            return "empty"
        elif "autocannon" in equipment_lower or "lrm" in equipment_lower or "srm" in equipment_lower or "laser" in equipment_lower or "ppc" in equipment_lower:
            return "weapon"
        elif "heat sink" in equipment_lower:
            return "heat_sink"
        elif "ammo" in equipment_lower:
            return "ammo"
        elif any(word in equipment_lower for word in ["shoulder", "actuator", "hand"]):
            return "structural"  # Use 'structural' instead of 'actuator'
        elif any(word in equipment_lower for word in ["engine", "fusion", "gyro"]):
            return "engine"
        elif any(word in equipment_lower for word in ["cockpit", "sensors", "life support"]):
            return "cockpit"
        else:
            return "equipment"
    
    def get_max_slots_for_location(self, location: str) -> int:
        """Get maximum slots for a location"""
        return self.max_slots.get(location, 12)  # Default to 12 if unknown
    
    def _is_location_header(self, line: str) -> bool:
        """Check if line is a location header"""
        location_headers = [
            "Left Arm:", "Right Arm:", "Left Torso:", "Right Torso:",
            "Center Torso:", "Head:", "Left Leg:", "Right Leg:"
        ]
        return line in location_headers
    
    def _normalize_location(self, line: str) -> str:
        """Normalize location name to standard abbreviation"""
        location_map = {
            "Left Arm:": "LA",
            "Right Arm:": "RA", 
            "Left Torso:": "LT",
            "Right Torso:": "RT",
            "Center Torso:": "CT",
            "Head:": "HD",
            "Left Leg:": "LL",
            "Right Leg:": "RL"
        }
        return location_map.get(line, line)
