import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.core.config import settings

class DriveService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        self.creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        self.folder_id = settings.DRIVE_FOLDER_ID
        
        self.service = None
        if os.path.exists(self.creds_path):
            try:
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.creds_path, scopes=self.scopes
                )
                self.service = build('drive', 'v3', credentials=self.credentials)
            except Exception as e:
                print(f"Failed to initialize Google Drive service: {e}")
        else:
            print(f"Credentials not found at {self.creds_path}. Please check configuration.")

    def search_files(self, q: str) -> str:
        """
        Executes a search query against the Google Drive API.
        """
        if not self.service:
            return json.dumps({"error": "Google Drive credentials not found or service not initialized."})
            
        try:
            # Ensure we only search within the designated folder
            if self.folder_id:
                folder_query = f"'{self.folder_id}' in parents"
                if q:
                    # Append the folder constraint securely
                    q = f"({q}) and {folder_query}"
                else:
                    q = folder_query
            
            # Execute the search
            results = self.service.files().list(
                q=q,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, webViewLink)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            return json.dumps({"files": files})
        except Exception as e:
            return json.dumps({"error": f"Error executing search: {str(e)}"})

# Singleton instance
drive_service = DriveService()
