#!/usr/bin/env python3
"""
Database Setup Script for Cloud Deployment
Run this script to set up your database on cloud platforms like PlanetScale or Railway
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_cloud_database():
    """Set up database tables in cloud database"""
    
    # Database connection config from environment
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'), 
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'autocommit': True
    }
    
    print("Connecting to cloud database...")
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ Connected successfully!")
        
        # Read and execute SQL setup file
        with open('database_setup.sql', 'r') as sql_file:
            sql_content = sql_file.read()
            
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except mysql.connector.Error as err:
                    print(f"⚠️  Warning: {err}")
                    
        print("✅ Database setup completed!")
        
        # Test connection by showing tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📋 Created tables: {[table[0] for table in tables]}")
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return False
    except FileNotFoundError:
        print("❌ database_setup.sql file not found!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Database connection closed.")
    
    return True

if __name__ == "__main__":
    print("🚀 Cloud Database Setup Script")
    print("=" * 40)
    
    # Check if environment variables are set
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set them in your .env file or environment")
        exit(1)
    
    print(f"Database: {os.getenv('DB_NAME')} at {os.getenv('DB_HOST')}")
    
    confirm = input("\n⚠️  This will create/modify database tables. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        exit(0)
    
    if setup_cloud_database():
        print("\n🎉 Setup completed successfully!")
        print("Your database is ready for deployment!")
    else:
        print("\n💥 Setup failed. Please check your configuration.")
        exit(1)