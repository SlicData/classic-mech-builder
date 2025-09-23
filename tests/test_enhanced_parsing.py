#!/usr/bin/env python3
"""
Test the enhanced MTF seeder with weapon, armor, and equipment parsing
"""

import sys
sys.path.append('/Users/justi/classic-mech-builder/db/seeds')

from mtf_seeder import MTFParser
from pathlib import Path

def test_enhanced_parsing():
    """Test the new parsing capabilities"""
    
    # Test with King Crab MTF content
    test_content = """
chassis:King Crab
model:KGC-009C
mul id:8066
Config:Biped
techbase:Mixed (IS Chassis)
era:3143
source:TRO: 3150
rules level:2

quirk:command_mech

mass:100
engine:300 Fusion Engine(IS)
structure:IS Endo Steel
myomer:Standard
cockpit:Small Cockpit
gyro:Heavy Duty Gyro

heat sinks:14 IS Double
walk mp:3
jump mp:0

armor:Standard(Clan)
LA armor:34
RA armor:34
LT armor:32
RT armor:32
CT armor:46
HD armor:9
LL armor:42
RL armor:42
RTL armor:10
RTR armor:10
RTC armor:16

Weapons:6
HAG/20, Left Arm
Plasma Rifle, Left Arm
HAG/20, Right Arm
Plasma Rifle, Right Arm
ER Small Laser, Left Torso
ER Small Laser, Right Torso

Left Arm:
Shoulder
Upper Arm Actuator
CLHAG20
CLHAG20
CLHAG20
CLHAG20
CLHAG20
CLHAG20
ISPlasmaRifle
ISPlasmaRifle
IS Endo Steel
IS Endo Steel

Right Arm:
Shoulder
Upper Arm Actuator
CLHAG20
CLHAG20
CLHAG20
CLHAG20
CLHAG20
CLHAG20
ISPlasmaRifle
ISPlasmaRifle
IS Endo Steel
IS Endo Steel
"""
    
    parser = MTFParser()
    mech_data = parser.parse_mtf_file_from_content(test_content)
    
    if mech_data:
        print("Enhanced MTF Parsing Test Results:")
        print(f"Chassis: {mech_data.chassis}")
        print(f"Model: {mech_data.model}")
        print(f"Walk MP: {mech_data.walk_mp}")
        print(f"Jump MP: {mech_data.jump_mp}")
        print(f"Tech Base: {mech_data.tech_base}")
        print(f"Era: {mech_data.era}")
        
        print(f"\nWeapons ({len(mech_data.weapons)}):")
        for weapon in mech_data.weapons:
            print(f"  - {weapon.name} in {weapon.location}")
        
        print(f"\nArmor ({len(mech_data.armor)}):")
        for armor in mech_data.armor:
            rear_info = f" (rear: {armor.armor_rear})" if armor.armor_rear else ""
            print(f"  - {armor.location}: {armor.armor_front}{rear_info}")
        
        print(f"\nQuirks ({len(mech_data.quirks)}):")
        for quirk in mech_data.quirks:
            print(f"  - {quirk}")
        
        print(f"\nCritical Slots ({len(mech_data.crit_slots)}):")
        for slot in mech_data.crit_slots[:10]:  # Show first 10
            print(f"  - {slot.location} slot {slot.slot_index}: {slot.display_name} ({slot.item_type})")
        if len(mech_data.crit_slots) > 10:
            print(f"  ... and {len(mech_data.crit_slots) - 10} more slots")
            
        return True
    else:
        print("Failed to parse test content")
        return False

def add_parse_from_content_method():
    """Add a helper method to parse from string content"""
    # We need to add a method to parse from string content rather than file
    import tempfile
    
    def parse_mtf_file_from_content(self, content: str):
        """Parse MTF content from string"""
        try:
            # Extract basic info
            chassis_model = self._extract_chassis_model(content)
            if not chassis_model:
                return None
            
            chassis, model = chassis_model
            
            # Parse all fields using existing methods
            from mtf_seeder import MechData
            data = MechData(
                chassis=chassis,
                model=model,
                tech_base=self._parse_tech_base(content),
                era=self._parse_era(content),
                rules_level=self._parse_rules_level(content),
                tonnage=self._parse_tonnage(content),
                battle_value=self._calculate_battle_value(content),
                walk_mp=self._parse_walk_mp(content),
                run_mp=self._parse_run_mp(content),
                jump_mp=self._parse_jump_mp(content),
                engine_type=self._parse_engine_type(content),
                engine_rating=self._parse_engine_rating(content),
                heat_sinks=self._parse_heat_sinks(content),
                armor_type=self._parse_armor_type(content),
                role=self._parse_role(content),
                year=self._parse_year(content),
                source=self._parse_source(content),
                cost_cbill=self._parse_cost(content),
                # Parse new detailed data
                weapons=self._parse_weapons(content),
                armor=self._parse_armor_values(content),
                equipment=self._parse_equipment(content),
                crit_slots=self._parse_crit_slots(content),
                quirks=self._parse_quirks(content)
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing content: {e}")
            return None
    
    # Add method to MTFParser class
    from mtf_seeder import MTFParser
    MTFParser.parse_mtf_file_from_content = parse_mtf_file_from_content

if __name__ == "__main__":
    add_parse_from_content_method()
    success = test_enhanced_parsing()
    
    if success:
        print("\n✅ Enhanced MTF parsing is working!")
        print("Ready to test with database integration.")
    else:
        print("\n❌ Enhanced MTF parsing failed.")
    
    sys.exit(0 if success else 1)
