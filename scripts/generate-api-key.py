#!/usr/bin/env python3
"""Generate secure API keys for production use."""

import secrets
import sys


def generate_api_key(length: int = 32) -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(length)


def generate_secret_key(length: int = 64) -> str:
    """Generate a secure secret key."""
    return secrets.token_urlsafe(length)


def main():
    """Generate and display API keys."""
    print("=" * 80)
    print("Tesseract SaaS MVP - Secure Key Generator")
    print("=" * 80)
    print()

    # Generate secret key
    secret_key = generate_secret_key()
    print("🔐 Application Secret Key (use for SECRET_KEY):")
    print(f"   {secret_key}")
    print()

    # Generate API keys
    num_keys = 3 if len(sys.argv) < 2 else int(sys.argv[1])
    print(f"🔑 API Keys (generate {num_keys} keys for API_KEYS):")
    api_keys = []
    for i in range(num_keys):
        key = generate_api_key()
        api_keys.append(key)
        print(f"   {i+1}. {key}")
    print()

    print("📋 Environment Variable Format:")
    print(f"   SECRET_KEY={secret_key}")
    print(f"   API_KEYS={','.join(api_keys)}")
    print()

    print("⚠️  IMPORTANT:")
    print("   - Store these keys securely (use a password manager)")
    print("   - Never commit these keys to git")
    print("   - Rotate keys regularly (every 90 days recommended)")
    print("   - Use different keys for staging and production")
    print()

    print("💡 Database Password Generator:")
    db_password = secrets.token_urlsafe(24)
    print(f"   POSTGRES_PASSWORD={db_password}")
    print()


if __name__ == "__main__":
    main()
