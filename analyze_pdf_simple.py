#!/usr/bin/env python3
"""
Enkel PDF-analysator med Claude AI
"""
import sys
import os
from pathlib import Path

# Ladda .env
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if 'ANTHROPIC_API_KEY' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from pdf_reader import PDFReader
from claude_analyzer import ClaudeAnalyzer

def analyze_pdf(pdf_path: str):
    """Analysera en PDF-fil"""
    print(f"\nLäser PDF: {pdf_path}")
    print("=" * 60)
    
    # Läs PDF
    reader = PDFReader()
    pdf_data = reader.read_pdf(pdf_path)
    
    if pdf_data['status'] != 'success':
        print(f"❌ Kunde inte läsa PDF: {pdf_data.get('message')}")
        return
    
    # Visa info
    print(f"✓ PDF inläst med {pdf_data['method_used']}")
    print(f"Sidor: {pdf_data['metadata'].get('pages', 'N/A')}")
    print(f"Titel: {pdf_data['metadata'].get('title', 'N/A')}")
    print(f"Författare: {pdf_data['metadata'].get('author', 'N/A')}")
    print(f"Text längd: {len(pdf_data['text'])} tecken")
    
    # Textförhandsvisning
    print("\nTextförhandsvisning:")
    print("-" * 60)
    preview = pdf_data['text'][:500]
    print(preview + "..." if len(pdf_data['text']) > 500 else preview)
    print("-" * 60)
    
    # Analysera med Claude
    analyzer = ClaudeAnalyzer()
    if not analyzer.api_key:
        print("\n❌ Ingen API-nyckel konfigurerad!")
        return
    
    print("\nAnalyserar med Claude AI...")
    
    # Sammanfattning
    result = analyzer.analyze_text(pdf_data['text'], 'summary')
    if result['status'] == 'success':
        print("\n📄 SAMMANFATTNING:")
        print("=" * 60)
        print(result['analysis'])
        print(f"\n(Tokens: {result['usage']['input_tokens']} in, {result['usage']['output_tokens']} ut)")
    
    # Nyckelord
    print("\nExtraherar nyckelord...")
    keywords_result = analyzer.analyze_text(pdf_data['text'], 'keywords')
    if keywords_result['status'] == 'success':
        print("\n🔑 NYCKELORD:")
        print("=" * 60)
        print(keywords_result['analysis'])
    
    print("\n✅ Analys klar!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Användning: python analyze_pdf_simple.py <pdf-fil>")
        print("\nExempel PDFer att testa:")
        print("- rapport.pdf")
        print("- dokument.pdf")
        print("- /Users/din-mapp/fil.pdf")
    else:
        pdf_path = sys.argv[1]
        if os.path.exists(pdf_path):
            analyze_pdf(pdf_path)
        else:
            print(f"❌ Filen finns inte: {pdf_path}")