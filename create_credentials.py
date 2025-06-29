#!/usr/bin/env python3
"""
Helper script to create credentials.json if you have trouble with Google Cloud Console
"""
import json

print("Google Drive OAuth2 Credentials Setup")
print("=" * 40)
print("\nOm du redan har OAuth2 credentials från Google Cloud Console:")
print("1. Kopiera Client ID")
print("2. Kopiera Client Secret")
print("\nOm inte, måste du skapa dem via: https://console.cloud.google.com/apis/credentials")

client_id = input("\nClient ID: ").strip()
client_secret = input("Client Secret: ").strip()

if client_id and client_secret:
    credentials = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "project_id": "ttiotmpc",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    with open('credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print("\n✓ credentials.json skapad!")
    print("\nNu kan du köra: python pdf_analyzer_app.py")
else:
    print("\n✗ Avbruten - ingen credentials.json skapad")