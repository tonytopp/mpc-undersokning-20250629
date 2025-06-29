#!/usr/bin/env python3
"""
PDF Reader Module
Handles PDF reading and text extraction
"""
import os
import PyPDF2
import pdfplumber
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFReader:
    """PDF reading and extraction functionality"""
    
    def __init__(self):
        """Initialize PDF reader"""
        self.supported_formats = ['.pdf']
        
    def read_pdf_with_pypdf2(self, file_path: str) -> str:
        """Read PDF using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                    
                return text
        except Exception as e:
            logger.error(f"Error reading PDF with PyPDF2: {e}")
            return ""
    
    def read_pdf_with_pdfplumber(self, file_path: str) -> str:
        """Read PDF using pdfplumber (better for tables)"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
                    # Extract tables if any
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                        text += "\n"
                        
            return text
        except Exception as e:
            logger.error(f"Error reading PDF with pdfplumber: {e}")
            return ""
    
    def extract_metadata(self, file_path: str) -> Dict:
        """Extract PDF metadata"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    'pages': len(pdf_reader.pages),
                    'encrypted': pdf_reader.is_encrypted
                }
                
                if pdf_reader.metadata:
                    info = pdf_reader.metadata
                    metadata.update({
                        'title': info.get('/Title', 'N/A'),
                        'author': info.get('/Author', 'N/A'),
                        'subject': info.get('/Subject', 'N/A'),
                        'creator': info.get('/Creator', 'N/A'),
                        'producer': info.get('/Producer', 'N/A'),
                        'creation_date': str(info.get('/CreationDate', 'N/A')),
                        'modification_date': str(info.get('/ModDate', 'N/A'))
                    })
                    
                return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def read_pdf(self, file_path: str, method: str = 'auto') -> Dict:
        """
        Read PDF file with specified method
        
        Args:
            file_path: Path to PDF file
            method: 'pypdf2', 'pdfplumber', or 'auto'
            
        Returns:
            Dict with text, metadata, and status
        """
        if not os.path.exists(file_path):
            return {'status': 'error', 'message': 'File not found'}
            
        result = {
            'status': 'success',
            'file_path': file_path,
            'text': '',
            'metadata': {},
            'method_used': method
        }
        
        # Extract metadata
        result['metadata'] = self.extract_metadata(file_path)
        
        # Extract text
        if method == 'pypdf2':
            result['text'] = self.read_pdf_with_pypdf2(file_path)
        elif method == 'pdfplumber':
            result['text'] = self.read_pdf_with_pdfplumber(file_path)
        else:  # auto
            # Try pdfplumber first (better for complex PDFs)
            text = self.read_pdf_with_pdfplumber(file_path)
            if text.strip():
                result['text'] = text
                result['method_used'] = 'pdfplumber'
            else:
                # Fallback to PyPDF2
                result['text'] = self.read_pdf_with_pypdf2(file_path)
                result['method_used'] = 'pypdf2'
                
        if not result['text'].strip():
            result['status'] = 'warning'
            result['message'] = 'No text extracted from PDF'
            
        return result
    
    def batch_read(self, file_paths: List[str]) -> List[Dict]:
        """Read multiple PDF files"""
        results = []
        for file_path in file_paths:
            logger.info(f"Reading: {file_path}")
            results.append(self.read_pdf(file_path))
        return results

# Test the module
if __name__ == "__main__":
    reader = PDFReader()
    
    # Test with a sample PDF if available
    test_pdf = "test.pdf"
    if os.path.exists(test_pdf):
        result = reader.read_pdf(test_pdf)
        print(f"Status: {result['status']}")
        print(f"Method used: {result['method_used']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Text preview: {result['text'][:500]}...")
    else:
        print("No test.pdf found. Create one to test the reader.")