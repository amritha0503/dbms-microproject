#!/usr/bin/env python3
"""
Flask Secret Key Generator
Run this script to generate secure secret keys for Flask applications
"""

import secrets
import string

def generate_secret_key(length=64):
    """Generate a cryptographically secure random secret key"""
    return secrets.token_hex(length // 2)

def generate_password(length=16):
    """Generate a strong password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print("🔐 Flask Security Key Generator")
    print("=" * 40)
    
    # Generate different types of keys
    print("\n📋 Generated Keys:")
    print(f"Flask Secret Key (64 chars): {generate_secret_key(64)}")
    print(f"Flask Secret Key (32 chars): {generate_secret_key(32)}")
    print(f"Strong Password (16 chars):  {generate_password(16)}")
    print(f"Strong Password (24 chars):  {generate_password(24)}")
    
    print("\n⚠️  Important Security Notes:")
    print("- Never share these keys publicly")
    print("- Use different keys for development/production")
    print("- Store in environment variables, not in code")
    print("- Regenerate if compromised")
    
    print("\n📝 Usage in .env file:")
    print(f"FLASK_SECRET_KEY={generate_secret_key(64)}")
    print(f"DB_PASSWORD={generate_password(16)}")