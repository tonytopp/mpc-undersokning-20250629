# PDF Analyzer Terminal Interface

Ett interaktivt terminalgränssnitt för PDF-analys med integrerad kommandofunktionalitet.

## Start

```bash
./start_terminal.sh
# eller
python3 pdf_analyzer_terminal.py
```

## Funktioner

- **Interaktiv terminal** med färgkodning och autocompletition
- **PDF-analys** med flera analystyper (sammanfattning, nyckelord, entiteter, teknisk, omfattande)
- **Jämför PDFer** - jämför två PDF-filer
- **Google Drive-integration** - lista och hämta PDFer från Drive
- **Google Sheets-export** - exportera analysresultat till Sheets
- **Inbyggd terminal** - kör shell-kommandon direkt från gränssnittet
- **Historik** - kommandohistorik sparas mellan sessioner

## Kommandon

### Filhantering
- `open <fil>` - Öppna en PDF-fil
- `list` - Lista PDF-filer i aktuell katalog
- `save` - Spara analysresultat till JSON
- `export` - Exportera till JSON

### Analys
- `analyze <typ>` - Analysera aktuell PDF
- `summary` - Snabb sammanfattning
- `keywords` - Extrahera nyckelord
- `entities` - Hitta entiteter (namn, datum, etc)
- `technical` - Teknisk analys
- `comprehensive` - Omfattande analys
- `compare <fil>` - Jämför med annan PDF

### Integration
- `google` - Anslut till Google Drive
- `sheets` - Exportera till Google Sheets

### System
- `shell <kommando>` - Kör shell-kommando
- `clear` - Rensa skärmen
- `help` - Visa hjälp
- `exit` - Avsluta

## Exempel

```bash
pdf-analyzer> list
PDF files in current directory:
  1. dokument1.pdf (125.3 KB)
  2. dokument2.pdf (89.7 KB)

pdf-analyzer> open dokument1.pdf
✓ Successfully opened dokument1.pdf

pdf-analyzer> summary
Analyzing dokument1.pdf (summary)...
✓ Analysis complete

SUMMARY ANALYSIS:
Document Summary:
This document contains approximately 1250 words...

pdf-analyzer> compare dokument2.pdf
Comparing dokument1.pdf with dokument2.pdf...
✓ Comparison complete

pdf-analyzer> save
✓ Results saved to analysis_dokument1_20250629_143022.json

pdf-analyzer> shell ls -la *.json
-rw-r--r--  1 user  staff  4523 Jun 29 14:30 analysis_dokument1_20250629_143022.json
```

## Tangentbordsgenvägar

- **Tab** - Autocompletition för kommandon och filnamn
- **Upp/Ner** - Navigera i kommandohistorik
- **Ctrl+C** - Avbryt aktuellt kommando
- **Ctrl+D** - Avsluta (samma som 'exit')

## Färgkodning

- 🟢 Grön - Lyckade operationer
- 🔴 Röd - Fel och varningar
- 🔵 Blå - Information
- 🟡 Gul - Förhandsvisning av text
- 🟣 Lila - Rubriker

## Konfiguration

Historikfilen sparas i: `~/.pdf_analyzer_history`

För Google-integration behövs `credentials.json` i samma katalog.