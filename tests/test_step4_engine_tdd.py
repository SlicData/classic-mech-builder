#!/usr/bin/env python3
"""
Test CMB-20 Step 4: Engine and Heat Sink Parsing - TDD Approach
Write the test FIRST, then make it pass
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_engine_parser_exists():
    """Test that engine parser module can be imported"""
    try:
        from mtf_parser.engine_parser import EngineParser
        print("✅ EngineParser class imported successfully")
        return True
    except ImportError:
        print("❌ EngineParser class not found - need to create it")
        return False

def test_engine_parsing():
    """Test engine parsing functionality - this should fail initially"""
    
    # Sample MTF content with engine data
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
        
        # Test engine parsing - should return engine data
        engine_data = engine_parser.parse_engine(atlas_engine_sample)
        
        # Expected results
        expected_rating = 300
        expected_type = "Fusion"
        
        if engine_data:
            print(f"✅ Engine parsed: {engine_data}")
            
            # Validate engine rating
            if hasattr(engine_data, 'rating') and engine_data.rating == expected_rating:
                print(f"✅ Engine rating correct: {engine_data.rating}")
            else:
                print(f"❌ Engine rating incorrect: expected {expected_rating}")
                return False
                
            # Validate engine type
            if hasattr(engine_data, 'engine_type') and engine_data.engine_type == expected_type:
                print(f"✅ Engine type correct: {engine_data.engine_type}")
            else:
                print(f"❌ Engine type incorrect: expected {expected_type}")
                return False
                
            return True
        else:
            print("❌ No engine data returned")
            return False
            
    except Exception as e:
        print(f"❌ Engine parsing test failed: {e}")
        return False

def test_heat_sink_parsing():
    """Test heat sink parsing functionality - this should fail initially"""
    
    atlas_sample = """
Heat Sinks:20 Single
"""
    
    try:
        from mtf_parser.engine_parser import EngineParser
        import logging
        
        logger = logging.getLogger(__name__)
        engine_parser = EngineParser(logger)
        
        # Test heat sink parsing
        heat_sink_data = engine_parser.parse_heat_sinks(atlas_sample)
        
        expected_count = 20
        expected_type = "Single"
        
        if heat_sink_data:
            print(f"✅ Heat sinks parsed: {heat_sink_data}")
            
            # Validate count
            if hasattr(heat_sink_data, 'count') and heat_sink_data.count == expected_count:
                print(f"✅ Heat sink count correct: {heat_sink_data.count}")
            else:
                print(f"❌ Heat sink count incorrect: expected {expected_count}")
                return False
                
            # Validate type
            if hasattr(heat_sink_data, 'heat_sink_type') and heat_sink_data.heat_sink_type == expected_type:
                print(f"✅ Heat sink type correct: {heat_sink_data.heat_sink_type}")
            else:
                print(f"❌ Heat sink type incorrect: expected {expected_type}")
                return False
                
            return True
        else:
            print("❌ No heat sink data returned")
            return False
            
    except Exception as e:
        print(f"❌ Heat sink parsing test failed: {e}")
        return False

def test_engine_validation():
    """Test engine validation against movement - this should fail initially"""
    
    try:
        from mtf_parser.engine_parser import EngineParser
        import logging
        
        logger = logging.getLogger(__name__)
        engine_parser = EngineParser(logger)
        
        # Test validation logic
        # Atlas: 100 tons, 300 engine, 3 walk MP
        is_valid = engine_parser.validate_engine_rating(
            tonnage=100, 
            engine_rating=300, 
            walk_mp=3
        )
        
        if is_valid:
            print("✅ Engine validation working")
            return True
        else:
            print("❌ Engine validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Engine validation test failed: {e}")
        return False

def test_integration_with_main_parser():
    """Test that engine parser integrates with main MTF parser"""
    
    try:
        from mtf_parser import MTFParser
        
        parser = MTFParser()
        
        if hasattr(parser, 'engine_parser'):
            print("✅ Engine parser integrated with main MTF parser")
            return True
        else:
            print("❌ Engine parser not integrated with main parser")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== TDD Step 4: Engine and Heat Sink Parsing ===")
    print("🔴 RED PHASE: Running tests that should fail\n")
    
    test_results = []
    
    print("1. Testing EngineParser import...")
    test_results.append(test_engine_parser_exists())
    
    print("\n2. Testing engine parsing...")
    test_results.append(test_engine_parsing())
    
    print("\n3. Testing heat sink parsing...")
    test_results.append(test_heat_sink_parsing())
    
    print("\n4. Testing engine validation...")
    test_results.append(test_engine_validation())
    
    print("\n5. Testing integration...")
    test_results.append(test_integration_with_main_parser())
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n=== TDD RED PHASE RESULTS ===")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == 0:
        print("🔴 PERFECT! All tests failing as expected in RED phase")
        print("✅ Ready to write minimum code to make tests pass (GREEN phase)")
    elif passed < total:
        print("🟡 Some tests passing, some failing - good for TDD")
        print("✅ Ready to implement missing functionality")
    else:
        print("🟢 All tests passing - either we already have the code or tests are wrong")
    
    print("\nNext: Implement EngineParser to make these tests pass! 🚀")
