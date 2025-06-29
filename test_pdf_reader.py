#!/usr/bin/env python3
"""
Test PDF Reader - No AI needed
"""
from pdf_reader import PDFReader
import sys

if len(sys.argv) < 2:
    print("Usage: python test_pdf_reader.py <pdf_file>")
    print("\nExample: python test_pdf_reader.py document.pdf")
    sys.exit(1)

pdf_file = sys.argv[1]
reader = PDFReader()

print(f"Reading: {pdf_file}")
print("-" * 50)

result = reader.read_pdf(pdf_file)

if result['status'] == 'success':
    print(f"✓ Success using {result['method_used']}")
    print(f"\nMetadata:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")
    
    print(f"\nText (first 1000 chars):")
    print("-" * 50)
    text = result['text']
    print(text[:1000] + "..." if len(text) > 1000 else text)
    
    print(f"\n\nTotal characters: {len(text)}")
else:
    print(f"✗ Error: {result.get('message', 'Failed to read PDF')}")