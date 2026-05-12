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
        self.init_error = "Not initialized yet"
        self.initialize()

    def initialize(self):
        """
        Attempts to load credentials and initialize the Google Drive API service.
        Can be called dynamically per request to automatically recover if secrets are mounted post-startup.
        """
        logger.info("=" * 70)
        logger.info("ATTEMPTING DYNAMIC GOOGLE DRIVE SERVICE INITIALIZATION")
        logger.info("=" * 70)
        
        # Reset previous state
        self.credentials = None
        self.init_error = None
        
        # METHOD 1: GOOGLE_CREDENTIALS_JSON environment variable (JSON string directly)
        env_json = settings.GOOGLE_CREDENTIALS_JSON
        if env_json and env_json.strip():
            logger.info("[METHOD 1] Attempting to load from GOOGLE_CREDENTIALS_JSON environment variable...")
            try:
                # Strip invisible leading/trailing characters that can occur during cloud dashboard copy-pasting
                cleaned_json = env_json.strip()
                creds_info = json.loads(cleaned_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_info, scopes=self.scopes
                )
                logger.info("✅ Successfully loaded credentials from GOOGLE_CREDENTIALS_JSON")
            except Exception as e:
                self.init_error = f"Failed parsing GOOGLE_CREDENTIALS_JSON string: {str(e)}"
                logger.warning(f"❌ {self.init_error}")

        # METHOD 2: Check raw string inside GOOGLE_APPLICATION_CREDENTIALS if user pasted JSON there
        elif settings.GOOGLE_APPLICATION_CREDENTIALS and settings.GOOGLE_APPLICATION_CREDENTIALS.strip().startswith("{"):
            logger.info("[METHOD 2] Attempting to load from raw JSON string in GOOGLE_APPLICATION_CREDENTIALS...")
            try:
                creds_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS.strip())
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_info, scopes=self.scopes
                )
                logger.info("✅ Successfully loaded credentials from raw JSON string in GOOGLE_APPLICATION_CREDENTIALS")
            except Exception as e:
                self.init_error = f"Failed parsing GOOGLE_APPLICATION_CREDENTIALS JSON string: {str(e)}"
                logger.warning(f"❌ {self.init_error}")

        # METHOD 3: Standard File Path checking (Render Secret Files mount or physical disk)
        if not self.credentials:
            logger.info("[METHOD 3] Scanning file paths for credentials.json...")
            candidate_paths = [
                "/etc/secrets/credentials.json",  # Render Secret Files target mount
                settings.GOOGLE_APPLICATION_CREDENTIALS,
                "credentials.json",
                os.path.join(os.getcwd(), "credentials.json"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials.json"),
                "../credentials.json",
                "../../credentials.json"
            ]
            
            file_found = False
            for path in candidate_paths:
                if os.path.exists(path):
                    file_found = True
                    logger.info(f"  ✅ Found file candidate at: {path}")
                    try:
                        self.credentials = service_account.Credentials.from_service_account_file(
                            path, scopes=self.scopes
                        )
                        logger.info(f"✅ Successfully loaded credentials from file: {path}")
                        self.init_error = None
                        break
                    except Exception as e:
                        logger.warning(f"  ❌ File found but failed to load Service Account info: {e}")
                        self.init_error = f"File found at {path} but contains invalid Service Account formatting: {str(e)}"
            
            if not file_found and not self.init_error:
                self.init_error = "No credentials.json file found on disk, and GOOGLE_CREDENTIALS_JSON environment variable is empty."

        # INITIALIZE SERVICE OBJECT
        if self.credentials:
            try:
                self.service = build('drive', 'v3', credentials=self.credentials)
                logger.info("✅ Google Drive API v3 service successfully built.")
                return True
            except Exception as e:
                self.service = None
                self.init_error = f"Failed to build Google Drive API resource client: {str(e)}"
                logger.error(f"❌ {self.init_error}")
                return False
        else:
            self.service = None
            logger.error("❌ CRITICAL: Credentials could not be loaded.")
            return False

    def search_files(self, q: str) -> str:
        """
        Executes a search query against the Google Drive API using files().list()
        Dynamically attempts initialization recovery if state is missing.
        Implements an advanced multi-pass broad discovery fallback to ensure real files are returned
        and absolute prevention of LLM credential hallucination messages.
        """
        logger.info(f"\n[SEARCH REQUEST] Requested Query Filter: {q}")
        
        # Lazy initialization recovery attempt per request
        if not self.service:
            logger.info("Service missing. Attempting dynamic recovery load...")
            self.initialize()
            
        # If still missing after dynamic attempt, return a highly precise directive instructing the agent exactly what to communicate
        if not self.service:
            err_details = self.init_error or "Unknown initialization error"
            directive = (
                f"CRITICAL SYSTEM ERROR: Google Drive authentication failed on the backend server. "
                f"Diagnostic details: '{err_details}'. "
                f"INSTRUCTION FOR ASSISTANT: Do not ask the user for their email or password. "
                f"Instead, output exactly this message formatted cleanly to the user: "
                f"'⚠️ **Backend Configuration Notice:** The deployed server on Render could not locate your Google Drive service account credentials. "
                f"To resolve this, please open your Render Dashboard, select your Web Service, and either add the `GOOGLE_CREDENTIALS_JSON` environment variable containing your JSON string, or upload `credentials.json` via the Secret Files tab as detailed in the project deployment documentation.'"
            )
            return directive
            
        try:
            # Pass 1: Build specific query securely mapping optional folder target
            query_parts = []
            if self.folder_id:
                query_parts.append(f"'{self.folder_id}' in parents")
            if q and q.strip():
                # Ensure query parameters conform to Google Drive API v3 string specifications
                clean_q = q.strip()
                query_parts.append(f"({clean_q})")
                
            final_query = " and ".join(query_parts) if query_parts else None
            logger.info(f"[SEARCH EXECUTION - PASS 1] Specific query syntax: {final_query}")
            
            results = self.service.files().list(
                q=final_query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, webViewLink)',
                pageSize=20,
                orderBy='modifiedTime desc'
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"✅ Pass 1 Specific Search returned {len(files)} matches.")
            
            # Pass 2: Broad Fallback Discovery if exact filter returned zero matches
            if not files and self.folder_id:
                logger.info("[SEARCH EXECUTION - PASS 2] Pass 1 returned empty. Executing broad folder contents discovery...")
                broad_query = f"'{self.folder_id}' in parents"
                broad_results = self.service.files().list(
                    q=broad_query,
                    spaces='drive',
                    fields='files(id, name, mimeType, modifiedTime, webViewLink)',
                    pageSize=20,
                    orderBy='modifiedTime desc'
                ).execute()
                
                broad_files = broad_results.get('files', [])
                logger.info(f"✅ Pass 2 Broad Folder Discovery returned {len(broad_files)} available files.")
                
                if broad_files:
                    # Return the available files along with a clear context directive instructing the LLM to present them
                    return json.dumps({
                        "status": "SUCCESS", 
                        "files": broad_files,
                        "directive_for_agent": (
                            f"CRITICAL ASSISTANT DIRECTIVE: No files matched the strict user filter '{q}', "
                            f"but actual files WERE discovered in the shared Google Drive folder. "
                            f"DO NOT claim you lack credentials. Present these discovered files beautifully as a Markdown list to the user."
                        )
                    })
                else:
                    # Folder is entirely empty or permissions are uninherited
                    empty_directive = (
                        f"CRITICAL ASSISTANT DIRECTIVE: Authentication succeeded perfectly, but ZERO files exist inside the shared Google Drive folder. "
                        f"DO NOT claim you lack credentials. Output exactly this friendly explanation to the user: "
                        f"'📂 **Google Drive Connected Successfully:** I can read your shared folder, but it appears to be completely empty. Please upload files directly into your shared Drive folder or ensure the uploaded files inherit link-sharing read visibility for the Service Account.'"
                    )
                    return empty_directive
            
            # Return discovered specific matches safely
            return json.dumps({"status": "SUCCESS", "files": files})
            
        except HttpError as e:
            err_msg = f"Google Drive API returned HttpError {e.resp.status}: {e.resp.reason}"
            logger.error(f"❌ {err_msg}")
            # Format error as explicit instruction to avoid LLM misinterpreting it as missing credentials
            return f"CRITICAL ASSISTANT DIRECTIVE: Output exactly this text to the user: '❌ **Google Drive API Permission Denied ({e.resp.status}):** Ensure your Service Account email is added as a Viewer directly on the shared folder settings.'"
        except Exception as e:
            logger.error(f"❌ Search execution exception: {str(e)}")
            return f"CRITICAL ASSISTANT DIRECTIVE: Output exactly this text to the user: '❌ **Search Processing Exception:** {str(e)}'"

# Singleton export
drive_service = DriveService()
