#!/usr/bin/env python3
"""
PDF Analyzer Terminal Interface
Interactive terminal UI with integrated command capabilities
"""
import os
import sys
import json
import subprocess
import readline
from datetime import datetime
from pathlib import Path
import glob
import shutil

# Import our modules
from pdf_reader import PDFReader
from claude_code_analyzer import ClaudeCodeAnalyzer
from google_drive_handler import GoogleDriveHandler
from google_sheets_writer import GoogleSheetsWriter

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class PDFAnalyzerTerminal:
    def __init__(self):
        self.reader = PDFReader()
        self.analyzer = ClaudeCodeAnalyzer()
        self.drive_handler = None
        self.sheets_writer = None
        self.history = []
        self.current_pdf = None
        self.analysis_results = {}
        
        # Setup readline for command history
        self.setup_readline()
        
    def setup_readline(self):
        """Setup readline for better command line experience"""
        # Enable tab completion
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)
        
        # Load history if exists
        self.history_file = Path.home() / '.pdf_analyzer_history'
        if self.history_file.exists():
            readline.read_history_file(self.history_file)
    
    def completer(self, text, state):
        """Tab completion for commands"""
        commands = ['analyze', 'open', 'list', 'summary', 'keywords', 'entities', 
                   'technical', 'comprehensive', 'compare', 'save', 'export',
                   'google', 'sheets', 'clear', 'help', 'exit', 'shell']
        
        # Add PDF files
        pdf_files = glob.glob("*.pdf")
        commands.extend(pdf_files)
        
        matches = [cmd for cmd in commands if cmd.startswith(text)]
        return matches[state] if state < len(matches) else None
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print application header"""
        self.clear_screen()
        width = shutil.get_terminal_size().columns
        print(Colors.HEADER + "="*width)
        print(" PDF ANALYZER TERMINAL ".center(width))
        print("="*width + Colors.ENDC)
        print()
    
    def print_status(self, message, status="info"):
        """Print status message with color"""
        if status == "success":
            print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
        elif status == "error":
            print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
        elif status == "warning":
            print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
        else:
            print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")
    
    def print_menu(self):
        """Print main menu"""
        print(f"\n{Colors.BOLD}Current PDF:{Colors.ENDC} {self.current_pdf or 'None'}")
        print(f"\n{Colors.BOLD}Commands:{Colors.ENDC}")
        print(f"  {Colors.OKCYAN}open <file>{Colors.ENDC}     - Open a PDF file")
        print(f"  {Colors.OKCYAN}list{Colors.ENDC}            - List PDF files in current directory")
        print(f"  {Colors.OKCYAN}analyze <type>{Colors.ENDC}  - Analyze current PDF (summary/keywords/entities/technical/comprehensive)")
        print(f"  {Colors.OKCYAN}compare <file>{Colors.ENDC}  - Compare current PDF with another")
        print(f"  {Colors.OKCYAN}save{Colors.ENDC}            - Save analysis results")
        print(f"  {Colors.OKCYAN}export{Colors.ENDC}          - Export to JSON")
        print(f"  {Colors.OKCYAN}google{Colors.ENDC}          - Connect to Google Drive")
        print(f"  {Colors.OKCYAN}sheets{Colors.ENDC}          - Export to Google Sheets")
        print(f"  {Colors.OKCYAN}shell <cmd>{Colors.ENDC}     - Run shell command")
        print(f"  {Colors.OKCYAN}clear{Colors.ENDC}           - Clear screen")
        print(f"  {Colors.OKCYAN}help{Colors.ENDC}            - Show this help")
        print(f"  {Colors.OKCYAN}exit{Colors.ENDC}            - Exit application")
    
    def open_pdf(self, filename):
        """Open a PDF file"""
        if not filename:
            self.print_status("Please specify a filename", "error")
            return
        
        if not os.path.exists(filename):
            self.print_status(f"File not found: {filename}", "error")
            return
        
        self.print_status(f"Opening {filename}...")
        pdf_data = self.reader.read_pdf(filename)
        
        if pdf_data['status'] == 'success':
            self.current_pdf = filename
            self.current_pdf_data = pdf_data
            self.analysis_results = {}
            
            self.print_status(f"Successfully opened {filename}", "success")
            print(f"\n{Colors.BOLD}Metadata:{Colors.ENDC}")
            print(f"  Pages: {pdf_data['metadata'].get('pages', 'N/A')}")
            print(f"  Title: {pdf_data['metadata'].get('title', 'N/A')}")
            print(f"  Author: {pdf_data['metadata'].get('author', 'N/A')}")
            
            # Show preview
            text = pdf_data['text']
            preview = text[:300] + "..." if len(text) > 300 else text
            print(f"\n{Colors.BOLD}Preview:{Colors.ENDC}")
            print(f"{Colors.WARNING}{preview}{Colors.ENDC}")
        else:
            self.print_status(f"Failed to open PDF: {pdf_data.get('message', 'Unknown error')}", "error")
    
    def list_pdfs(self):
        """List PDF files in current directory"""
        pdf_files = glob.glob("*.pdf")
        if pdf_files:
            print(f"\n{Colors.BOLD}PDF files in current directory:{Colors.ENDC}")
            for i, pdf in enumerate(pdf_files, 1):
                size = os.path.getsize(pdf) / 1024  # KB
                print(f"  {i}. {Colors.OKCYAN}{pdf}{Colors.ENDC} ({size:.1f} KB)")
        else:
            self.print_status("No PDF files found in current directory", "warning")
    
    def analyze_pdf(self, analysis_type):
        """Analyze current PDF"""
        if not self.current_pdf:
            self.print_status("No PDF file open. Use 'open <file>' first", "error")
            return
        
        valid_types = ['summary', 'keywords', 'entities', 'technical', 'comprehensive']
        if analysis_type not in valid_types:
            self.print_status(f"Invalid analysis type. Choose from: {', '.join(valid_types)}", "error")
            return
        
        self.print_status(f"Analyzing {self.current_pdf} ({analysis_type})...")
        result = self.analyzer.analyze_text(self.current_pdf_data['text'], analysis_type)
        
        if result['status'] == 'success':
            self.analysis_results[analysis_type] = result
            print(f"\n{Colors.BOLD}{analysis_type.upper()} ANALYSIS:{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{result['analysis']}{Colors.ENDC}")
        else:
            self.print_status(f"Analysis failed: {result.get('message', 'Unknown error')}", "error")
    
    def compare_pdfs(self, other_file):
        """Compare current PDF with another"""
        if not self.current_pdf:
            self.print_status("No PDF file open. Use 'open <file>' first", "error")
            return
        
        if not other_file:
            self.print_status("Please specify a file to compare with", "error")
            return
        
        if not os.path.exists(other_file):
            self.print_status(f"File not found: {other_file}", "error")
            return
        
        self.print_status(f"Comparing {self.current_pdf} with {other_file}...")
        other_data = self.reader.read_pdf(other_file)
        
        if other_data['status'] != 'success':
            self.print_status(f"Failed to read {other_file}", "error")
            return
        
        result = self.analyzer.compare_documents(
            self.current_pdf_data['text'], 
            other_data['text']
        )
        
        if result['status'] == 'success':
            print(f"\n{Colors.BOLD}COMPARISON RESULTS:{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{result['comparison']}{Colors.ENDC}")
        else:
            self.print_status(f"Comparison failed: {result.get('message', 'Unknown error')}", "error")
    
    def save_results(self):
        """Save analysis results"""
        if not self.analysis_results:
            self.print_status("No analysis results to save", "warning")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{os.path.splitext(self.current_pdf)[0]}_{timestamp}.json"
        
        data = {
            'pdf_file': self.current_pdf,
            'timestamp': timestamp,
            'metadata': self.current_pdf_data['metadata'],
            'analyses': self.analysis_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.print_status(f"Results saved to {filename}", "success")
    
    def run_shell_command(self, command):
        """Run a shell command"""
        if not command:
            self.print_status("Please specify a command", "error")
            return
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.stdout:
                print(f"{Colors.OKGREEN}{result.stdout}{Colors.ENDC}")
            if result.stderr:
                print(f"{Colors.FAIL}{result.stderr}{Colors.ENDC}")
        except Exception as e:
            self.print_status(f"Command failed: {str(e)}", "error")
    
    def connect_google_drive(self):
        """Connect to Google Drive"""
        if not os.path.exists('credentials.json'):
            self.print_status("credentials.json not found!", "error")
            print("\nTo get credentials:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Enable Google Drive API")
            print("3. Create OAuth 2.0 credentials")
            print("4. Download as credentials.json")
            return
        
        self.print_status("Connecting to Google Drive...")
        self.drive_handler = GoogleDriveHandler()
        
        if self.drive_handler.service:
            self.print_status("Connected to Google Drive", "success")
            
            # List PDF files
            files = self.drive_handler.list_pdf_files(limit=10)
            if files:
                print(f"\n{Colors.BOLD}Recent PDF files in Google Drive:{Colors.ENDC}")
                for i, file in enumerate(files, 1):
                    print(f"  {i}. {Colors.OKCYAN}{file['name']}{Colors.ENDC}")
        else:
            self.print_status("Failed to connect to Google Drive", "error")
    
    def export_to_sheets(self):
        """Export results to Google Sheets"""
        if not self.analysis_results:
            self.print_status("No analysis results to export", "warning")
            return
        
        if not os.path.exists('credentials.json'):
            self.print_status("Google credentials not found", "error")
            return
        
        self.print_status("Exporting to Google Sheets...")
        self.sheets_writer = GoogleSheetsWriter()
        
        # Prepare data
        data = []
        for analysis_type, result in self.analysis_results.items():
            if result['status'] == 'success':
                data.append({
                    'filename': self.current_pdf,
                    'analysis_type': analysis_type,
                    'analysis': result['analysis'],
                    'timestamp': datetime.now().isoformat()
                })
        
        # Write to sheets
        spreadsheet_id = self.sheets_writer.create_analysis_spreadsheet(
            f"PDF Analysis - {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        if spreadsheet_id:
            for item in data:
                self.sheets_writer.append_analysis(spreadsheet_id, item)
            
            self.print_status(f"Exported to Google Sheets", "success")
            print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        else:
            self.print_status("Failed to create spreadsheet", "error")
    
    def run(self):
        """Main run loop"""
        self.print_header()
        self.print_menu()
        
        while True:
            try:
                # Get command
                command = input(f"\n{Colors.BOLD}pdf-analyzer>{Colors.ENDC} ").strip()
                
                if not command:
                    continue
                
                # Save to history
                readline.write_history_file(self.history_file)
                
                # Parse command
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Execute command
                if cmd == 'exit' or cmd == 'quit':
                    self.print_status("Goodbye!", "success")
                    break
                elif cmd == 'clear':
                    self.print_header()
                    self.print_menu()
                elif cmd == 'help':
                    self.print_menu()
                elif cmd == 'open':
                    self.open_pdf(args)
                elif cmd == 'list':
                    self.list_pdfs()
                elif cmd == 'analyze':
                    self.analyze_pdf(args or 'comprehensive')
                elif cmd == 'summary':
                    self.analyze_pdf('summary')
                elif cmd == 'keywords':
                    self.analyze_pdf('keywords')
                elif cmd == 'entities':
                    self.analyze_pdf('entities')
                elif cmd == 'technical':
                    self.analyze_pdf('technical')
                elif cmd == 'comprehensive':
                    self.analyze_pdf('comprehensive')
                elif cmd == 'compare':
                    self.compare_pdfs(args)
                elif cmd == 'save':
                    self.save_results()
                elif cmd == 'export':
                    self.save_results()
                elif cmd == 'google':
                    self.connect_google_drive()
                elif cmd == 'sheets':
                    self.export_to_sheets()
                elif cmd == 'shell':
                    self.run_shell_command(args)
                else:
                    # Try to open as PDF file
                    if command.endswith('.pdf') and os.path.exists(command):
                        self.open_pdf(command)
                    else:
                        self.print_status(f"Unknown command: {cmd}", "error")
                        print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                self.print_status(f"Error: {str(e)}", "error")

def main():
    """Main entry point"""
    terminal = PDFAnalyzerTerminal()
    terminal.run()

if __name__ == "__main__":
    main()