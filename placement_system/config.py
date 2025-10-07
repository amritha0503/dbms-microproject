import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration for production
DATABASE_CONFIG = { # Using os.getenv with no default for sensitive info is safer
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'), # No default for password
    'database': os.getenv('DB_NAME', 'placement_db'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'autocommit': True,
    'charset': 'utf8mb4',
    'use_unicode': True
}