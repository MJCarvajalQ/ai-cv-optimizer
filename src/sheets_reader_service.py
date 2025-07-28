"""
Google Sheets Reader - Read job data from Google Sheets using Service Account
"""
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional

class SheetsReader:
    """
    Reads job data from Google Sheets using Service Account authentication.
    This is more suitable for automated access.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly'
    ]
    
    def __init__(self):
        self.credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self._sheets_service = None

    def _get_credentials(self):
        """Get service account credentials"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Service account credentials file not found: {self.credentials_path}\n"
                f"Please make sure credentials.json is in the project root"
            )
        
        # Load service account credentials
        credentials = Credentials.from_service_account_file(
            self.credentials_path, 
            scopes=self.SCOPES
        )
        
        return credentials

    def _get_sheets_service(self):
        """Lazy-load the Google Sheets service"""
        if self._sheets_service is None:
            creds = self._get_credentials()
            self._sheets_service = build('sheets', 'v4', credentials=creds)
        return self._sheets_service

    def get_service_account_email(self):
        """Get the service account email for sharing instructions"""
        try:
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
                return creds_data.get('client_email', 'Unknown')
        except Exception:
            return 'Unknown'

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
                    print(f"📧 Make sure to share the sheet with: {self.get_service_account_email()}")
                    print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                    return False
                elif e.resp.status == 403:
                    print(f"❌ Permission denied accessing the sheet.")
                    print(f"📧 Make sure to share the sheet with: {self.get_service_account_email()}")
                    print(f"   Give 'Viewer' permission to this email address.")
                    return False
                else:
                    print(f"❌ HTTP Error {e.resp.status}: {e}")
                    return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def read_jobs_from_sheet(self, spreadsheet_id: str, range_name: str = 'Sheet1!A:D') -> List[Dict]:
        """
        Read job data from Google Sheet.
        
        Expected columns:
        A: Company Name
        B: Job Title
        C: Job Description
        D: Requirements
        
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
                if len(row) >= 4:  # Ensure we have all required columns
                    job = {
                        'row_number': i,
                        'company': row[0].strip() if row[0] else '',
                        'title': row[1].strip() if row[1] else '',
                        'description': row[2].strip() if row[2] else '',
                        'requirements': row[3].strip() if row[3] else ''
                    }
                    jobs.append(job)
                elif len(row) >= 2:  # At least company and title
                    job = {
                        'row_number': i,
                        'company': row[0].strip() if row[0] else '',
                        'title': row[1].strip() if row[1] else '',
                        'description': row[2].strip() if len(row) > 2 and row[2] else '',
                        'requirements': row[3].strip() if len(row) > 3 and row[3] else ''
                    }
                    jobs.append(job)
            
            print(f"✅ Successfully read {len(jobs)} jobs from the sheet.")
            return jobs
            
        except HttpError as e:
            print(f"❌ Google Sheets API error: {e}")
            if e.resp.status == 403:
                print(f"📧 Make sure to share the sheet with: {self.get_service_account_email()}")
            return []
        except Exception as e:
            print(f"❌ Failed to read from Google Sheet: {e}")
            return []

    def get_job_by_row(self, spreadsheet_id: str, row_number: int, range_name: str = 'Sheet1!A:D') -> Optional[Dict]:
        """Get a specific job by row number"""
        jobs = self.read_jobs_from_sheet(spreadsheet_id, range_name)
        for job in jobs:
            if job['row_number'] == row_number:
                return job
        return None

    def list_jobs(self, spreadsheet_id: str, range_name: str = 'Sheet1!A:D') -> None:
        """Print a list of all jobs in the sheet"""
        jobs = self.read_jobs_from_sheet(spreadsheet_id, range_name)
        
        if not jobs:
            print("No jobs found in the sheet.")
            print(f"\n📧 Make sure to:")
            print(f"   1. Share the sheet with: {self.get_service_account_email()}")
            print(f"   2. Give 'Viewer' permission to this email")
            print(f"   3. Check that your sheet has data in columns A-D")
            return
        
        print(f"\nFound {len(jobs)} jobs in the sheet:")
        print("-" * 80)
        
        for job in jobs:
            print(f"Row {job['row_number']}: {job['company']} - {job['title']}")
            if job['description']:
                preview = job['description'][:100] + "..." if len(job['description']) > 100 else job['description']
                print(f"    Description: {preview}")
            print()
