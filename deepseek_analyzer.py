#!/usr/bin/env python3
"""
DeepSeek Analyzer
Analyzes PDF content using DeepSeek API
"""
import os
import json
import requests
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekAnalyzer:
    """Analyze PDF content with DeepSeek API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize DeepSeek analyzer"""
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        
        if not self.api_key:
            logger.warning("No DeepSeek API key provided. Set DEEPSEEK_API_KEY environment variable.")
    
    def analyze_text(self, text: str, analysis_type: str = 'comprehensive') -> Dict:
        """
        Analyze text using DeepSeek API
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        if not self.api_key:
            return {'status': 'error', 'message': 'No API key configured'}
        
        # Define analysis prompts
        prompts = {
            'summary': """Please provide a concise summary of the following text. 
                         Focus on the main points and key information.""",
            
            'keywords': """Extract the most important keywords and concepts from this text. 
                          List them in order of importance.""",
            
            'entities': """Identify and list all named entities in this text including:
                          - People names
                          - Organizations
                          - Locations
                          - Dates
                          - Technical terms""",
            
            'comprehensive': """Analyze this text and provide:
                               1. A brief summary (2-3 paragraphs)
                               2. Key topics and themes
                               3. Important entities (people, places, organizations)
                               4. Main conclusions or insights
                               5. Any action items or recommendations mentioned""",
            
            'technical': """Analyze this technical document and identify:
                           1. Technical concepts and terminology
                           2. Technologies mentioned
                           3. Architecture or design patterns
                           4. Best practices discussed
                           5. Potential issues or improvements"""
        }
        
        prompt = prompts.get(analysis_type, prompts['comprehensive'])
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant that analyzes documents.'},
                    {'role': 'user', 'content': f"{prompt}\n\nText to analyze:\n{text[:8000]}"}  # Limit text length
                ],
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                
                return {
                    'status': 'success',
                    'analysis_type': analysis_type,
                    'analysis': analysis,
                    'tokens_used': result.get('usage', {})
                }
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {
                    'status': 'error',
                    'message': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {'status': 'error', 'message': str(e)}
    
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
        prompt = f"""Based on the following text, generate {num_questions} insightful questions 
                    that would help someone better understand the content. 
                    Format as a numbered list."""
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'user', 'content': f"{prompt}\n\nText:\n{text[:6000]}"}
                ],
                'temperature': 0.8,
                'max_tokens': 1000
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                questions = result['choices'][0]['message']['content']
                
                return {
                    'status': 'success',
                    'questions': questions
                }
            else:
                return {'status': 'error', 'message': f'API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def compare_documents(self, text1: str, text2: str) -> Dict:
        """Compare two document texts"""
        prompt = """Compare these two documents and identify:
                   1. Key similarities
                   2. Major differences
                   3. Unique information in each document
                   4. Overall assessment of how they relate"""
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'user', 'content': f"{prompt}\n\nDocument 1:\n{text1[:3000]}\n\nDocument 2:\n{text2[:3000]}"}
                ],
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                comparison = result['choices'][0]['message']['content']
                
                return {
                    'status': 'success',
                    'comparison': comparison
                }
            else:
                return {'status': 'error', 'message': f'API error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error comparing documents: {e}")
            return {'status': 'error', 'message': str(e)}

# Test the module
if __name__ == "__main__":
    analyzer = DeepSeekAnalyzer()
    
    # Test with sample text
    sample_text = """
    Artificial Intelligence (AI) is transforming industries worldwide. 
    Machine learning algorithms are being used to automate tasks, 
    predict outcomes, and improve decision-making processes.
    """
    
    if analyzer.api_key:
        print("Testing DeepSeek analysis...")
        result = analyzer.analyze_text(sample_text, 'summary')
        print(json.dumps(result, indent=2))
    else:
        print("Please set DEEPSEEK_API_KEY to test the analyzer")