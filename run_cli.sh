#!/bin/bash
# Kör CLI-versionen med .env-filen

cd "/Users/tonytopp/mpc undersökning 20250629"
source pdf_env/bin/activate

# Ladda .env
export $(grep -v '^#' .env | xargs)

echo "PDF Analyzer CLI - Claude AI"
echo "============================"
echo ""
echo "Välj en PDF-fil att analysera:"
echo ""

# Visa exempel
echo "Exempel:"
echo "python pdf_analyzer_cli.py"
echo ""
echo "Eller analysera direkt:"
echo "python test_pdf_reader.py din-pdf.pdf"
echo ""

# Starta CLI
python pdf_analyzer_cli.py