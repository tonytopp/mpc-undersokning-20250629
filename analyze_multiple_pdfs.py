#!/usr/bin/env python3
"""
Analysera och sortera flera PDF-filer
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import glob

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

def analyze_and_categorize_pdfs(pdf_paths):
    """Analysera och kategorisera flera PDFer"""
    reader = PDFReader()
    analyzer = ClaudeAnalyzer()
    
    results = {
        'invoices': [],
        'technical_docs': [],
        'product_info': [],
        'other': [],
        'errors': []
    }
    
    print(f"Analyserar {len(pdf_paths)} PDF-filer...")
    print("=" * 60)
    
    for i, pdf_path in enumerate(pdf_paths, 1):
        print(f"\n[{i}/{len(pdf_paths)}] {os.path.basename(pdf_path)}")
        
        try:
            # Läs PDF
            pdf_data = reader.read_pdf(pdf_path)
            if pdf_data['status'] != 'success':
                results['errors'].append({
                    'file': pdf_path,
                    'error': pdf_data.get('message', 'Kunde inte läsa PDF')
                })
                continue
            
            # Analysera för kategorisering
            categorize_prompt = """Analyze this document and categorize it as one of:
            - invoice (faktura, bill, invoice)
            - technical_doc (technical specifications, manual, datasheet)
            - product_info (product catalog, brochure)
            - other
            
            Respond with ONLY the category name."""
            
            cat_result = analyzer.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": f"{categorize_prompt}\n\nDocument text:\n{pdf_data['text'][:2000]}"
                }]
            )
            
            category = cat_result.content[0].text.strip().lower()
            
            # Få sammanfattning
            summary_result = analyzer.analyze_text(pdf_data['text'][:3000], 'summary')
            
            doc_info = {
                'file': os.path.basename(pdf_path),
                'path': pdf_path,
                'pages': pdf_data['metadata'].get('pages', 'N/A'),
                'category': category,
                'summary': summary_result['analysis'] if summary_result['status'] == 'success' else 'N/A'
            }
            
            # Sortera baserat på kategori
            if 'invoice' in category or 'faktura' in pdf_data['text'].lower():
                results['invoices'].append(doc_info)
                print("  → Kategoriserad som: FAKTURA")
            elif 'technical' in category or any(word in pdf_data['text'].lower() for word in ['design', 'engineering', 'specification']):
                results['technical_docs'].append(doc_info)
                print("  → Kategoriserad som: TEKNISK DOKUMENTATION")
            elif 'product' in category:
                results['product_info'].append(doc_info)
                print("  → Kategoriserad som: PRODUKTINFORMATION")
            else:
                results['other'].append(doc_info)
                print("  → Kategoriserad som: ÖVRIGT")
                
        except Exception as e:
            results['errors'].append({
                'file': pdf_path,
                'error': str(e)
            })
            print(f"  → FEL: {str(e)}")
    
    return results

def print_results(results):
    """Skriv ut resultat snyggt formaterat"""
    print("\n" + "=" * 60)
    print("RESULTAT - SORTERADE DOKUMENT")
    print("=" * 60)
    
    # Fakturor
    if results['invoices']:
        print(f"\n📄 FAKTUROR ({len(results['invoices'])} st)")
        print("-" * 40)
        for doc in results['invoices']:
            print(f"• {doc['file']} ({doc['pages']} sidor)")
            print(f"  Sammanfattning: {doc['summary'][:150]}...")
    
    # Tekniska dokument
    if results['technical_docs']:
        print(f"\n🔧 TEKNISKA DOKUMENT ({len(results['technical_docs'])} st)")
        print("-" * 40)
        for doc in results['technical_docs']:
            print(f"• {doc['file']} ({doc['pages']} sidor)")
            print(f"  Sammanfattning: {doc['summary'][:150]}...")
    
    # Produktinfo
    if results['product_info']:
        print(f"\n📦 PRODUKTINFORMATION ({len(results['product_info'])} st)")
        print("-" * 40)
        for doc in results['product_info']:
            print(f"• {doc['file']} ({doc['pages']} sidor)")
            print(f"  Sammanfattning: {doc['summary'][:150]}...")
    
    # Övrigt
    if results['other']:
        print(f"\n📁 ÖVRIGT ({len(results['other'])} st)")
        print("-" * 40)
        for doc in results['other']:
            print(f"• {doc['file']} ({doc['pages']} sidor)")
    
    # Fel
    if results['errors']:
        print(f"\n❌ FEL ({len(results['errors'])} st)")
        print("-" * 40)
        for err in results['errors']:
            print(f"• {os.path.basename(err['file'])}: {err['error']}")
    
    # Spara resultat
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"pdf_analysis_results_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultat sparat i: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Användning:")
        print("  python analyze_multiple_pdfs.py <pdf1> <pdf2> ...")
        print("  python analyze_multiple_pdfs.py /path/to/folder/*.pdf")
        print("\nExempel:")
        print("  python analyze_multiple_pdfs.py ~/Downloads/*.pdf")
    else:
        # Samla alla PDF-filer
        pdf_files = []
        for arg in sys.argv[1:]:
            if '*' in arg:
                # Glob pattern
                pdf_files.extend(glob.glob(arg))
            elif os.path.isfile(arg) and arg.lower().endswith('.pdf'):
                pdf_files.append(arg)
        
        if pdf_files:
            results = analyze_and_categorize_pdfs(pdf_files)
            print_results(results)
        else:
            print("Inga PDF-filer hittades!")