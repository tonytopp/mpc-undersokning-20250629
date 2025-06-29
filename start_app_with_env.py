#!/usr/bin/env python3
"""
Start PDF Analyzer with environment variables from .env file
"""
import os
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                if key == 'ANTHROPIC_API_KEY':
                    print(f"✓ Loaded {key}")

# Import and run the app
from pdf_analyzer_app import main
main()