#!/usr/bin/env python3
"""
Claude Code Analyzer
Analyzes PDF content using Claude Code directly (no API needed)
This version simulates analysis without external dependencies
"""
import os
import json
from typing import Dict, List, Optional
import logging
import re
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeCodeAnalyzer:
    """Analyze PDF content locally without API"""
    
    def __init__(self):
        """Initialize analyzer"""
        logger.info("Claude Code Analyzer initialized (local processing)")
    
    def analyze_text(self, text: str, analysis_type: str = 'comprehensive') -> Dict:
        """
        Analyze text locally without API calls
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        try:
            if analysis_type == 'summary':
                analysis = self._generate_summary(text)
            elif analysis_type == 'keywords':
                analysis = self._extract_keywords(text)
            elif analysis_type == 'entities':
                analysis = self._extract_entities(text)
            elif analysis_type == 'technical':
                analysis = self._technical_analysis(text)
            else:  # comprehensive
                analysis = self._comprehensive_analysis(text)
            
            return {
                'status': 'success',
                'analysis_type': analysis_type,
                'analysis': analysis,
                'model': 'local-analyzer'
            }
                
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_summary(self, text: str) -> str:
        """Generate a basic summary"""
        sentences = text.split('.')[:10]  # First 10 sentences
        word_count = len(text.split())
        
        return f"""Document Summary:
        
This document contains approximately {word_count} words.

Key sentences:
{'. '.join(sentences[:3])}.

The document appears to discuss various topics related to the content provided."""

    def _extract_keywords(self, text: str) -> str:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_freq = Counter(words)
        
        # Filter common words
        common_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'more'}
        keywords = [(word, count) for word, count in word_freq.most_common(20) 
                   if word not in common_words]
        
        keyword_list = '\n'.join([f"- {word} ({count} occurrences)" for word, count in keywords[:10]])
        
        return f"""Keywords extracted:

{keyword_list}

These keywords represent the most frequently used terms in the document."""

    def _extract_entities(self, text: str) -> str:
        """Extract named entities"""
        # Simple pattern matching for entities
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        
        emails = re.findall(email_pattern, text)
        urls = re.findall(url_pattern, text)
        dates = re.findall(date_pattern, text)
        
        # Capital words (potential names/organizations)
        capital_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        potential_names = list(set([w for w in capital_words if len(w.split()) <= 3]))[:10]
        
        return f"""Entities found:

Emails: {', '.join(emails) if emails else 'None found'}
URLs: {', '.join(urls[:3]) if urls else 'None found'}
Dates: {', '.join(dates[:5]) if dates else 'None found'}
Potential names/organizations: {', '.join(potential_names[:10]) if potential_names else 'None found'}"""

    def _technical_analysis(self, text: str) -> str:
        """Perform technical analysis"""
        # Look for technical indicators
        code_indicators = ['function', 'class', 'import', 'def', 'var', 'const', 'return']
        tech_terms = ['API', 'database', 'server', 'client', 'algorithm', 'framework']
        
        found_indicators = [term for term in code_indicators if term.lower() in text.lower()]
        found_tech = [term for term in tech_terms if term.lower() in text.lower()]
        
        return f"""Technical Analysis:

Programming indicators found: {', '.join(found_indicators) if found_indicators else 'None'}
Technical terms found: {', '.join(found_tech) if found_tech else 'None'}

Document type: {'Technical documentation' if found_indicators or found_tech else 'Non-technical document'}"""

    def _comprehensive_analysis(self, text: str) -> str:
        """Perform comprehensive analysis"""
        summary = self._generate_summary(text)
        keywords = self._extract_keywords(text)
        entities = self._extract_entities(text)
        
        return f"""Comprehensive Analysis:

{summary}

{keywords}

{entities}

This analysis was performed locally without external API calls."""
    
    def analyze_pdf_content(self, pdf_data: Dict, analysis_types: List[str] = None) -> Dict:
        """
        Analyze PDF content with multiple analysis types
        
        Args:
            pdf_data: Dict from PDFReader with 'text' key
            analysis_types: List of analysis types to perform
            
        Returns:
            Combined analysis results
        """
        if not pdf_data.get('text'):
            return {'status': 'error', 'message': 'No text content to analyze'}
        
        if not analysis_types:
            analysis_types = ['comprehensive']
        
        results = {
            'status': 'success',
            'file_path': pdf_data.get('file_path'),
            'analyses': {}
        }
        
        for analysis_type in analysis_types:
            logger.info(f"Performing {analysis_type} analysis...")
            result = self.analyze_text(pdf_data['text'], analysis_type)
            results['analyses'][analysis_type] = result
        
        return results
    
    def generate_questions(self, text: str, num_questions: int = 5) -> Dict:
        """Generate questions about the document content"""
        try:
            # Extract key topics
            keywords = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
            word_freq = Counter(keywords)
            top_words = [word for word, _ in word_freq.most_common(10)]
            
            questions = [
                f"1. What is the main topic discussed regarding '{top_words[0] if top_words else 'this document'}'?",
                f"2. How does '{top_words[1] if len(top_words) > 1 else 'the content'}' relate to the overall document?",
                f"3. What are the key points mentioned about '{top_words[2] if len(top_words) > 2 else 'the subject'}'?",
                "4. What conclusions can be drawn from this document?",
                "5. How might this information be applied in practice?"
            ]
            
            return {
                'status': 'success',
                'questions': '\n'.join(questions[:num_questions])
            }
                
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def compare_documents(self, text1: str, text2: str) -> Dict:
        """Compare two document texts"""
        try:
            # Extract keywords from both
            words1 = set(re.findall(r'\b[a-zA-Z]{4,}\b', text1.lower()))
            words2 = set(re.findall(r'\b[a-zA-Z]{4,}\b', text2.lower()))
            
            common = words1.intersection(words2)
            unique1 = words1 - words2
            unique2 = words2 - words1
            
            comparison = f"""Document Comparison:

1. Key similarities:
   - Common keywords: {len(common)} words
   - Shared topics: {', '.join(list(common)[:10])}

2. Major differences:
   - Document 1 has {len(unique1)} unique words
   - Document 2 has {len(unique2)} unique words

3. Unique information:
   - Document 1 unique terms: {', '.join(list(unique1)[:5])}
   - Document 2 unique terms: {', '.join(list(unique2)[:5])}

4. Overall assessment:
   - The documents share {(len(common) / (len(words1) + len(words2) - len(common)) * 100):.1f}% similarity"""
            
            return {
                'status': 'success',
                'comparison': comparison
            }
                
        except Exception as e:
            logger.error(f"Error comparing documents: {e}")
            return {'status': 'error', 'message': str(e)}

# Test the module
if __name__ == "__main__":
    analyzer = ClaudeCodeAnalyzer()
    
    # Test with sample text
    sample_text = """
    Artificial Intelligence (AI) is transforming industries worldwide. 
    Machine learning algorithms are being used to automate tasks, 
    predict outcomes, and improve decision-making processes.
    """
    
    print("Testing Claude Code analysis...")
    result = analyzer.analyze_text(sample_text, 'summary')
    print(json.dumps(result, indent=2))