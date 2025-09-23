#!/usr/bin/env python3
"""
Engine Parser - CMB-20 Step 4 - REFACTORED VERSION
REFACTOR PHASE: Enhanced, production-ready implementation
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum
from .utils import EngineType

class HeatSinkType(Enum):
    """BattleTech heat sink types"""
    SINGLE = "Single"
    DOUBLE = "Double"

@dataclass
class EngineData:
    """Data structure for engine information"""
    rating: int
    engine_type: EngineType
    weight: float = 0.0
    
    def __post_init__(self):
        """Calculate engine weight based on type and rating"""
        self.weight = self._calculate_engine_weight()
    
    def _calculate_engine_weight(self) -> float:
        """Calculate engine weight using BattleTech rules"""
        if self.engine_type == EngineType.FUSION:
            # Standard Fusion engine weight calculation
            if self.rating <= 400:
                return self.rating / 25.0
            else:
                return (self.rating - 400) / 25.0 + 16.0
        elif self.engine_type == EngineType.XL_FUSION:
            # XL engines are half weight
            return self._calculate_engine_weight() / 2.0 if self.engine_type == EngineType.FUSION else self.rating / 50.0
        else:
            # Default to fusion calculation for unknown types
            return self.rating / 25.0

@dataclass  
class HeatSinkData:
    """Data structure for heat sink information"""
    count: int
    heat_sink_type: HeatSinkType
    engine_heat_sinks: int = 0
    external_heat_sinks: int = 0
    
    def __post_init__(self):
        """Calculate engine vs external heat sinks"""
        # Engines include up to 10 heat sinks for free
        self.engine_heat_sinks = min(10, self.count)
        self.external_heat_sinks = max(0, self.count - 10)

class EngineParser:
    """Enhanced engine and heat sink parser with comprehensive validation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.engine_patterns = self._build_engine_patterns()
        self.heat_sink_patterns = self._build_heat_sink_patterns()
    
    def parse_engine(self, content: str) -> Optional[EngineData]:
        """Parse engine data from MTF content with enhanced patterns"""
        for pattern in self.engine_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    rating = int(match.group(1))
                    engine_type_str = match.group(2).strip()
                    engine_type = self._normalize_engine_type(engine_type_str)
                    
                    return EngineData(rating=rating, engine_type=engine_type)
                except ValueError as e:
                    self.logger.warning(f"Failed to parse engine rating: {e}")
                    continue
        
        self.logger.warning("No engine data found in MTF content")
        return None
    
    def parse_heat_sinks(self, content: str) -> Optional[HeatSinkData]:
        """Parse heat sink data from MTF content with enhanced patterns"""
        for pattern in self.heat_sink_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    count = int(match.group(1))
                    heat_sink_type_str = match.group(2).strip()
                    heat_sink_type = self._normalize_heat_sink_type(heat_sink_type_str)
                    
                    return HeatSinkData(count=count, heat_sink_type=heat_sink_type)
                except ValueError as e:
                    self.logger.warning(f"Failed to parse heat sink count: {e}")
                    continue
        
        self.logger.warning("No heat sink data found in MTF content")
        return None
    
    def validate_engine_rating(self, tonnage: int, engine_rating: int, walk_mp: int) -> bool:
        """Validate engine rating against mech tonnage and movement"""
        if tonnage <= 0 or engine_rating <= 0:
            return False
            
        # BattleTech formula: Engine Rating / Tonnage = Walk MP
        expected_walk_mp = engine_rating // tonnage
        
        is_valid = expected_walk_mp == walk_mp
        
        if not is_valid:
            self.logger.warning(
                f"Engine validation failed: {engine_rating}/{tonnage} = {expected_walk_mp}, "
                f"but walk MP is {walk_mp}"
            )
        else:
            self.logger.debug(f"Engine validation passed: {engine_rating}/{tonnage} = {walk_mp}")
        
        return is_valid
    
    def validate_heat_sinks(self, heat_sink_data: HeatSinkData, engine_data: EngineData) -> bool:
        """Validate heat sink configuration"""
        if not heat_sink_data or not engine_data:
            return False
        
        # Minimum heat sinks = engine rating / 25 (rounded up)
        min_heat_sinks = (engine_data.rating + 24) // 25  # Ceiling division
        
        if heat_sink_data.count < min_heat_sinks:
            self.logger.warning(
                f"Insufficient heat sinks: {heat_sink_data.count} < {min_heat_sinks} "
                f"(minimum for {engine_data.rating} engine)"
            )
            return False
        
        return True
    
    def _normalize_engine_type(self, engine_type_str: str) -> EngineType:
        """Normalize engine type string to enum"""
        engine_type_lower = engine_type_str.lower()
        
        if 'xxl' in engine_type_lower:
            return EngineType.XXL_FUSION
        elif 'xl' in engine_type_lower:
            return EngineType.XL_FUSION
        elif 'light' in engine_type_lower:
            return EngineType.LIGHT_FUSION
        elif 'compact' in engine_type_lower:
            return EngineType.COMPACT_FUSION
        elif 'ice' in engine_type_lower:
            return EngineType.ICE
        elif 'fuel' in engine_type_lower:
            return EngineType.FUEL_CELL
        else:
            return EngineType.FUSION  # Default
    
    def _normalize_heat_sink_type(self, heat_sink_type_str: str) -> HeatSinkType:
        """Normalize heat sink type string to enum"""
        heat_sink_type_lower = heat_sink_type_str.lower()
        
        if 'double' in heat_sink_type_lower or 'dhs' in heat_sink_type_lower:
            return HeatSinkType.DOUBLE
        else:
            return HeatSinkType.SINGLE  # Default
    
    def _build_engine_patterns(self) -> List[str]:
        """Build regex patterns for engine parsing"""
        return [
            r'Engine:\s*(\d+)\s+(.+?)\s+Engine',      # "Engine:300 Fusion Engine"
            r'Engine:\s*(\d+)\s+(.+)',                 # "Engine:300 Fusion"
            r'(\d+)\s+(.+?)\s+Engine',                 # "300 Fusion Engine"
        ]
    
    def _build_heat_sink_patterns(self) -> List[str]:
        """Build regex patterns for heat sink parsing"""
        return [
            r'Heat Sinks:\s*(\d+)\s+(.+)',             # "Heat Sinks:20 Single"
            r'Heat Sinks:\s*(\d+)',                    # "Heat Sinks:20" (assume Single)
            r'(\d+)\s+(.+?)\s+Heat Sinks?',           # "20 Single Heat Sinks"
        ]
    
    def get_engine_summary(self, engine_data: EngineData, heat_sink_data: HeatSinkData) -> Dict[str, any]:
        """Generate engine and heat sink summary"""
        return {
            'engine_rating': engine_data.rating if engine_data else 0,
            'engine_type': engine_data.engine_type.value if engine_data else 'Unknown',
            'engine_weight': engine_data.weight if engine_data else 0.0,
            'heat_sink_count': heat_sink_data.count if heat_sink_data else 0,
            'heat_sink_type': heat_sink_data.heat_sink_type.value if heat_sink_data else 'Unknown',
            'engine_heat_sinks': heat_sink_data.engine_heat_sinks if heat_sink_data else 0,
            'external_heat_sinks': heat_sink_data.external_heat_sinks if heat_sink_data else 0,
        }
