"""
CV Generator - Turn AI outputs into Google Docs
"""
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CVGenerator:
    """
    Handles the creation of Google Docs based on AI-generated content.
    """
    
    def __init__(self):
        self.credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self._service = None

    def _get_service(self):
        """
        Lazy-load the Google Docs service
        """
        if self._service is None:
            try:
                credentials = Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=[
                        'https://www.googleapis.com/auth/documents',
                        'https://www.googleapis.com/auth/drive.file'
                    ]
                )
                self._service = build('docs', 'v1', credentials=credentials)
            except FileNotFoundError:
                raise FileNotFoundError(f"Google credentials not found: {self.credentials_path}")
            except Exception as e:
                raise Exception(f"Failed to initialize Google Docs service: {e}")
        
        return self._service

    def create_google_doc(self, cv_content: str, title: str) -> str:
        """
        Create a new Google Document with the specified content and title.
        Formats the CV with proper styling.

        Returns the URL of the created document.
        """
        try:
            service = self._get_service()
            
            # Create document
            document = service.documents().create(
                body={
                    'title': title
                }
            ).execute()

            document_id = document.get('documentId')
            print(f"Created document with ID: {document_id}")

            # Parse CV content if it's JSON
            cv_data = self._parse_cv_content(cv_content)
            
            # Generate formatted content
            formatted_content = self._format_cv_content(cv_data)
            
            # Insert content with formatting
            requests = self._build_formatting_requests(formatted_content)
            
            if requests:
                service.documents().batchUpdate(
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
    
    def _format_cv_content(self, cv_data: dict) -> str:
        """Format CV data into a clean, ATS-friendly document"""
        if 'raw_content' in cv_data:
            return cv_data['raw_content']
        
        content = []
        
        # Personal Information
        if 'personal_info' in cv_data:
            info = cv_data['personal_info']
            content.append(f"{info.get('name', '')}")  # Name as title
            
            contact = []
            if info.get('email'): contact.append(info['email'])
            if info.get('phone'): contact.append(info['phone'])
            if info.get('location'): contact.append(info['location'])
            
            if contact:
                content.append(' | '.join(contact))
            content.append('')  # Empty line
        
        # Professional Summary
        if cv_data.get('professional_summary'):
            content.append('PROFESSIONAL SUMMARY')
            content.append(cv_data['professional_summary'])
            content.append('')
        
        # Skills
        if cv_data.get('skills'):
            content.append('CORE SKILLS')
            skills_text = ' • '.join(cv_data['skills'])
            content.append(skills_text)
            content.append('')
        
        # Experience
        if cv_data.get('experience'):
            content.append('PROFESSIONAL EXPERIENCE')
            for exp in cv_data['experience']:
                content.append(f"{exp.get('title', '')} | {exp.get('company', '')}")
                if exp.get('duration'):
                    content.append(exp['duration'])
                
                if exp.get('achievements'):
                    for achievement in exp['achievements']:
                        content.append(f"• {achievement}")
                content.append('')
        
        # Education
        if cv_data.get('education'):
            content.append('EDUCATION')
            for edu in cv_data['education']:
                edu_line = []
                if edu.get('degree'): edu_line.append(edu['degree'])
                if edu.get('school'): edu_line.append(edu['school'])
                if edu.get('year'): edu_line.append(str(edu['year']))
                
                if edu_line:
                    content.append(' | '.join(edu_line))
            content.append('')
        
        return '\n'.join(content)
    
    def _build_formatting_requests(self, content: str) -> list:
        """Build Google Docs formatting requests for better styling"""
        requests = []
        
        # Insert the main content
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        })
        
        # Add basic formatting (this is simplified - real implementation would be more complex)
        # For now, just insert the content cleanly
        
        return requests
    
    def create_formatted_cv(self, cv_json: dict, title: str) -> str:
        """Create a Google Doc with structured CV data and professional formatting"""
        try:
            service = self._get_service()
            
            # Create document
            document = service.documents().create(
                body={'title': title}
            ).execute()
            
            document_id = document.get('documentId')
            
            # Build content with proper structure
            content_requests = self._build_structured_cv_requests(cv_json)
            
            if content_requests:
                service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': content_requests}
                ).execute()
            
            return f"https://docs.google.com/document/d/{document_id}"
            
        except Exception as e:
            raise Exception(f"Failed to create formatted CV: {e}")
    
    def _build_structured_cv_requests(self, cv_data: dict) -> list:
        """Build detailed formatting requests for professional CV layout"""
        requests = []
        current_index = 1
        
        # Personal Info (Header)
        if 'personal_info' in cv_data:
            info = cv_data['personal_info']
            name = info.get('name', '')
            
            # Insert name
            if name:
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': f"{name}\n"
                    }
                })
                
                # Bold the name
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + len(name)
                        },
                        'textStyle': {
                            'bold': True,
                            'fontSize': {'magnitude': 16, 'unit': 'PT'}
                        },
                        'fields': 'bold,fontSize'
                    }
                })
                
                current_index += len(name) + 1
            
            # Contact info
            contact_parts = []
            if info.get('email'): contact_parts.append(info['email'])
            if info.get('phone'): contact_parts.append(info['phone'])
            if info.get('location'): contact_parts.append(info['location'])
            
            if contact_parts:
                contact_text = ' | '.join(contact_parts) + '\n\n'
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': contact_text
                    }
                })
                current_index += len(contact_text)
        
        # Add sections
        sections = [
            ('PROFESSIONAL SUMMARY', cv_data.get('professional_summary', '')),
            ('CORE SKILLS', ' • '.join(cv_data.get('skills', []))),
        ]
        
        for section_title, section_content in sections:
            if section_content:
                # Section header
                header_text = f"{section_title}\n"
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': header_text
                    }
                })
                
                # Bold section header
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + len(section_title)
                        },
                        'textStyle': {'bold': True},
                        'fields': 'bold'
                    }
                })
                
                current_index += len(header_text)
                
                # Section content
                content_text = f"{section_content}\n\n"
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': content_text
                    }
                })
                current_index += len(content_text)
        
        return requests
