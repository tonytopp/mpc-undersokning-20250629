#!/usr/bin/env python3
"""
PDF Analyzer CLI - Command line version
Test PDF analysis without GUI
"""
import os
import sys
import json
from pdf_reader import PDFReader
from claude_analyzer import ClaudeAnalyzer
from google_drive_handler import GoogleDriveHandler

def main():
    print("PDF Analyzer CLI")
    print("=" * 50)
    
    # Check Claude API
    analyzer = ClaudeAnalyzer()
    if analyzer.api_key:
        print("✓ Claude API key configured")
    else:
        print("✗ Claude API key missing!")
        print("  Set with: export ANTHROPIC_API_KEY='your-key'")
    
    # Main menu
    while True:
        print("\nOptions:")
        print("1. Analyze local PDF")
        print("2. Test Claude with sample text")
        print("3. Setup Google Drive (optional)")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ")
        
        if choice == "1":
            analyze_local_pdf(analyzer)
        elif choice == "2":
            test_claude(analyzer)
        elif choice == "3":
            setup_google_drive()
        elif choice == "4":
            break
        else:
            print("Invalid option")

def analyze_local_pdf(analyzer):
    """Analyze a local PDF file"""
    pdf_path = input("Enter PDF path: ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    # Read PDF
    reader = PDFReader()
    print(f"\nReading PDF: {pdf_path}")
    pdf_data = reader.read_pdf(pdf_path)
    
    if pdf_data['status'] != 'success':
        print(f"Error reading PDF: {pdf_data.get('message', 'Unknown error')}")
        return
    
    # Show metadata
    print(f"\nMetadata:")
    print(f"- Pages: {pdf_data['metadata'].get('pages', 'N/A')}")
    print(f"- Title: {pdf_data['metadata'].get('title', 'N/A')}")
    print(f"- Author: {pdf_data['metadata'].get('author', 'N/A')}")
    
    # Show text preview
    text = pdf_data['text']
    print(f"\nText preview (first 500 chars):")
    print("-" * 40)
    print(text[:500] + "..." if len(text) > 500 else text)
    print("-" * 40)
    
    # Analyze with Claude
    if analyzer.api_key:
        analyze = input("\nAnalyze with Claude? (y/n): ")
        if analyze.lower() == 'y':
            print("\nAnalysis types:")
            print("1. Summary")
            print("2. Keywords")
            print("3. Comprehensive")
            print("4. Technical")
            
            type_choice = input("Select type (1-4): ")
            types_map = {
                "1": "summary",
                "2": "keywords", 
                "3": "comprehensive",
                "4": "technical"
            }
            
            analysis_type = types_map.get(type_choice, "comprehensive")
            
            print(f"\nAnalyzing ({analysis_type})...")
            result = analyzer.analyze_text(text, analysis_type)
            
            if result['status'] == 'success':
                print("\n" + "=" * 50)
                print(f"ANALYSIS RESULT ({analysis_type}):")
                print("=" * 50)
                print(result['analysis'])
                
                # Save result
                save = input("\nSave analysis to file? (y/n): ")
                if save.lower() == 'y':
                    output_file = f"analysis_{os.path.basename(pdf_path)}.json"
                    with open(output_file, 'w') as f:
                        json.dump({
                            'pdf_file': pdf_path,
                            'analysis_type': analysis_type,
                            'analysis': result['analysis'],
                            'metadata': pdf_data['metadata']
                        }, f, indent=2)
                    print(f"Saved to: {output_file}")
            else:
                print(f"Analysis failed: {result.get('message', 'Unknown error')}")

def test_claude(analyzer):
    """Test Claude with sample text"""
    if not analyzer.api_key:
        print("Claude API key not configured!")
        return
    
    sample_text = """
    Artificial Intelligence (AI) is rapidly transforming how we work and live. 
    Machine learning algorithms can now perform tasks that previously required 
    human intelligence, from recognizing images to understanding natural language.
    This technological revolution brings both opportunities and challenges for society.
    """
    
    print("\nTesting Claude with sample text...")
    result = analyzer.analyze_text(sample_text, 'summary')
    
    if result['status'] == 'success':
        print("\nAnalysis result:")
        print(result['analysis'])
    else:
        print(f"Test failed: {result.get('message', 'Unknown error')}")

def setup_google_drive():
    """Setup Google Drive connection"""
    print("\nGoogle Drive Setup")
    print("-" * 30)
    
    if not os.path.exists('credentials.json'):
        print("credentials.json not found!")
        print("\nTo get credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Enable Google Drive API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download as credentials.json")
        return
    
    print("Connecting to Google Drive...")
    handler = GoogleDriveHandler()
    
    if handler.service:
        print("✓ Connected successfully!")
        
        # List files
        print("\nFetching PDF files...")
        files = handler.list_pdf_files()
        
        if files:
            print(f"\nFound {len(files)} PDF files:")
            for i, file in enumerate(files[:10]):  # Show first 10
                print(f"{i+1}. {file['name']} (ID: {file['id']})")
        else:
            print("No PDF files found")
    else:
        print("✗ Connection failed")

if __name__ == "__main__":
    main()