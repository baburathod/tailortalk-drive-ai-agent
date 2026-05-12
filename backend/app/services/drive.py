import os
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.core.config import settings

# Setup logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriveService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        self.folder_id = settings.DRIVE_FOLDER_ID
        self.service = None
        self.credentials = None
        
        logger.info("=" * 70)
        logger.info("INITIALIZING GOOGLE DRIVE SERVICE")
        logger.info("=" * 70)
        logger.info(f"DRIVE_FOLDER_ID: {self.folder_id}")
        logger.info(f"GOOGLE_APPLICATION_CREDENTIALS env: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
        logger.info(f"GOOGLE_CREDENTIALS_JSON env length: {len(settings.GOOGLE_CREDENTIALS_JSON) if settings.GOOGLE_CREDENTIALS_JSON else 0}")
        
        # METHOD 1: GOOGLE_CREDENTIALS_JSON environment variable (JSON string directly)
        if settings.GOOGLE_CREDENTIALS_JSON and settings.GOOGLE_CREDENTIALS_JSON.strip():
            logger.info("\n[METHOD 1] Attempting to load from GOOGLE_CREDENTIALS_JSON environment variable...")
            try:
                creds_info = json.loads(settings.GOOGLE_CREDENTIALS_JSON)
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_info, scopes=self.scopes
                )
                logger.info("✅ Successfully loaded credentials from GOOGLE_CREDENTIALS_JSON")
            except json.JSONDecodeError as e:
                logger.warning(f"❌ Invalid JSON in GOOGLE_CREDENTIALS_JSON: {e}")
            except Exception as e:
                logger.warning(f"❌ Error loading from GOOGLE_CREDENTIALS_JSON: {e}")

        # METHOD 2: GOOGLE_APPLICATION_CREDENTIALS as file path (RENDER SECRET FILES)
        # In Render, secret files are mounted at /etc/secrets/{filename}
        if not self.credentials:
            logger.info("\n[METHOD 2] Attempting to load from GOOGLE_APPLICATION_CREDENTIALS file path...")
            
            # Render mounts secret files at /etc/secrets/
            render_secret_path = "/etc/secrets/credentials.json"
            
            # Try multiple possible paths in order of priority
            candidate_paths = [
                render_secret_path,  # Render's standard secret file mount
                settings.GOOGLE_APPLICATION_CREDENTIALS,  # From env variable
                "credentials.json",  # Current directory
                os.path.join(os.getcwd(), "credentials.json"),
                os.path.join("/root", "credentials.json"),  # Render's home directory
                os.path.expanduser("~/credentials.json"),  # User home
            ]
            
            logger.info(f"Candidate paths to check:")
            for i, path in enumerate(candidate_paths, 1):
                logger.info(f"  {i}. {path}")
            
            for path in candidate_paths:
                logger.info(f"\nChecking: {path}")
                if os.path.exists(path):
                    logger.info(f"  ✅ File exists at {path}")
                    try:
                        with open(path, 'r') as f:
                            creds_content = f.read()
                            logger.info(f"  ✅ File is readable ({len(creds_content)} bytes)")
                        
                        self.credentials = service_account.Credentials.from_service_account_file(
                            path, scopes=self.scopes
                        )
                        logger.info(f"✅ Successfully loaded credentials from file: {path}")
                        break
                    except json.JSONDecodeError as e:
                        logger.warning(f"  ❌ Invalid JSON format in file: {e}")
                    except PermissionError as e:
                        logger.warning(f"  ❌ Permission denied reading file: {e}")
                    except Exception as e:
                        logger.warning(f"  ❌ Error loading from file: {e}")
                else:
                    logger.info(f"  ❌ File not found")
        
        # INITIALIZE GOOGLE DRIVE API SERVICE
        if self.credentials:
            logger.info("\n[INITIALIZATION] Building Google Drive API v3 service...")
            try:
                self.service = build('drive', 'v3', credentials=self.credentials)
                
                # Test the connection by calling about()
                logger.info("[TEST] Testing Google Drive API connection...")
                about = self.service.about().get(fields='user(displayName, emailAddress)').execute()
                user_info = about.get('user', {})
                logger.info(f"✅ Google Drive API v3 service initialized successfully")
                logger.info(f"   Authenticated as: {user_info.get('displayName', 'Unknown')} ({user_info.get('emailAddress', 'Unknown')})")
                logger.info("=" * 70)
                
            except HttpError as e:
                logger.error(f"❌ Google Drive API HttpError: {e}")
                self.service = None
            except Exception as e:
                logger.error(f"❌ Failed to build Google Drive API service: {e}")
                self.service = None
        else:
            logger.error("❌ CRITICAL: Google Drive credentials not loaded from any source!")
            logger.error("   API calls will fail. Please ensure credentials.json is provided.")
            logger.error("=" * 70)

    def search_files(self, q: str) -> str:
        """
        Executes a search query against the Google Drive API using files().list()
        
        Args:
            q: Query string according to Google Drive API v3 syntax
            
        Returns:
            JSON string with results or error message
        """
        logger.info(f"\n[SEARCH REQUEST] Query: {q}")
        logger.info(f"[SEARCH REQUEST] Folder ID: {self.folder_id}")
        
        # Check if service is initialized
        if not self.service:
            error_msg = "Google Drive service not initialized. Credentials may not be loaded."
            logger.error(f"❌ {error_msg}")
            return json.dumps({"error": error_msg, "status": "CREDENTIAL_ERROR"})
        
        if not self.credentials:
            error_msg = "Google Drive credentials not available. Service initialization failed."
            logger.error(f"❌ {error_msg}")
            return json.dumps({"error": error_msg, "status": "CREDENTIAL_ERROR"})
        
        try:
            # Build the query with folder constraint
            query_parts = []
            
            # If a folder ID is specified, ensure we search within it
            if self.folder_id:
                query_parts.append(f"'{self.folder_id}' in parents")
            
            # Add the user's search query
            if q and q.strip():
                query_parts.append(q)
            
            # Combine query parts
            final_query = " and ".join(query_parts) if query_parts else None
            
            logger.info(f"[SEARCH] Final query: {final_query}")
            
            # Execute the files().list() call
            logger.info("[API] Calling Google Drive API files().list()...")
            
            list_call = self.service.files().list(
                q=final_query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, webViewLink, parents, owners)',
                pageSize=20,
                orderBy='modifiedTime desc'
            )
            
            results = list_call.execute()
            
            files = results.get('files', [])
            logger.info(f"✅ Search successful. Found {len(files)} files")
            
            # Log file details
            for i, file in enumerate(files, 1):
                logger.info(f"   {i}. {file.get('name')} ({file.get('mimeType')})")
            
            return json.dumps({
                "status": "SUCCESS",
                "files": files,
                "count": len(files)
            })
            
        except HttpError as e:
            error_details = {
                "error": f"Google Drive API error: {e.resp.status} - {e.resp.reason}",
                "status": "API_ERROR",
                "details": str(e)
            }
            logger.error(f"❌ {error_details['error']}")
            return json.dumps(error_details)
            
        except Exception as e:
            error_details = {
                "error": f"Error executing search: {str(e)}",
                "status": "SEARCH_ERROR",
                "details": str(e)
            }
            logger.error(f"❌ {error_details['error']}")
            return json.dumps(error_details)

# Singleton instance
drive_service = DriveService()
