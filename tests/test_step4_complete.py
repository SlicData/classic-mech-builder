#!/usr/bin/env python3
"""
Test CMB-20 Step 4: Engine Parser - Complete TDD Verification
REFACTOR PHASE: Verify enhanced implementation works perfectly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_original_requirements_still_pass():
    """Verify our refactored code still passes original TDD tests"""
    
    print("🔄 REFACTOR VERIFICATION: Original requirements...")
    
    # Original test data from GREEN phase
    atlas_engine_sample = """
chassis:Atlas
model:AS7-D

Mass:100
Engine:300 Fusion Engine
Structure:Standard
Myomer:Standard

Heat Sinks:20 Single
Walk MP:3
Jump MP:0
"""
    
    try:
        from mtf_parser.engine_parser import EngineParser
        import logging
        
        logger = logging.getLogger(__name__)
        engine_parser = EngineParser(logger)
        
        # Test 1: Engine parsing
        engine_data = engine_parser.parse_engine(atlas_engine_sample)
        if engine_data and engine_data.rating == 300 and engine_data.engine_type.value == "Fusion":
            print("✅ Original engine parsing test still passes")
        else:
            print("❌ Original engine parsing test broken by refactor")
            return False
        
        # Test 2: Heat sink parsing  
        heat_sink_data = engine_parser.parse_heat_sinks(atlas_engine_sample)
        if heat_sink_data and heat_sink_data.count == 20 and heat_sink_data.heat_sink_type.value == "Single":
            print("✅ Original heat sink parsing test still passes")
        else:
            print("❌ Original heat sink parsing test broken by refactor")
            return False
        
        # Test 3: Engine validation
        is_valid = engine_parser.validate_engine_rating(100, 300, 3)
        if is_valid:
            print("✅ Original engine validation test still passes")
        else:
            print("❌ Original engine validation test broken by refactor")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Original requirements test failed: {e}")
        return False

def test_enhanced_features():
    """Test the enhanced features added in REFACTOR phase"""
    
    print("\n🚀 ENHANCED FEATURES: Testing refactored improvements...")
    
    test_cases = [
        ("XL Engine", "Engine:350 XL Fusion Engine", 350, "XL Fusion"),
        ("Light Engine", "Engine:280 Light Fusion Engine", 280, "Light Fusion"),
        ("Double Heat Sinks", "Heat Sinks:15 Double", 15, "Double"),
    ]
    
    try:
        from mtf_parser.engine_parser import EngineParser
        import logging
        
        logger = logging.getLogger(__name__)
        engine_parser = EngineParser(logger)
        
        # Test enhanced engine types
        for test_name, content, expected_rating, expected_type in test_cases:
            if "Engine" in test_name:
                engine_data = engine_parser.parse_engine(content)
                if engine_data and engine_data.rating == expected_rating and engine_data.engine_type.value == expected_type:
                    print(f"✅ {test_name}: {engine_data.rating} {engine_data.engine_type.value}")
                else:
                    print(f"❌ {test_name} failed")
                    return False
            else:
                heat_sink_data = engine_parser.parse_heat_sinks(content)
                if heat_sink_data and heat_sink_data.count == expected_rating and heat_sink_data.heat_sink_type.value == expected_type:
                    print(f"✅ {test_name}: {heat_sink_data.count} {heat_sink_data.heat_sink_type.value}")
                else:
                    print(f"❌ {test_name} failed")
                    return False
        
        # Test weight calculations
        engine_content = "Engine:300 Fusion Engine"
        engine_data = engine_parser.parse_engine(engine_content)
        if engine_data and engine_data.weight > 0:
            print(f"✅ Engine weight calculation: {engine_data.weight} tons")
        else:
            print("❌ Engine weight calculation failed")
            return False
        
        # Test heat sink distribution
        hs_content = "Heat Sinks:20 Single"
        heat_sink_data = engine_parser.parse_heat_sinks(hs_content)
        if heat_sink_data and heat_sink_data.engine_heat_sinks == 10 and heat_sink_data.external_heat_sinks == 10:
            print(f"✅ Heat sink distribution: {heat_sink_data.engine_heat_sinks} engine, {heat_sink_data.external_heat_sinks} external")
        else:
            print("❌ Heat sink distribution calculation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
        return False

def test_integration_complete():
    """Test complete integration with main MTF parser"""
    
    print("\n🔗 INTEGRATION: Testing with main MTF parser...")
    
    try:
        from mtf_parser import MTFParser
        
        # Verify engine parser is integrated
        parser = MTFParser()
        if hasattr(parser, 'engine_parser'):
            print("✅ Engine parser integrated with main MTF parser")
        else:
            print("❌ Engine parser not integrated")
            return False
        
        # Test import from package
        from mtf_parser import EngineParser
        engine_parser = EngineParser(None)
        print("✅ EngineParser can be imported from mtf_parser package")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_validation_comprehensive():
    """Test comprehensive validation features"""
    
    print("\n🛡️ VALIDATION: Testing comprehensive validation...")
    
    try:
        from mtf_parser.engine_parser import EngineParser, EngineData, HeatSinkData, EngineType, HeatSinkType
        import logging
        
        logger = logging.getLogger(__name__)
        engine_parser = EngineParser(logger)
        
        # Test edge cases
        test_cases = [
            ("Valid Atlas", 100, 300, 3, True),
            ("Invalid ratio", 50, 300, 3, False),  # 300/50 = 6, not 3
            ("Zero tonnage", 0, 300, 3, False),
            ("Zero engine", 100, 0, 3, False),
        ]
        
        for test_name, tonnage, engine_rating, walk_mp, expected in test_cases:
            result = engine_parser.validate_engine_rating(tonnage, engine_rating, walk_mp)
            if result == expected:
                print(f"✅ {test_name}: {result}")
            else:
                print(f"❌ {test_name}: expected {expected}, got {result}")
                return False
        
        # Test heat sink validation
        engine_data = EngineData(rating=300, engine_type=EngineType.FUSION)
        
        # Test sufficient heat sinks (20 >= 12 minimum for 300 engine)
        heat_sink_data_good = HeatSinkData(count=20, heat_sink_type=HeatSinkType.SINGLE)
        if engine_parser.validate_heat_sinks(heat_sink_data_good, engine_data):
            print("✅ Heat sink validation: sufficient heat sinks")
        else:
            print("❌ Heat sink validation failed for sufficient heat sinks")
            return False
        
        # Test insufficient heat sinks (5 < 12 minimum for 300 engine)
        heat_sink_data_bad = HeatSinkData(count=5, heat_sink_type=HeatSinkType.SINGLE)
        if not engine_parser.validate_heat_sinks(heat_sink_data_bad, engine_data):
            print("✅ Heat sink validation: insufficient heat sinks detected")
        else:
            print("❌ Heat sink validation failed to detect insufficient heat sinks")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def generate_step4_summary():
    """Generate final summary of Step 4 accomplishments"""
    
    print("\n" + "="*60)
    print("🎉 CMB-20 STEP 4: ENGINE PARSER - COMPLETE!")
    print("="*60)
    
    print("\n📋 TDD CYCLE SUCCESSFULLY COMPLETED:")
    print("🔴 RED Phase: ✅ Tests written first, all failing as expected")
    print("🟢 GREEN Phase: ✅ Minimal code written to pass tests")  
    print("🔄 REFACTOR Phase: ✅ Enhanced with production-ready features")
    
    print("\n🎯 FEATURES IMPLEMENTED:")
    print("✅ Engine parsing (Standard, XL, Light, Compact, ICE)")
    print("✅ Heat sink parsing (Single, Double)")
    print("✅ Engine weight calculations")
    print("✅ Heat sink distribution (engine vs external)")
    print("✅ Engine rating validation against movement")
    print("✅ Heat sink count validation against engine requirements")
    print("✅ Comprehensive error handling and logging")
    print("✅ Integration with modular MTF parser")
    
    print("\n📁 FILES CREATED/MODIFIED:")
    print("📄 src/mtf_parser/engine_parser.py - Complete engine parsing module")
    print("📄 tests/test_step4_engine_tdd.py - TDD test suite")
    print("📄 tests/test_step4_complete.py - Final verification tests")
    print("🔧 src/mtf_parser/base_parser.py - Integrated engine parser")
    print("🔧 src/mtf_parser/__init__.py - Added exports")
    
    print("\n🏆 TDD BENEFITS REALIZED:")
    print("✅ Clear requirements from tests")
    print("✅ Fast development cycle")
    print("✅ No over-engineering")
    print("✅ Comprehensive test coverage")
    print("✅ Confidence in refactoring")
    print("✅ Living documentation")
    
    print("\n🚀 READY FOR STEP 5!")
    print("The modular architecture + TDD approach is proving highly effective!")

if __name__ == "__main__":
    print("=== CMB-20 Step 4: Complete TDD Verification ===")
    
    # Run all verification tests
    success = True
    success &= test_original_requirements_still_pass()
    success &= test_enhanced_features() 
    success &= test_integration_complete()
    success &= test_validation_comprehensive()
    
    if success:
        generate_step4_summary()
        print("\n🎊 STEP 4 COMPLETE AND VERIFIED! 🎊")
    else:
        print("\n❌ Step 4 verification failed - need to fix issues")
