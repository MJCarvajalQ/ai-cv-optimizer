"""
CV Generator with OAuth Authentication - Turn AI outputs into Google Docs
"""
import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from professional_cv_formatter import ProfessionalCVFormatter

class CVGeneratorOAuth:
    """
    Handles the creation of Google Docs based on AI-generated content using OAuth.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    def __init__(self, language='english'):
        self.oauth_credentials_path = os.getenv('GOOGLE_OAUTH_CREDENTIALS_PATH', 'oauth_credentials.json')
        self.token_path = 'token.pickle'
        self.language = language.lower()
        self._docs_service = None
        self._drive_service = None

    def _get_credentials(self):
        """Get OAuth credentials, refreshing or creating as needed"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing OAuth token...")
                creds.refresh(Request())
            else:
                print("Getting new OAuth credentials...")
                print("This will open a browser window for authentication.")
                
                if not os.path.exists(self.oauth_credentials_path):
                    raise FileNotFoundError(
                        f"OAuth credentials file not found: {self.oauth_credentials_path}\\n"
                        f"Please follow the setup instructions in OAUTH_SETUP.md"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.oauth_credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds

    def _get_docs_service(self):
        """Lazy-load the Google Docs service"""
        if self._docs_service is None:
            creds = self._get_credentials()
            self._docs_service = build('docs', 'v1', credentials=creds)
        return self._docs_service

    def _get_drive_service(self):
        """Lazy-load the Google Drive service"""  
        if self._drive_service is None:
            creds = self._get_credentials()
            self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    def create_google_doc(self, cv_content: str, title: str, language: str = None, folder_id: str = None) -> str:
        """
        Create a new Google Document with the specified content and title.
        Formats the CV with proper styling.

        Returns the URL of the created document.
        """
        try:
            docs_service = self._get_docs_service()
            
            # Create document
            document = docs_service.documents().create(
                body={'title': title}
            ).execute()
            
            # Move to folder if specified
            if folder_id:
                drive_service = self._get_drive_service()
                document_id = document.get('documentId')
                
                # Move the document to the specified folder
                file = drive_service.files().get(fileId=document_id, fields='parents').execute()
                previous_parents = ",".join(file.get('parents'))
                
                drive_service.files().update(
                    fileId=document_id,
                    addParents=folder_id,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()
                
                print(f"📁 Moved document to folder: {folder_id}")

            document_id = document.get('documentId')
            print(f"Created document with ID: {document_id}")

            # Parse CV content if it's JSON
            cv_data = self._parse_cv_content(cv_content)
            
            # Generate formatted content requests with language support
            doc_language = language or self.language
            requests = self._build_structured_cv_requests(cv_data, doc_language)
            
            if requests:
                docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()

            # Return the URL of the document
            return f"https://docs.google.com/document/d/{document_id}"
            
        except HttpError as e:
            raise Exception(f"Google Docs API error: {e}")
        except Exception as e:
            raise Exception(f"Failed to create Google Doc: {e}")
    
    def _parse_cv_content(self, content: str) -> dict:
        """Parse AI-generated CV content (JSON or plain text)"""
        try:
            # Try to parse as JSON first
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, treat as plain text
            return {'raw_content': content}
    
    def create_drive_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """Create a folder in Google Drive and return its ID"""
        try:
            drive_service = self._get_drive_service()
            
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = drive_service.files().create(
                body=folder_metadata,
                fields='id, name'
            ).execute()
            
            folder_id = folder.get('id')
            folder_name = folder.get('name')
            print(f"📁 Created folder '{folder_name}' with ID: {folder_id}")
            
            return folder_id
            
        except HttpError as e:
            raise Exception(f"Google Drive API error: {e}")
        except Exception as e:
            raise Exception(f"Failed to create folder: {e}")
    
    def find_or_create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """Find existing folder or create a new one"""
        try:
            drive_service = self._get_drive_service()
            
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = drive_service.files().list(
                q=query,
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                # Folder exists, return its ID
                folder_id = files[0].get('id')
                print(f"📁 Found existing folder '{folder_name}' with ID: {folder_id}")
                return folder_id
            else:
                # Folder doesn't exist, create it
                return self.create_drive_folder(folder_name, parent_folder_id)
                
        except HttpError as e:
            raise Exception(f"Google Drive API error: {e}")
        except Exception as e:
            raise Exception(f"Failed to find or create folder: {e}")

    def _build_structured_cv_requests(self, cv_data: dict, language: str = 'english') -> list:
        """Build detailed formatting requests using Professional CV style"""
        # Use Professional formatter for clean layout with language support
        formatter = ProfessionalCVFormatter(language=language)
        return formatter.build_professional_cv_requests(cv_data)
