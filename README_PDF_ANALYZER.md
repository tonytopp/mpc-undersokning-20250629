# PDF Analyzer - Google Drive & DeepSeek Integration

En komplett PDF-analysapplikation som integrerar Google Drive och DeepSeek AI.

## Funktioner

- **PDF-läsning**: Läs och extrahera text från PDF-filer
- **Google Drive Integration**: 
  - Ladda upp PDF-filer till Google Drive
  - Lista och ladda ner PDF-filer från Google Drive
  - Autentisering med OAuth2
- **DeepSeek AI-analys**:
  - Omfattande textanalys
  - Sammanfattningar
  - Nyckelordsextraktion
  - Entitetsigenkänning
  - Teknisk dokumentanalys
  - Generera frågor om innehållet
- **Grafiskt användargränssnitt** med PyQt5

## Installation

1. Installera beroenden:
```bash
pip install -r requirements.txt
```

2. Konfigurera Google Drive API:
   - Gå till https://console.cloud.google.com/
   - Skapa ett nytt projekt eller välj befintligt
   - Aktivera Google Drive API
   - Skapa credentials (OAuth 2.0 Client ID)
   - Ladda ner som `credentials.json` till projektmappen

3. Konfigurera DeepSeek API:
   - Gå till https://platform.deepseek.com/
   - Skapa ett konto och generera API-nyckel
   - Sätt miljövariabeln: `export DEEPSEEK_API_KEY="din-api-nyckel"`

## Användning

Kör huvudapplikationen:
```bash
python pdf_analyzer_app.py
```

### Steg-för-steg:

1. **Anslut till Google Drive** (valfritt)
   - Klicka på "Connect to Google Drive"
   - Följ autentiseringsflödet i webbläsaren

2. **Ladda PDF**
   - Från datorn: "Load PDF from Computer"
   - Från Google Drive: Lista filer och välj "Download Selected"

3. **Analysera**
   - Välj analystyp (Comprehensive, Summary, Keywords, etc.)
   - Klicka "Analyze with DeepSeek"

4. **Exportera resultat**
   - Klicka "Export Results" för att spara analys som JSON

## Filer

- `pdf_reader.py` - PDF-läsare med PyPDF2 och pdfplumber
- `google_drive_handler.py` - Google Drive integration
- `deepseek_analyzer.py` - DeepSeek AI-analys
- `pdf_analyzer_app.py` - Huvudapplikation med GUI
- `requirements.txt` - Python-beroenden

## API-nycklar

API-nycklar kan konfigureras på två sätt:

1. Miljövariabler:
   ```bash
   export DEEPSEEK_API_KEY="sk-89ab36dbe41e44acb9b58178d54642e6"
   ```

2. Via Settings-menyn i applikationen

## Felsökning

- Om Google Drive-anslutning misslyckas, kontrollera att `credentials.json` finns
- Om DeepSeek-analys inte fungerar, verifiera att API-nyckeln är korrekt
- Vid importfel, kör: `pip install -r requirements.txt`