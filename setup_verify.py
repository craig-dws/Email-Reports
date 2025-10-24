"""
Setup Verification Script
Run this to verify your Email Reports system is properly configured.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")

    required_packages = [
        'google-api-python-client',
        'google-auth-oauthlib',
        'pdfplumber',
        'jinja2',
        'rapidfuzz',
        'premailer',
        'python-dotenv'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (MISSING)")
            missing.append(package)

    if missing:
        print(f"\n  Install missing packages: venv\\Scripts\\pip install {' '.join(missing)}")
        return False

    return True


def check_directory_structure():
    """Check if required directories exist."""
    print("\nChecking directory structure...")

    required_dirs = [
        'data',
        'data/pdfs',
        'data/archive',
        'logs',
        'templates',
        'config',
        'src',
        'venv'
    ]

    all_exist = True
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (MISSING)")
            all_exist = False

    return all_exist


def check_config_files():
    """Check if configuration files exist."""
    print("\nChecking configuration files...")

    files = {
        '.env': 'Configuration file (REQUIRED)',
        'credentials.json': 'Gmail OAuth credentials (REQUIRED for Gmail access)',
        'data/clients.csv': 'Client database (REQUIRED)',
        'templates/email_template.html': 'Email template (REQUIRED)',
    }

    all_exist = True
    for file_path, description in files.items():
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} ({description}) - MISSING")
            all_exist = False

    return all_exist


def check_env_configuration():
    """Check .env file configuration."""
    print("\nChecking .env configuration...")

    env_path = Path('.env')
    if not env_path.exists():
        print("  ✗ .env file not found")
        print("    Copy .env.example to .env and configure it")
        return False

    required_vars = [
        'GMAIL_SENDER_EMAIL',
        'LOOKER_STUDIO_SENDER',
        'CLIENT_DATABASE_PATH',
        'PDF_STORAGE_PATH',
        'TEMPLATE_PATH',
        'AGENCY_NAME',
        'AGENCY_EMAIL'
    ]

    # Read .env file
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    all_configured = True
    for var in required_vars:
        if var in env_vars and env_vars[var] and not env_vars[var].startswith('your-'):
            print(f"  ✓ {var}")
        else:
            print(f"  ✗ {var} (Not configured or using default value)")
            all_configured = False

    return all_configured


def main():
    """Run all verification checks."""
    print("="*60)
    print("EMAIL REPORTS AUTOMATION SYSTEM - SETUP VERIFICATION")
    print("="*60)

    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Directory Structure': check_directory_structure(),
        'Configuration Files': check_config_files(),
        'Environment Configuration': check_env_configuration()
    }

    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    all_passed = True
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check:.<40} {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✓ ALL CHECKS PASSED - System is ready to use!")
        print("\nNext steps:")
        print("1. Set up Gmail OAuth credentials (see README - Step 5)")
        print("2. Add clients to data/clients.csv")
        print("3. Run: venv\\Scripts\\python main.py --full")
    else:
        print("\n✗ SETUP INCOMPLETE - Please fix the issues above")
        print("\nSee README.md for detailed setup instructions")

    print()


if __name__ == '__main__':
    main()
