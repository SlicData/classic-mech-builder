#!/usr/bin/env python3
"""
CMB-20 Complete Integration Test
Full test of enhanced MTF parsing and database integration
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def setup_logging():
    """Setup logging for test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def test_parsing_only():
    """Test parsing without database"""
    logger = setup_logging()
    logger.info("🔍 Testing MTF parsing only...")
    
    test_file = Path('data/test_mech.mtf')
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return False
    
    try:
        from mtf_parser.base_parser import MTFParser
        
        parser = MTFParser()
        mech_data = parser.parse_mtf_file(test_file)
        
        if not mech_data:
            logger.error("Failed to parse MTF file")
            return False
        
        logger.info(f"✅ Parsed: {mech_data.chassis} {mech_data.model}")
        logger.info(f"   Tonnage: {mech_data.tonnage}t")
        logger.info(f"   Movement: {mech_data.walk_mp}/{mech_data.run_mp}/{mech_data.jump_mp}")
        logger.info(f"   Engine: {mech_data.engine_type.value} {mech_data.engine_rating}")
        logger.info(f"   Heat Sinks: {mech_data.heat_sinks}")
        
        logger.info(f"📊 Detailed Data:")
        logger.info(f"   Weapons: {len(mech_data.weapons)}")
        for weapon in mech_data.weapons[:3]:  # Show first 3
            logger.info(f"     - {weapon.name} x{weapon.count} in {weapon.location}")
        
        logger.info(f"   Armor locations: {len(mech_data.armor)}")
        for armor in mech_data.armor[:3]:  # Show first 3
            logger.info(f"     - {armor.location}: {armor.armor_front} armor, {armor.internal} internal")
        
        logger.info(f"   Equipment: {len(mech_data.equipment)}")
        logger.info(f"   Critical slots: {len(mech_data.crit_slots)}")
        logger.info(f"   Quirks: {len(mech_data.quirks)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Parsing test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_database_integration():
    """Test full database integration"""
    logger = setup_logging()
    logger.info("🔍 Testing database integration...")
    
    try:
        from mtf_parser.base_parser import MTFParser
        from database.seeder import DatabaseSeeder
        
        # Parse the test file
        test_file = Path('data/test_mech.mtf')
        parser = MTFParser()
        mech_data = parser.parse_mtf_file(test_file)
        
        if not mech_data:
            logger.error("Failed to parse MTF file for database test")
            return False
        
        # Try database connection and insertion
        db = DatabaseSeeder('cmb_dev')
        db.connect()
        
        success = db.insert_mech(mech_data)
        db.close()
        
        if success:
            logger.info("✅ Database integration successful!")
            return True
        else:
            logger.error("❌ Database insertion failed")
            return False
            
    except Exception as e:
        logger.error(f"Database integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_validation_queries():
    """Run validation queries to check database population"""
    logger = setup_logging()
    logger.info("🔍 Running database validation queries...")
    
    try:
        import psycopg2
        
        # Connect to database
        from database.seeder import DatabaseSeeder
        db = DatabaseSeeder('cmb_dev')
        db.connect()
        
        cursor = db.conn.cursor()
        
        # Run validation queries
        queries = [
            ("Mechs", "SELECT COUNT(*) FROM mech"),
            ("Weapons in catalog", "SELECT COUNT(*) FROM weapon_catalog"),
            ("Mech weapons", "SELECT COUNT(*) FROM mech_weapon"),
            ("Mech armor", "SELECT COUNT(*) FROM mech_armor"),
            ("Equipment in catalog", "SELECT COUNT(*) FROM equipment_catalog"),
            ("Mech equipment", "SELECT COUNT(*) FROM mech_equipment"),
            ("Critical slots", "SELECT COUNT(*) FROM mech_crit_slot"),
            ("Quirks", "SELECT COUNT(*) FROM mech_quirk")
        ]
        
        for name, query in queries:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "❌"
            logger.info(f"   {status} {name}: {count}")
        
        # Show sample data
        logger.info("\n📊 Sample Data:")
        cursor.execute("SELECT chassis, model, tonnage, walk_mp FROM mech LIMIT 3")
        mechs = cursor.fetchall()
        for mech in mechs:
            logger.info(f"   - {mech[0]} {mech[1]} ({mech[2]}t, {mech[3]} walk)")
        
        cursor.execute("SELECT name, class FROM weapon_catalog LIMIT 3")
        weapons = cursor.fetchall()
        if weapons:
            logger.info("   Weapons:")
            for weapon in weapons:
                logger.info(f"   - {weapon[0]} ({weapon[1]})")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Validation queries failed: {e}")
        return False

def main():
    """Run complete integration test suite"""
    logger = setup_logging()
    logger.info("🚀 CMB-20 Complete Integration Test")
    logger.info("=" * 50)
    
    # Test 1: Parsing only
    logger.info("\n1️⃣ PARSING TEST")
    if not test_parsing_only():
        logger.error("💥 Parsing test failed - stopping here")
        return False
    
    # Test 2: Database integration
    logger.info("\n2️⃣ DATABASE INTEGRATION TEST")
    if not test_database_integration():
        logger.error("💥 Database integration failed")
        return False
    
    # Test 3: Validation queries
    logger.info("\n3️⃣ DATABASE VALIDATION")
    if not run_validation_queries():
        logger.error("💥 Database validation failed")
        return False
    
    logger.info("\n🎯 ALL TESTS PASSED!")
    logger.info("CMB-20 integration is working correctly.")
    logger.info("Ready for full MegaMek data import!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
