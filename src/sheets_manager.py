"""
Google Sheets Manager - Handle job tracking and data management
"""
import os
import pandas as pd
from typing import Dict, List, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsManager:
    """Manages Google Sheets integration for job tracking"""
    
    def __init__(self):
        self.sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        self.credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self._service = None
        
        if not self.sheets_id:
            raise ValueError("GOOGLE_SHEETS_ID not found in environment variables")
    
    def _get_service(self):
        """Initialize Google Sheets service with lazy loading"""
        if self._service is None:
            try:
                # Define the scope
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive.file'
                ]
                
                # Load credentials
                credentials = Credentials.from_service_account_file(
                    self.credentials_path, 
                    scopes=scopes
                )
                
                # Build service
                self._service = build('sheets', 'v4', credentials=credentials)
                
            except FileNotFoundError:
                raise FileNotFoundError(f"Google credentials not found: {self.credentials_path}")
            except Exception as e:
                raise Exception(f"Failed to initialize Google Sheets service: {e}")
        
        return self._service
    
    def get_all_jobs(self) -> pd.DataFrame:
        """Retrieve all job data from the spreadsheet"""
        try:
            service = self._get_service()
            
            # Read data from the sheet
            result = service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range='Sheet1!A1:Z1000'  # Adjust range as needed
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return pd.DataFrame()
            
            # Convert to DataFrame
            headers = values[0]
            data = values[1:] if len(values) > 1 else []
            
            # Pad rows to match header length
            padded_data = []
            for row in data:
                padded_row = row + [''] * (len(headers) - len(row))
                padded_data.append(padded_row[:len(headers)])
            
            df = pd.DataFrame(padded_data, columns=headers)
            return df
            
        except HttpError as e:
            raise Exception(f"Google Sheets API error: {e}")
        except Exception as e:
            raise Exception(f"Failed to retrieve job data: {e}")
    
    def get_job(self, job_id: int) -> pd.DataFrame:
        """Get specific job by row number (1-based)"""
        all_jobs = self.get_all_jobs()
        
        if job_id <= 0 or job_id > len(all_jobs):
            return pd.DataFrame()
        
        return all_jobs.iloc[[job_id - 1]]  # Convert to 0-based index
    
    def get_pending_jobs(self) -> pd.DataFrame:
        """Get jobs that don't have CVs generated yet"""
        all_jobs = self.get_all_jobs()
        
        if all_jobs.empty:
            return all_jobs
        
        # Filter jobs without CV generated
        if 'CV Generated' in all_jobs.columns:
            pending = all_jobs[all_jobs['CV Generated'].isna() | (all_jobs['CV Generated'] == '')]
        else:
            # If no CV Generated column, assume all are pending
            pending = all_jobs
        
        return pending
    
    def update_job_status(self, job_id: int, cv_link: str = None, status: str = None, notes: str = None):
        """Update job status and CV information"""
        try:
            service = self._get_service()
            
            # Prepare updates
            updates = []
            
            if cv_link:
                # Update CV Generated column (assuming column F)
                updates.append({
                    'range': f'Sheet1!F{job_id + 1}',  # +1 for header row
                    'values': [[cv_link]]
                })
            
            if status:
                # Update Status column (assuming column G)
                updates.append({
                    'range': f'Sheet1!G{job_id + 1}',
                    'values': [[status]]
                })
            
            if notes:
                # Update Notes column (assuming column H)
                updates.append({
                    'range': f'Sheet1!H{job_id + 1}',
                    'values': [[notes]]
                })
            
            # Add timestamp (assuming column I)
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updates.append({
                'range': f'Sheet1!I{job_id + 1}',
                'values': [[timestamp]]
            })
            
            if updates:
                # Batch update
                body = {
                    'valueInputOption': 'RAW',
                    'data': updates
                }
                
                service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.sheets_id,
                    body=body
                ).execute()
        
        except Exception as e:
            raise Exception(f"Failed to update job {job_id}: {e}")
    
    def add_job(self, job_data: Dict[str, str]) -> int:
        """Add a new job to the spreadsheet"""
        try:
            service = self._get_service()
            
            # Get current data to find next row
            current_data = self.get_all_jobs()
            next_row = len(current_data) + 2  # +1 for header, +1 for next empty row
            
            # Prepare row data based on expected columns
            row_data = [
                job_data.get('job_title', ''),
                job_data.get('company', ''),
                job_data.get('job_description', ''),
                job_data.get('job_url', ''),
                job_data.get('location', ''),
                '',  # CV Generated (empty initially)
                'Pending',  # Status
                '',  # Notes
                '',  # Timestamp (will be updated when processed)
            ]
            
            # Add the row
            service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f'Sheet1!A{next_row}:I{next_row}',
                valueInputOption='RAW',
                body={'values': [row_data]}
            ).execute()
            
            return next_row - 1  # Return 1-based job ID
            
        except Exception as e:
            raise Exception(f"Failed to add job: {e}")
    
    def create_sheets_template(self):
        """Create the initial spreadsheet structure"""
        try:
            service = self._get_service()
            
            # Define headers
            headers = [
                'Job Title',
                'Company', 
                'Job Description',
                'Job URL',
                'Location',
                'CV Generated',
                'Status',
                'Notes',
                'Last Updated'
            ]
            
            # Clear and set headers
            service.spreadsheets().values().clear(
                spreadsheetId=self.sheets_id,
                range='Sheet1!A1:Z1000'
            ).execute()
            
            service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range='Sheet1!A1:I1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            # Format headers (bold)
            format_body = {
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 9
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {'bold': True},
                                'backgroundColor': {
                                    'red': 0.9,
                                    'green': 0.9, 
                                    'blue': 0.9
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                }]
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheets_id,
                body=format_body
            ).execute()
            
            print("✅ Spreadsheet template created successfully!")
            
        except Exception as e:
            raise Exception(f"Failed to create spreadsheet template: {e}")
    
    def validate_connection(self) -> bool:
        """Test connection to Google Sheets"""
        try:
            service = self._get_service()
            
            # Try to get spreadsheet metadata
            service.spreadsheets().get(
                spreadsheetId=self.sheets_id
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Connection validation failed: {e}")
            return False
