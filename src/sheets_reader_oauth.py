"""
Google Sheets Reader - OAuth Version
Read job data from Google Sheets using OAuth authentication (same as CV generator)
"""
import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional

class SheetsReaderOAuth:
    """
    Reads job data from Google Sheets using OAuth authentication.
    Uses the same OAuth setup as CVGeneratorOAuth for consistency.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    def __init__(self):
        self.oauth_credentials_path = os.getenv('GOOGLE_OAUTH_CREDENTIALS_PATH', 'oauth_credentials.json')
        self.token_path = 'token.pickle'
        self._sheets_service = None

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
                        f"OAuth credentials file not found: {self.oauth_credentials_path}\n"
                        f"Please follow the setup instructions in OAUTH_SETUP.md"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.oauth_credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds

    def _get_sheets_service(self):
        """Lazy-load the Google Sheets service"""
        if self._sheets_service is None:
            creds = self._get_credentials()
            self._sheets_service = build('sheets', 'v4', credentials=creds)
        return self._sheets_service

    def test_sheet_access(self, spreadsheet_id: str):
        """Test if we can access the sheet and provide helpful error messages"""
        try:
            service = self._get_sheets_service()
            
            # Try to get spreadsheet metadata first
            try:
                spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                title = spreadsheet.get('properties', {}).get('title', 'Unknown')
                print(f"✅ Successfully accessed sheet: '{title}'")
                return True
            except HttpError as e:
                if e.resp.status == 404:
                    print(f"❌ Sheet not found or not accessible.")
                    print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                    print(f"📧 Make sure you have access to this sheet with your Google account")
                    return False
                elif e.resp.status == 403:
                    print(f"❌ Permission denied accessing the sheet.")
                    print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                    print(f"📧 Make sure you have access to this sheet with your Google account")
                    return False
                else:
                    print(f"❌ HTTP Error {e.resp.status}: {e}")
                    return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def read_jobs_from_sheet(self, spreadsheet_id: str, range_name: str = 'Sheet1!A:I') -> List[Dict]:
        """
        Read job data from Google Sheet.
        
        Expected columns:
        A: Job Title
        B: Company
        C: Job Description
        D: Job URL
        E: Location
        F: CV Generated
        G: Status
        H: Notes
        I: Last Updated
        
        Returns list of job dictionaries.
        """
        try:
            service = self._get_sheets_service()
            
            # First test access
            if not self.test_sheet_access(spreadsheet_id):
                return []
            
            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id, 
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print('No data found in the sheet.')
                return []
            
            print(f"📊 Found {len(values)} rows in the sheet")
            if len(values) > 0:
                print(f"📋 Header row: {values[0]}")
            
            jobs = []
            # Skip header row (first row)
            for i, row in enumerate(values[1:], start=2):
                if len(row) >= 2:  # At least job title and company
                    # Handle your actual column layout: Job Title, Company, Job Description, Job URL, Location, Status
                    job = {
                        'row_number': i,
                        'title': row[0].strip() if len(row) > 0 and row[0] else '',  # Job Title (Column A)
                        'company': row[1].strip() if len(row) > 1 and row[1] else '',  # Company (Column B)
                        'description': row[2].strip() if len(row) > 2 and row[2] else '',  # Job Description (Column C)
                        'url': row[3].strip() if len(row) > 3 and row[3] else '',  # Job URL (Column D)
                        'location': row[4].strip() if len(row) > 4 and row[4] else '',  # Location (Column E)
                        'status': row[5].strip() if len(row) > 5 and row[5] else '',  # Status (Column F)
                        'requirements': row[2].strip() if len(row) > 2 and row[2] else ''  # Use description as requirements for AI
                    }
                    jobs.append(job)
            
            print(f"✅ Successfully read {len(jobs)} jobs from the sheet.")
            return jobs
            
        except HttpError as e:
            print(f"❌ Google Sheets API error: {e}")
            if e.resp.status == 403:
                print(f"📧 Make sure you have access to this sheet with your Google account")
            return []
        except Exception as e:
            print(f"❌ Failed to read from Google Sheet: {e}")
            return []

    def get_job_by_row(self, spreadsheet_id: str, row_number: int, range_name: str = 'Sheet1!A:E') -> Optional[Dict]:
        """Get a specific job by row number"""
        jobs = self.read_jobs_from_sheet(spreadsheet_id, range_name)
        for job in jobs:
            if job['row_number'] == row_number:
                return job
        return None

    def update_job_status(self, spreadsheet_id: str, row_number: int, cv_generated_url: str, status: str = "Applied", notes: str = "", sheet_name: str = 'Sheet1') -> bool:
        """Update multiple columns for job tracking"""
        try:
            import datetime
            service = self._get_sheets_service()
            
            # Update columns F (CV Generated), G (Status), H (Notes), I (Last Updated)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Prepare data for columns F through I
            values = [
                cv_generated_url,  # Column F: CV Generated (URL to the document)
                status,            # Column G: Status
                notes,             # Column H: Notes
                current_time       # Column I: Last Updated
            ]
            
            range_name = f"{sheet_name}!F{row_number}:I{row_number}"
            
            body = {
                'values': [values]
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Updated row {row_number}: CV Generated, Status: {status}, Updated: {current_time}")
            return True
            
        except HttpError as e:
            print(f"❌ Failed to update job tracking: {e}")
            if e.resp.status == 403:
                print(f"📧 Make sure you have edit access to this sheet with your Google account")
            return False
        except Exception as e:
            print(f"❌ Unexpected error updating job status: {e}")
            return False

    def list_jobs(self, spreadsheet_id: str):
        """List all jobs in the spreadsheet"""
        jobs = self.read_jobs_from_sheet(spreadsheet_id)
        
        if not jobs:
            print("❌ No jobs found in the spreadsheet")
            return
        
        print(f"\n📋 Jobs in the spreadsheet:")
        print("-" * 80)
        for job in jobs:
            status = job.get('status', 'No Status')
            print(f"Row {job['row_number']}: {job['company']} - {job['title']} ({status})")
            if job.get('location'):
                print(f"    📍 Location: {job['location']}")
            if job.get('url'):
                print(f"    🔗 URL: {job['url']}")
            print()
        
        print(f"✅ Total: {len(jobs)} jobs found")
