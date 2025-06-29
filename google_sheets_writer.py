import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
from typing import List, Dict, Optional
import logging


class GoogleSheetsWriter:
    """Hanterar skrivning till Google Sheets"""
    
    def __init__(self, credentials_file: str, spreadsheet_name: str):
        """
        Initialiserar Google Sheets-anslutning
        
        Args:
            credentials_file: Sökväg till service account JSON-fil
            spreadsheet_name: Namnet på Google Sheets-dokumentet
        """
        self.logger = logging.getLogger(__name__)
        
        # Konfigurera Google Sheets API scope
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            # Autentisera med service account
            self.creds = Credentials.from_service_account_file(
                credentials_file, 
                scopes=self.scope
            )
            self.client = gspread.authorize(self.creds)
            
            # Öppna eller skapa spreadsheet
            try:
                self.spreadsheet = self.client.open(spreadsheet_name)
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.client.create(spreadsheet_name)
                self.logger.info(f"Skapade nytt spreadsheet: {spreadsheet_name}")
            
        except Exception as e:
            self.logger.error(f"Fel vid initialisering av Google Sheets: {e}")
            raise
    
    def write_metrics(self, metrics: List[Dict], sheet_name: str = "Metrics"):
        """
        Skriver metrics till ett specifikt sheet
        
        Args:
            metrics: Lista med metrics-dictionaries
            sheet_name: Namnet på sheet att skriva till
        """
        try:
            # Hämta eller skapa sheet
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=sheet_name, 
                    rows=1000, 
                    cols=20
                )
            
            # Konvertera metrics till DataFrame för enklare hantering
            df = pd.DataFrame(metrics)
            
            # Om sheet är tomt, skriv headers
            if worksheet.row_count == 0 or worksheet.cell(1, 1).value is None:
                headers = list(df.columns)
                worksheet.update('A1', [headers])
            
            # Hitta första tomma rad
            values = worksheet.get_all_values()
            next_row = len(values) + 1
            
            # Förbered data för batch-uppdatering
            data_to_write = df.values.tolist()
            
            # Skriv data
            if data_to_write:
                cell_range = f'A{next_row}:' \
                           f'{chr(65 + len(df.columns) - 1)}{next_row + len(data_to_write) - 1}'
                worksheet.update(cell_range, data_to_write)
                
                self.logger.info(f"Skrev {len(data_to_write)} rader till {sheet_name}")
            
        except Exception as e:
            self.logger.error(f"Fel vid skrivning av metrics: {e}")
            raise
    
    def write_analysis(self, analysis: Dict, sheet_name: str = "Analysis"):
        """
        Skriver analysresultat till sheet
        
        Args:
            analysis: Dictionary med analysresultat
            sheet_name: Namnet på sheet att skriva till
        """
        try:
            # Hämta eller skapa sheet
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=sheet_name, 
                    rows=1000, 
                    cols=10
                )
                # Lägg till headers
                headers = ["Timestamp", "Analysis", "Metrics Count"]
                worksheet.update('A1', [headers])
            
            # Hitta första tomma rad
            values = worksheet.get_all_values()
            next_row = len(values) + 1
            
            # Förbered data
            row_data = [
                analysis.get('timestamp', datetime.now().isoformat()),
                analysis.get('analysis', ''),
                analysis.get('metrics_count', 0)
            ]
            
            # Skriv data
            cell_range = f'A{next_row}:C{next_row}'
            worksheet.update(cell_range, [row_data])
            
            self.logger.info(f"Skrev analysresultat till {sheet_name}")
            
        except Exception as e:
            self.logger.error(f"Fel vid skrivning av analys: {e}")
            raise
    
    def create_dashboard_sheet(self):
        """Skapar ett dashboard-sheet med formler och visualiseringar"""
        try:
            sheet_name = "Dashboard"
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=sheet_name, 
                    rows=50, 
                    cols=10
                )
            
            # Skapa dashboard-layout
            dashboard_layout = [
                ["Program Monitor Dashboard", "", "", "", ""],
                ["", "", "", "", ""],
                ["Sammanfattning", "", "", "", ""],
                ["Total mätpunkter:", "=COUNTA(Metrics!A:A)-1", "", "", ""],
                ["Genomsnittlig CPU:", "=AVERAGE(Metrics!D:D)", "%", "", ""],
                ["Max CPU:", "=MAX(Metrics!D:D)", "%", "", ""],
                ["Genomsnittligt minne:", "=AVERAGE(Metrics!E:E)", "MB", "", ""],
                ["Max minne:", "=MAX(Metrics!E:E)", "MB", "", ""],
                ["", "", "", "", ""],
                ["Senaste analys:", "", "", "", ""],
                ["=INDEX(Analysis!B:B,COUNTA(Analysis!B:B))", "", "", "", ""]
            ]
            
            # Skriv dashboard-layout
            worksheet.update('A1', dashboard_layout)
            
            # Formatera headers
            worksheet.format('A1', {
                'textFormat': {'bold': True, 'fontSize': 16}
            })
            worksheet.format('A3', {
                'textFormat': {'bold': True, 'fontSize': 14}
            })
            worksheet.format('A10', {
                'textFormat': {'bold': True, 'fontSize': 14}
            })
            
            self.logger.info("Dashboard skapat")
            
        except Exception as e:
            self.logger.error(f"Fel vid skapande av dashboard: {e}")
            raise
    
    def share_spreadsheet(self, email: str, role: str = 'reader'):
        """
        Delar spreadsheet med en användare
        
        Args:
            email: E-postadress att dela med
            role: Roll (reader, writer, owner)
        """
        try:
            self.spreadsheet.share(email, perm_type='user', role=role)
            self.logger.info(f"Spreadsheet delat med {email} som {role}")
        except Exception as e:
            self.logger.error(f"Fel vid delning av spreadsheet: {e}")
            raise
    
    def get_spreadsheet_url(self) -> str:
        """Returnerar URL till spreadsheet"""
        return self.spreadsheet.url


def setup_google_sheets_monitoring():
    """Exempel på hur man sätter upp Google Sheets-integration"""
    
    # Steg för att sätta upp Google Sheets API:
    print("""
    För att använda Google Sheets API:
    
    1. Gå till Google Cloud Console (https://console.cloud.google.com)
    2. Skapa ett nytt projekt eller välj ett befintligt
    3. Aktivera Google Sheets API och Google Drive API
    4. Skapa service account credentials:
       - Gå till "Credentials" 
       - Klicka "Create Credentials" > "Service Account"
       - Ladda ner JSON-nyckelfilen
    5. Installera nödvändiga paket:
       pip install gspread google-auth pandas
    
    Exempel på användning:
    """)
    
    example_code = '''
# Exempel på integration med program_monitor.py
from google_sheets_writer import GoogleSheetsWriter
from program_monitor import ProgramMonitor

# Initiera Google Sheets writer
sheets_writer = GoogleSheetsWriter(
    credentials_file='path/to/your/credentials.json',
    spreadsheet_name='Program Monitor Data'
)

# Skapa dashboard
sheets_writer.create_dashboard_sheet()

# Initiera program monitor med anpassad write-funktion
monitor = ProgramMonitor(
    process_name="your_program",
    deepseek_api_key="your_api_key"
)

# Override write_to_google_sheets metoden
original_write = monitor.write_to_google_sheets

def custom_write_to_google_sheets(data):
    if data['type'] == 'metrics':
        sheets_writer.write_metrics([data['data']])
    elif data['type'] == 'analysis':
        sheets_writer.write_analysis(data['data'])
    # Anropa också original för JSON-backup
    original_write(data)

monitor.write_to_google_sheets = custom_write_to_google_sheets

# Starta övervakning
monitor.start_monitoring()

# Hämta spreadsheet URL
print(f"Visa data på: {sheets_writer.get_spreadsheet_url()}")
'''
    
    print(example_code)


if __name__ == "__main__":
    setup_google_sheets_monitoring()