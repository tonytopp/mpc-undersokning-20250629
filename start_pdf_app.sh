#!/bin/bash
# Startskript för PDF Analyzer med API-nyckel

# Sätt din Anthropic API-nyckel här:
export ANTHROPIC_API_KEY="sk-ant-din-nyckel-här"

# Gå till rätt mapp
cd "/Users/tonytopp/mpc undersökning 20250629"

# Aktivera virtual environment
source pdf_env/bin/activate

# Starta appen
echo "Starting PDF Analyzer with Claude AI..."
python pdf_analyzer_app.py