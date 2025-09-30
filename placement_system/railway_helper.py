#!/usr/bin/env python3
"""
Railway Connection Helper
This script will help you format your Railway connection details correctly
"""

def format_railway_connection():
    print("🚂 Railway Connection Setup Helper")
    print("=" * 50)
    
    print("\n📋 From your Railway MySQL service 'Variables' tab, copy these values:")
    print("(Go to Variables tab in your MySQL service)")
    print()
    
    # Get user input for each variable
    mysql_host = input("MYSQL_HOST: ").strip()
    mysql_user = input("MYSQL_USER (usually 'root'): ").strip() or "root"
    mysql_password = input("MYSQL_PASSWORD: ").strip()
    mysql_port = input("MYSQL_PORT (usually 3306): ").strip() or "3306"
    mysql_database = input("MYSQL_DATABASE (usually 'railway'): ").strip() or "railway"
    
    print("\n✅ Creating your .env configuration...")
    
    env_content = f"""# Database Configuration - Railway Cloud Database
DB_HOST={mysql_host}
DB_USER={mysql_user}
DB_PASSWORD={mysql_password}
DB_NAME={mysql_database}
DB_PORT={mysql_port}

# Flask Configuration
FLASK_SECRET_KEY=eee1fe1958d624f95d4e89b383ef3c2238f54ce8f0409d85ba7b192c9632e078
FLASK_ENV=production
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file updated!")
    print("\n📋 Your configuration:")
    print(f"Host: {mysql_host}")
    print(f"User: {mysql_user}")
    print(f"Database: {mysql_database}")
    print(f"Port: {mysql_port}")
    
    print("\n🧪 Next steps:")
    print("1. python test_cloud_connection.py")
    print("2. python setup_cloud_db.py")
    
    return True

if __name__ == "__main__":
    try:
        format_railway_connection()
    except KeyboardInterrupt:
        print("\n❌ Cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")