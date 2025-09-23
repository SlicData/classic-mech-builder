# CMB-11: Database Configuration
# Copy this file to config.py and update with your database settings

DB_CONFIG = {
    'host': 'localhost',
    'database': 'cmb_dev',  # Change to your database name
    'user': 'postgres',     # Change to your username
    'password': '',         # Add your password
    'port': 5432
}

# Performance test thresholds (in milliseconds)
PERFORMANCE_THRESHOLDS = {
    'simple_query': 50,      # Simple single-table queries
    'complex_query': 200,    # Complex multi-table joins
    'aggregation': 100,      # Aggregation queries
    'search': 150           # Text search queries
}

# Test data expectations
TEST_EXPECTATIONS = {
    'min_total_mechs': 1000,        # Minimum mechs in database
    'min_weapon_types': 50,         # Minimum weapon types
    'min_equipment_types': 20,      # Minimum equipment types
    'expected_locations': 8,        # CT, HD, LA, RA, LT, RT, LL, RL
}
