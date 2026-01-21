#!/usr/bin/env python3
"""
Validation script for project structure.
"""

import os
import sys
from pathlib import Path


def validate_project_structure():
    """Validate that all required files and directories exist."""
    
    required_files = [
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
        "Makefile",
        ".env.example",
        "computer_use_backend/__init__.py",
        "computer_use_backend/main.py",
        "computer_use_backend/config.py",
        "computer_use_backend/logging_config.py",
        "computer_use_backend/database.py",
        "computer_use_backend/models/__init__.py",
        "computer_use_backend/models/schemas.py",
        "computer_use_backend/services/__init__.py",
        "computer_use_backend/services/session_manager.py",
        "computer_use_backend/services/stream_handler.py",
        "computer_use_backend/routers/__init__.py",
        "computer_use_backend/routers/health.py",
        "computer_use_backend/routers/sessions.py",
        "computer_use_backend/routers/websocket.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_health.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ All required files exist")
    return True


def validate_pyproject_toml():
    """Validate pyproject.toml structure."""
    try:
        import tomllib
    except ImportError:
        # Python < 3.11
        try:
            import tomli as tomllib
        except ImportError:
            print("⚠️  Cannot validate pyproject.toml (tomllib/tomli not available)")
            return True
    
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        
        # Check required sections
        required_sections = ["build-system", "project"]
        for section in required_sections:
            if section not in data:
                print(f"❌ Missing section in pyproject.toml: {section}")
                return False
        
        # Check project metadata
        project = data["project"]
        required_fields = ["name", "version", "dependencies"]
        for field in required_fields:
            if field not in project:
                print(f"❌ Missing field in project section: {field}")
                return False
        
        print("✅ pyproject.toml structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating pyproject.toml: {e}")
        return False


def main():
    """Main validation function."""
    print("🔍 Validating Computer Use Backend project structure...")
    print()
    
    success = True
    
    # Validate file structure
    if not validate_project_structure():
        success = False
    
    # Validate pyproject.toml
    if not validate_pyproject_toml():
        success = False
    
    print()
    if success:
        print("🎉 Project structure validation passed!")
        print()
        print("Next steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Add your Anthropic API key to the .env file")
        print("3. Run 'docker compose up -d' to start the services")
        print("4. Visit http://localhost:8000/docs for API documentation")
        return 0
    else:
        print("💥 Project structure validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())