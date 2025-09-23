#!/usr/bin/env python3
"""
CMB-11: Database configuration helper
Detects and configures database connection settings
"""

import os
import subprocess
import sys

def detect_db_config():
    """Detect database configuration from environment and system"""
    
    # Start with defaults from Makefile
    config = {
        'host': 'localhost',
        'database': os.getenv('DB_NAME', 'cmb_dev'),
        'port': 5432,
        'password': ''
    }
    
    # Try to detect the correct username
    # Common patterns for PostgreSQL on macOS/Linux
    possible_users = [
        os.getenv('PGUSER'),           # PostgreSQL env var
        os.getenv('USER'),             # System username  
        'postgres',                    # Default PostgreSQL user
        'root',                        # Root user
    ]
    
    # Filter out None values
    possible_users = [u for u in possible_users if u]
    
    print("Attempting to detect PostgreSQL configuration...")
    print(f"Target database: {config['database']}")
    
    for user in possible_users:
        test_config = config.copy()
        test_config['user'] = user
        
        print(f"Trying user: {user}")
        
        if test_connection(test_config):
            print(f"✅ Successfully connected as user: {user}")
            return test_config
    
    print("❌ Could not detect working database configuration")
    print("\nPlease check:")
    print("1. PostgreSQL is running")
    print("2. Database 'cmb_dev' exists")
    print("3. Your user has access to the database")
    print("\nTo create the database, try:")
    print("  createdb cmb_dev")
    print("\nOr run migrations:")
    print("  make newdb && make migrate")
    
    return None

def test_connection(config):
    """Test database connection with given config"""
    try:
        import psycopg2
        conn = psycopg2.connect(**config)
        conn.close()
        return True
    except Exception:
        return False

def main():
    """Main function for standalone testing"""
    config = detect_db_config()
    if config:
        print(f"\nDetected configuration:")
        for key, value in config.items():
            if key == 'password' and not value:
                print(f"  {key}: (empty)")
            else:
                print(f"  {key}: {value}")
        return True
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
