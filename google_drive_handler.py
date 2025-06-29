#!/usr/bin/env python3
"""
Google Drive Handler
Handles upload and download of PDFs to/from Google Drive
"""
import os
import io
import json
import mimetypes
from typing import Optional, List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveHandler:
    """Handle Google Drive operations for PDFs"""
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """Initialize Google Drive handler"""
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    logger.error(f"Credentials file {self.credentials_file} not found")
                    logger.info("Get credentials from Google Cloud Console:")
                    logger.info("1. Go to https://console.cloud.google.com/")
                    logger.info("2. Create a new project or select existing")
                    logger.info("3. Enable Google Drive API")
                    logger.info("4. Create credentials (OAuth 2.0 Client ID)")
                    logger.info("5. Download as credentials.json")
                    return
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Drive")
    
    def upload_pdf(self, file_path: str, folder_id: Optional[str] = None) -> Dict:
        """
        Upload a PDF file to Google Drive
        
        Args:
            file_path: Path to the PDF file
            folder_id: Optional Google Drive folder ID
            
        Returns:
            Dict with file ID and web link
        """
        if not self.service:
            return {'status': 'error', 'message': 'Not authenticated'}
        
        try:
            file_name = os.path.basename(file_path)
            mime_type = 'application/pdf'
            
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            logger.info(f"Uploaded {file_name} with ID: {file.get('id')}")
            
            return {
                'status': 'success',
                'file_id': file.get('id'),
                'web_view_link': file.get('webViewLink'),
                'download_link': file.get('webContentLink'),
                'file_name': file_name
            }
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def download_pdf(self, file_id: str, save_path: str) -> Dict:
        """
        Download a PDF file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            save_path: Local path to save the file
            
        Returns:
            Dict with download status
        """
        if not self.service:
            return {'status': 'error', 'message': 'Not authenticated'}
        
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'downloaded.pdf')
            
            # Download file
            request = self.service.files().get_media(fileId=file_id)
            
            # Use full path with filename
            if os.path.isdir(save_path):
                full_path = os.path.join(save_path, file_name)
            else:
                full_path = save_path
            
            fh = io.FileIO(full_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"Download {int(status.progress() * 100)}%")
            
            logger.info(f"Downloaded to: {full_path}")
            
            return {
                'status': 'success',
                'file_path': full_path,
                'file_name': file_name,
                'file_id': file_id
            }
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def list_pdf_files(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        List PDF files in Google Drive
        
        Args:
            folder_id: Optional folder ID to list files from
            
        Returns:
            List of file dictionaries
        """
        if not self.service:
            return []
        
        try:
            query = "mimeType='application/pdf'"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, size, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} PDF files")
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Dict:
        """Create a folder in Google Drive"""
        if not self.service:
            return {'status': 'error', 'message': 'Not authenticated'}
        
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id,webViewLink'
            ).execute()
            
            logger.info(f"Created folder: {folder_name} with ID: {folder.get('id')}")
            
            return {
                'status': 'success',
                'folder_id': folder.get('id'),
                'web_view_link': folder.get('webViewLink')
            }
            
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return {'status': 'error', 'message': str(e)}

# Test the module
if __name__ == "__main__":
    handler = GoogleDriveHandler()
    
    # List PDF files
    print("\nListing PDF files:")
    files = handler.list_pdf_files()
    for file in files[:5]:  # Show first 5
        print(f"- {file['name']} (ID: {file['id']})")
    
    # Test upload (if test.pdf exists)
    if os.path.exists('test.pdf'):
        print("\nTesting upload:")
        result = handler.upload_pdf('test.pdf')
        print(result)