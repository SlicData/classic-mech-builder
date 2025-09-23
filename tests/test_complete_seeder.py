#!/usr/bin/env python3
"""
Test the enhanced MTF seeder with a small subset of files
"""

import sys
import os
sys.path.append('/Users/justi/classic-mech-builder/db/seeds')

from mtf_seeder import MTFParser, DatabaseSeeder, MechData
from pathlib import Path
import logging

def test_complete_seeder():
    """Test the complete enhanced seeder with database integration"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Test with actual MTF file
    test_file = Path('/Users/justi/classic-mech-builder/data/test_mech.mtf')
    
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return False
    
    # Parse the file
    parser = MTFParser()
    mech_data = parser.parse_mtf_file(test_file)
    
    if not mech_data:
        logger.error("Failed to parse test file")
        return False
    
    logger.info(f"Parsed mech: {mech_data.chassis} {mech_data.model}")
    logger.info(f"  Weapons: {len(mech_data.weapons)}")
    logger.info(f"  Armor locations: {len(mech_data.armor)}")
    logger.info(f"  Equipment: {len(mech_data.equipment)}")
    logger.info(f"  Critical slots: {len(mech_data.crit_slots)}")
    logger.info(f"  Quirks: {len(mech_data.quirks)}")
    
    # Test database insertion
    db = DatabaseSeeder('cmb_dev')
    try:
        db.connect()
        
        # Insert the parsed mech
        success = db.insert_mech(mech_data)
        
        if success:
            logger.info("✅ Successfully inserted enhanced mech data!")
            return True
        else:
            logger.error("❌ Failed to insert mech data")
            return False
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_complete_seeder()
    
    if success:
        print("\n🎯 Enhanced seeder test successful!")
        print("Ready to run full seeding with complete data.")
    else:
        print("\n💥 Enhanced seeder test failed.")
    
    sys.exit(0 if success else 1)
