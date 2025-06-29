#!/usr/bin/env python3
"""
PDF Analyzer Application
Main application with UI for PDF analysis using Google Drive and Claude AI
"""
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pdf_reader import PDFReader
from google_drive_handler import GoogleDriveHandler
from claude_analyzer import ClaudeAnalyzer as AIAnalyzer
import json
from datetime import datetime

class PDFAnalyzerApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.pdf_reader = PDFReader()
        self.drive_handler = None
        self.analyzer = AIAnalyzer()
        self.current_pdf_data = None
        
        self.init_ui()
        self.check_setup()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("PDF Analyzer - Google Drive & Claude AI")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        
        self.load_pdf_btn = QPushButton("Load PDF from Computer")
        self.load_pdf_btn.clicked.connect(self.load_local_pdf)
        file_layout.addWidget(self.load_pdf_btn)
        
        self.upload_drive_btn = QPushButton("Upload to Google Drive")
        self.upload_drive_btn.clicked.connect(self.upload_to_drive)
        self.upload_drive_btn.setEnabled(False)
        file_layout.addWidget(self.upload_drive_btn)
        
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)
        
        # Google Drive group
        drive_group = QGroupBox("Google Drive")
        drive_layout = QVBoxLayout()
        
        self.connect_drive_btn = QPushButton("Connect to Google Drive")
        self.connect_drive_btn.clicked.connect(self.connect_google_drive)
        drive_layout.addWidget(self.connect_drive_btn)
        
        self.list_files_btn = QPushButton("List PDF Files")
        self.list_files_btn.clicked.connect(self.list_drive_files)
        self.list_files_btn.setEnabled(False)
        drive_layout.addWidget(self.list_files_btn)
        
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.clicked.connect(self.download_from_drive)
        self.download_btn.setEnabled(False)
        drive_layout.addWidget(self.download_btn)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        drive_layout.addWidget(self.file_list)
        
        drive_group.setLayout(drive_layout)
        left_layout.addWidget(drive_group)
        
        # Analysis group
        analysis_group = QGroupBox("Analysis Options")
        analysis_layout = QVBoxLayout()
        
        self.analysis_type = QComboBox()
        self.analysis_type.addItems([
            "Comprehensive",
            "Summary",
            "Keywords",
            "Entities",
            "Technical"
        ])
        analysis_layout.addWidget(QLabel("Analysis Type:"))
        analysis_layout.addWidget(self.analysis_type)
        
        self.analyze_btn = QPushButton("Analyze with Claude AI")
        self.analyze_btn.clicked.connect(self.analyze_pdf)
        self.analyze_btn.setEnabled(False)
        analysis_layout.addWidget(self.analyze_btn)
        
        self.generate_questions_btn = QPushButton("Generate Questions")
        self.generate_questions_btn.clicked.connect(self.generate_questions)
        self.generate_questions_btn.setEnabled(False)
        analysis_layout.addWidget(self.generate_questions_btn)
        
        analysis_group.setLayout(analysis_layout)
        left_layout.addWidget(analysis_group)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # PDF Content tab
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.tabs.addTab(self.content_text, "PDF Content")
        
        # Analysis tab
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.tabs.addTab(self.analysis_text, "Analysis Results")
        
        # Metadata tab
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.tabs.addTab(self.metadata_text, "Metadata")
        
        right_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_label = QLabel("Ready")
        right_layout.addWidget(self.status_label)
        
        # Export button
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        right_layout.addWidget(self.export_btn)
        
        main_layout.addWidget(right_panel)
        
        # Menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        api_keys_action = QAction('API Keys', self)
        api_keys_action.triggered.connect(self.show_api_settings)
        settings_menu.addAction(api_keys_action)
    
    def check_setup(self):
        """Check if APIs are configured"""
        if not self.analyzer.api_key:
            self.status_label.setText("Warning: Claude API key not configured")
            self.status_label.setStyleSheet("color: orange")
    
    def connect_google_drive(self):
        """Connect to Google Drive"""
        try:
            self.status_label.setText("Connecting to Google Drive...")
            self.drive_handler = GoogleDriveHandler()
            
            if self.drive_handler.service:
                self.connect_drive_btn.setText("Connected to Google Drive")
                self.connect_drive_btn.setEnabled(False)
                self.list_files_btn.setEnabled(True)
                self.status_label.setText("Connected to Google Drive")
                self.status_label.setStyleSheet("color: green")
            else:
                self.status_label.setText("Failed to connect to Google Drive")
                self.status_label.setStyleSheet("color: red")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")
    
    def load_local_pdf(self):
        """Load PDF from local file system"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.status_label.setText("Reading PDF...")
            self.current_pdf_data = self.pdf_reader.read_pdf(file_path)
            
            if self.current_pdf_data['status'] == 'success':
                # Display content
                self.content_text.setPlainText(self.current_pdf_data['text'])
                
                # Display metadata
                metadata = json.dumps(self.current_pdf_data['metadata'], indent=2)
                self.metadata_text.setPlainText(metadata)
                
                # Enable buttons
                self.analyze_btn.setEnabled(True)
                self.generate_questions_btn.setEnabled(True)
                self.export_btn.setEnabled(True)
                
                if self.drive_handler:
                    self.upload_drive_btn.setEnabled(True)
                
                self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
                self.tabs.setCurrentIndex(0)
            else:
                self.status_label.setText("Failed to read PDF")
                self.status_label.setStyleSheet("color: red")
    
    def list_drive_files(self):
        """List PDF files from Google Drive"""
        if not self.drive_handler:
            return
        
        self.status_label.setText("Fetching files from Google Drive...")
        self.file_list.clear()
        
        files = self.drive_handler.list_pdf_files()
        
        for file in files:
            item = QListWidgetItem(file['name'])
            item.setData(Qt.UserRole, file)
            self.file_list.addItem(item)
        
        self.status_label.setText(f"Found {len(files)} PDF files")
    
    def on_file_selected(self):
        """Handle file selection"""
        if self.file_list.selectedItems():
            self.download_btn.setEnabled(True)
    
    def download_from_drive(self):
        """Download selected file from Google Drive"""
        selected = self.file_list.selectedItems()
        if not selected:
            return
        
        file_data = selected[0].data(Qt.UserRole)
        save_path = QFileDialog.getSaveFileName(
            self, "Save PDF", file_data['name'], "PDF Files (*.pdf)"
        )[0]
        
        if save_path:
            self.status_label.setText("Downloading...")
            result = self.drive_handler.download_pdf(file_data['id'], save_path)
            
            if result['status'] == 'success':
                self.status_label.setText(f"Downloaded: {result['file_name']}")
                
                # Automatically load the downloaded file
                self.current_pdf_data = self.pdf_reader.read_pdf(result['file_path'])
                self.content_text.setPlainText(self.current_pdf_data['text'])
                self.analyze_btn.setEnabled(True)
                self.generate_questions_btn.setEnabled(True)
                self.tabs.setCurrentIndex(0)
    
    def upload_to_drive(self):
        """Upload current PDF to Google Drive"""
        if not self.current_pdf_data or not self.drive_handler:
            return
        
        file_path = self.current_pdf_data['file_path']
        self.status_label.setText("Uploading to Google Drive...")
        
        result = self.drive_handler.upload_pdf(file_path)
        
        if result['status'] == 'success':
            self.status_label.setText("Uploaded successfully!")
            QMessageBox.information(
                self, "Success", 
                f"File uploaded!\nView at: {result['web_view_link']}"
            )
            # Refresh file list
            self.list_drive_files()
        else:
            self.status_label.setText("Upload failed")
            QMessageBox.critical(self, "Error", result['message'])
    
    def analyze_pdf(self):
        """Analyze PDF with AI"""
        if not self.current_pdf_data:
            return
        
        if not self.analyzer.api_key:
            QMessageBox.warning(
                self, "Warning", 
                "AI API key not configured. Please set it in Settings."
            )
            return
        
        analysis_type = self.analysis_type.currentText().lower()
        self.status_label.setText(f"Analyzing ({analysis_type})...")
        
        # Create progress dialog
        progress = QProgressDialog("Analyzing PDF...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            results = self.analyzer.analyze_pdf_content(
                self.current_pdf_data, 
                [analysis_type]
            )
            
            if results['status'] == 'success':
                analysis = results['analyses'][analysis_type]
                
                if analysis['status'] == 'success':
                    self.analysis_text.setPlainText(analysis['analysis'])
                    self.tabs.setCurrentIndex(1)
                    self.status_label.setText("Analysis complete")
                else:
                    self.status_label.setText("Analysis failed")
                    QMessageBox.critical(self, "Error", analysis['message'])
            
        finally:
            progress.close()
    
    def generate_questions(self):
        """Generate questions about the PDF"""
        if not self.current_pdf_data or not self.analyzer.api_key:
            return
        
        self.status_label.setText("Generating questions...")
        
        result = self.analyzer.generate_questions(self.current_pdf_data['text'])
        
        if result['status'] == 'success':
            self.analysis_text.append("\n\n--- Generated Questions ---\n")
            self.analysis_text.append(result['questions'])
            self.tabs.setCurrentIndex(1)
            self.status_label.setText("Questions generated")
    
    def export_results(self):
        """Export analysis results"""
        if not self.current_pdf_data:
            return
        
        file_path = QFileDialog.getSaveFileName(
            self, "Export Results", 
            f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )[0]
        
        if file_path:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'file_info': {
                    'name': os.path.basename(self.current_pdf_data['file_path']),
                    'metadata': self.current_pdf_data['metadata']
                },
                'content': self.content_text.toPlainText(),
                'analysis': self.analysis_text.toPlainText()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.status_label.setText(f"Exported to: {os.path.basename(file_path)}")
    
    def show_api_settings(self):
        """Show API settings dialog"""
        dialog = APISettingsDialog(self)
        if dialog.exec_():
            # Reload analyzer with new key
            self.analyzer = AIAnalyzer()
            self.check_setup()

class APISettingsDialog(QDialog):
    """Dialog for API settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Settings")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # API key
        layout.addWidget(QLabel("Anthropic API Key:"))
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setText(os.getenv('ANTHROPIC_API_KEY', ''))
        layout.addWidget(self.api_key)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(100)
        instructions.setPlainText(
            "To get an Anthropic API key:\n"
            "1. Go to https://console.anthropic.com/\n"
            "2. Sign up or log in\n"
            "3. Go to API Keys section\n"
            "4. Create a new API key"
        )
        layout.addWidget(instructions)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """Save API settings"""
        # Save to environment variable for current session
        os.environ['ANTHROPIC_API_KEY'] = self.api_key.text()
        
        # Save to config file for persistence
        config = {
            'anthropic_api_key': self.api_key.text()
        }
        
        with open('.api_config.json', 'w') as f:
            json.dump(config, f)
        
        self.accept()

def main():
    """Main entry point"""
    # Load saved API keys
    if os.path.exists('.api_config.json'):
        with open('.api_config.json', 'r') as f:
            config = json.load(f)
            os.environ['ANTHROPIC_API_KEY'] = config.get('anthropic_api_key', '')
            # Fallback to old key name for compatibility
            if not os.environ.get('ANTHROPIC_API_KEY'):
                os.environ['ANTHROPIC_API_KEY'] = config.get('deepseek_api_key', config.get('anthropic_api_key', ''))
    
    app = QApplication(sys.argv)
    window = PDFAnalyzerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()