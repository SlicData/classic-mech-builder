#!/usr/bin/env python3
"""
Base MTF Parser - Main parsing orchestrator
"""

import re
import logging
from pathlib import Path
from typing import Optional, List

from .utils import (
    MechData, TechBase, Era, EngineType, ArmorType, ArmorData, EquipmentData, 
    CritSlotData, extract_chassis_model, calc_internal_structure
)
from .movement_parser import MovementParser
from .weapon_parser import WeaponParser
from .armor_parser import ArmorParser
from .engine_parser import EngineParser
from .crit_slot_parser import CritSlotParser

class MTFParser:
    """Main MTF file parser that orchestrates all sub-parsers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.movement_parser = MovementParser(self.logger)
        self.weapon_parser = WeaponParser(self.logger)
        self.armor_parser = ArmorParser(self.logger)
        self.engine_parser = EngineParser(self.logger)
        self.crit_slot_parser = CritSlotParser(self.logger)
    
    def parse_mtf_file(self, file_path: Path) -> Optional[MechData]:
        """Parse MTF file and return MechData object"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            chassis_model = extract_chassis_model(content)
            if not chassis_model:
                return None
            chassis, model = chassis_model
            
            # Parse movement with validation
            walk_mp, run_mp, jump_mp = self.movement_parser.parse_movement(content)
            
            # Parse armor with validation
            armor_data, armor_type_parsed = self.armor_parser.parse_armor(content, self._parse_tonnage(content))
            
            # If no armor data from advanced parser, use fallback
            if not armor_data:
                armor_data = self._parse_armor_values(content)
            
            # Parse engine and heat sinks
            engine_data = self.engine_parser.parse_engine(content)
            heat_sink_data = self.engine_parser.parse_heat_sinks(content)
            
            # Validate engine against movement
            if engine_data:
                self.engine_parser.validate_engine_rating(
                    self._parse_tonnage(content), engine_data.rating, walk_mp
                )
            
            # Validate heat sinks against engine  
            if engine_data and heat_sink_data:
                self.engine_parser.validate_heat_sinks(heat_sink_data, engine_data)
            
            # Parse critical slots
            crit_slots = self.crit_slot_parser.parse_critical_slots(content)
            
            # Validate movement
            self.movement_parser.validate_movement(
                walk_mp, run_mp, jump_mp, chassis, model, file_path.name, content
            )
            
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
                engine_type=engine_data.engine_type if engine_data else self._parse_engine_type(content),
                engine_rating=engine_data.rating if engine_data else self._parse_engine_rating(content),
                heat_sinks=heat_sink_data.count if heat_sink_data else self._parse_heat_sinks(content),
                armor_type=self._parse_armor_type(content),
                role=self._parse_role(content),
                year=self._parse_year(content),
                source=self._parse_source(content),
                cost_cbill=self._parse_cost(content),
                weapons=self.weapon_parser.parse_weapons(content),
                armor=armor_data,  # This should be a list of ArmorData
                equipment=self._parse_equipment(content),
                crit_slots=crit_slots,
                quirks=self._parse_quirks(content)
            )
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    # Basic parsing methods (these could be moved to separate parsers too)
    def _parse_tech_base(self, content: str) -> TechBase:
        match = re.search(r'techbase:\s*(.+)', content, re.IGNORECASE)
        if match:
            value = match.group(1).strip().lower()
            if "inner sphere" in value: return TechBase.INNER_SPHERE
            elif "clan" in value: return TechBase.CLAN
        return TechBase.INNER_SPHERE
    
    def _parse_era(self, content: str) -> Era:
        return Era.SUCCESSION  # Default for simplicity
    
    def _parse_rules_level(self, content: str) -> int:
        match = re.search(r'rules level:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 1
    
    def _parse_tonnage(self, content: str) -> int:
        match = re.search(r'mass:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _calculate_battle_value(self, content: str) -> int:
        return self._parse_tonnage(content) * 20  # Simple estimate
    
    def _parse_engine_type(self, content: str) -> EngineType:
        return EngineType.FUSION  # Default
    
    def _parse_engine_rating(self, content: str) -> int:
        match = re.search(r'engine:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _parse_heat_sinks(self, content: str) -> int:
        match = re.search(r'heat sinks:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _parse_armor_type(self, content: str) -> ArmorType:
        return ArmorType.STANDARD  # Default
    
    def _parse_role(self, content: str) -> Optional[str]:
        return None
    
    def _parse_year(self, content: str) -> Optional[int]:
        match = re.search(r'era:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _parse_source(self, content: str) -> Optional[str]:
        match = re.search(r'source:\s*(.+)', content, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _parse_cost(self, content: str) -> Optional[int]:
        return None
    
    def _parse_armor_values(self, content: str) -> List[ArmorData]:
        armor = []
        patterns = {
            'LA': r'LA armor:\s*(\d+)', 'RA': r'RA armor:\s*(\d+)', 
            'CT': r'CT armor:\s*(\d+)', 'HD': r'HD armor:\s*(\d+)'
        }
        
        for location, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                armor.append(ArmorData(
                    location=location, 
                    armor_front=int(match.group(1)), 
                    internal=calc_internal_structure(location)
                ))
        return armor
    
    def _parse_equipment(self, content: str) -> List[EquipmentData]:
        return []  # Simplified for now
    
    def _parse_crit_slots(self, content: str) -> List[CritSlotData]:
        return []  # Simplified for now
    
    def _parse_quirks(self, content: str) -> List[str]:
        return []  # Simplified for now
