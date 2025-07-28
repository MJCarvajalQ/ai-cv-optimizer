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
        'https://www.googleapis.com/auth/spreadsheets'  # Full read/write access for status updates
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
                print(f"📧 Make sure to share the sheet with: {self.get_service_account_email()}")
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
                print(f"📧 Make sure to share the sheet with EDITOR permission: {self.get_service_account_email()}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error updating job tracking: {e}")
            return False

    def list_jobs(self, spreadsheet_id: str, range_name: str = 'Sheet1!A:E') -> None:
        """Print a list of all jobs in the sheet"""
        jobs = self.read_jobs_from_sheet(spreadsheet_id, range_name)
        
        if not jobs:
            print("No jobs found in the sheet.")
            print(f"\n📧 Make sure to:")
            print(f"   1. Share the sheet with: {self.get_service_account_email()}")
            print(f"   2. Give 'EDITOR' permission to this email (for status updates)")
            print(f"   3. Check that your sheet has data in columns A-E")
            print(f"   \n📋 Expected columns:")
            print(f"      A: Job Title")
            print(f"      B: Company")
            print(f"      C: Job Description")
            print(f"      D: Job URL")
            print(f"      E: Status (optional)")
            return
        
        print(f"\nFound {len(jobs)} jobs in the sheet:")
        print("-" * 80)
        
        for job in jobs:
            status_display = f" [{job['status']}]" if job['status'] else ""
            print(f"Row {job['row_number']}: {job['company']} - {job['title']}{status_display}")
            if job['url']:
                print(f"    URL: {job['url']}")
            if job['description']:
                preview = job['description'][:100] + "..." if len(job['description']) > 100 else job['description']
                print(f"    Description: {preview}")
            print()
