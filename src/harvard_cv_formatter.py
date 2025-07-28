"""
Harvard-style CV Formatter for Google Docs
Professional, clean layout following Harvard career services guidelines
"""

import json
from typing import List, Dict, Any

class HarvardCVFormatter:
    """
    Formats CVs according to Harvard Business School and Harvard career services guidelines:
    - Clean, minimalist design
    - Left-aligned headers
    - Consistent spacing
    - Professional fonts
    - Clear hierarchy
    """
    
    def __init__(self):
        self.current_index = 1
        
    def build_harvard_cv_requests(self, cv_data: dict) -> list:
        """Build formatting requests following Harvard CV style guidelines"""
        requests = []
        self.current_index = 1
        
        # Handle raw content fallback
        if 'raw_content' in cv_data:
            return self._handle_raw_content(cv_data['raw_content'])
        
        # 1. Header Section (Name and Contact)
        requests.extend(self._create_header_section(cv_data.get('personal_info', {})))
        
        # 2. Professional Summary (Optional)
        if cv_data.get('professional_summary'):
            requests.extend(self._create_summary_section(cv_data['professional_summary']))
        
        # 3. Core sections in Harvard-recommended order
        sections = [
            ('EXPERIENCE', self._format_experience_harvard, cv_data.get('experience', [])),
            ('EDUCATION', self._format_education_harvard, cv_data.get('education', [])),
            ('SKILLS', self._format_skills_harvard, cv_data.get('skills', [])),
            ('PROJECTS', self._format_projects_harvard, cv_data.get('projects', [])),
            ('CERTIFICATIONS', self._format_certifications_harvard, cv_data.get('certifications_courses', [])),
            ('LANGUAGES', self._format_languages_harvard, cv_data.get('languages', [])),
            ('AWARDS & HONORS', self._format_awards_harvard, cv_data.get('awards', []))
        ]
        
        for section_title, formatter_func, data in sections:
            if data:
                requests.extend(self._create_section(section_title, formatter_func(data)))
        
        return requests
    
    def _handle_raw_content(self, content: str) -> list:
        """Handle raw text content with basic formatting"""
        return [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
    
    def _create_header_section(self, personal_info: dict) -> list:
        """Create Harvard-style header with name and contact info"""
        requests = []
        
        name = personal_info.get('name', '')
        if not name:
            return requests
        
        # Name - large, bold, left-aligned
        name_text = f"{name}\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': name_text
            }
        })
        
        # Style the name
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(name)
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': 16, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        })
        
        # Left align name (Harvard style)
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(name_text)
                },
                'paragraphStyle': {
                    'alignment': 'START'
                },
                'fields': 'alignment'
            }
        })
        
        self.current_index += len(name_text)
        
        # Contact information - single line, clean
        contact_parts = []
        if personal_info.get('email'): 
            contact_parts.append(personal_info['email'])
        if personal_info.get('phone'): 
            contact_parts.append(personal_info['phone'])
        if personal_info.get('location'): 
            contact_parts.append(personal_info['location'])
        if personal_info.get('linkedin'): 
            contact_parts.append(f"LinkedIn: {personal_info['linkedin']}")
        
        if contact_parts:
            contact_text = ' | '.join(contact_parts) + '\n\n'
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': contact_text
                }
            })
            
            # Style contact info
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': self.current_index,
                        'endIndex': self.current_index + len(contact_text) - 2
                    },
                    'textStyle': {
                        'fontSize': {'magnitude': 11, 'unit': 'PT'}
                    },
                    'fields': 'fontSize'
                }
            })
            
            self.current_index += len(contact_text)
        
        return requests
    
    def _create_summary_section(self, summary: str) -> list:
        """Create professional summary section"""
        if not summary:
            return []
        
        requests = []
        
        # No header for summary in Harvard style, just the content
        summary_text = f"{summary}\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': summary_text
            }
        })
        
        # Style summary
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(summary_text) - 2
                },
                'textStyle': {
                    'fontSize': {'magnitude': 11, 'unit': 'PT'}
                },
                'fields': 'fontSize'
            }
        })
        
        self.current_index += len(summary_text)
        return requests
    
    def _create_section(self, title: str, content: str) -> list:
        """Create a section with Harvard-style formatting"""
        if not content:
            return []
        
        requests = []
        
        # Section header - bold, left-aligned, with underline
        header_text = f"{title}\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': header_text
            }
        })
        
        # Style section header
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(title)
                },
                'textStyle': {
                    'bold': True,
                    'underline': True,
                    'fontSize': {'magnitude': 12, 'unit': 'PT'}
                },
                'fields': 'bold,underline,fontSize'
            }
        })
        
        self.current_index += len(header_text)
        
        # Section content
        content_text = f"{content}\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': content_text
            }
        })
        
        # Style content
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(content_text) - 1
                },
                'textStyle': {
                    'fontSize': {'magnitude': 11, 'unit': 'PT'}
                },
                'fields': 'fontSize'
            }
        })
        
        self.current_index += len(content_text)
        return requests
    
    def _format_experience_harvard(self, experience: list) -> str:
        """Format experience section in Harvard style"""
        if not experience:
            return ""
        
        formatted = []
        for exp in experience:
            if isinstance(exp, dict):
                # Job title, Company, Dates (on one line)
                title = exp.get('position', exp.get('title', ''))
                company = exp.get('company', '')
                dates = exp.get('duration', exp.get('dates', ''))
                location = exp.get('location', '')
                
                # First line: Title, Company, Location, Dates
                header_parts = []
                if title and company:
                    header_parts.append(f"{title}, {company}")
                elif title:
                    header_parts.append(title)
                elif company:
                    header_parts.append(company)
                
                if location:
                    header_parts.append(location)
                if dates:
                    header_parts.append(dates)
                
                if header_parts:
                    formatted.append(' | '.join(header_parts))
                
                # Responsibilities/achievements as bullet points
                responsibilities = exp.get('responsibilities', exp.get('description', []))
                if isinstance(responsibilities, str):
                    responsibilities = [responsibilities]
                
                for resp in responsibilities:
                    if resp.strip():
                        formatted.append(f"• {resp.strip()}")
                
                formatted.append("")  # Blank line between jobs
        
        return '\n'.join(formatted)
    
    def _format_education_harvard(self, education: list) -> str:
        """Format education section in Harvard style"""
        if not education:
            return ""
        
        formatted = []
        for edu in education:
            if isinstance(edu, dict):
                # Institution, Degree, Date
                institution = edu.get('institution', '')
                degree = edu.get('degree', '')
                year = edu.get('year', edu.get('graduation_year', ''))
                gpa = edu.get('gpa', '')
                
                line_parts = []
                if institution:
                    line_parts.append(institution)
                if degree:
                    line_parts.append(degree)
                if year:
                    line_parts.append(str(year))
                
                if line_parts:
                    edu_line = ' | '.join(line_parts)
                    if gpa:
                        edu_line += f" | GPA: {gpa}"
                    formatted.append(edu_line)
                
                # Relevant coursework, honors, etc.
                if edu.get('relevant_coursework'):
                    formatted.append(f"Relevant Coursework: {edu['relevant_coursework']}")
                if edu.get('honors'):
                    formatted.append(f"Honors: {edu['honors']}")
                
                formatted.append("")  # Blank line
        
        return '\n'.join(formatted)
    
    def _format_skills_harvard(self, skills: list) -> str:
        """Format skills section in Harvard style"""
        if not skills:
            return ""
        
        # Group skills by category if they're objects, otherwise just list them
        if skills and isinstance(skills[0], dict):
            # Categorized skills
            formatted = []
            for skill_group in skills:
                category = skill_group.get('category', '')
                skill_list = skill_group.get('skills', [])
                if category and skill_list:
                    formatted.append(f"{category}: {', '.join(skill_list)}")
            return '\n'.join(formatted)
        else:
            # Simple skill list
            return ', '.join(str(skill) for skill in skills if skill)
    
    def _format_projects_harvard(self, projects: list) -> str:
        """Format projects section in Harvard style"""
        if not projects:
            return ""
        
        formatted = []
        for project in projects:
            if isinstance(project, dict):
                name = project.get('name', '')
                description = project.get('description', '')
                technologies = project.get('technologies', [])
                
                if name:
                    formatted.append(f"{name}")
                if description:
                    formatted.append(f"• {description}")
                if technologies:
                    tech_str = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
                    formatted.append(f"• Technologies: {tech_str}")
                
                formatted.append("")  # Blank line
        
        return '\n'.join(formatted)
    
    def _format_certifications_harvard(self, certifications: list) -> str:
        """Format certifications section in Harvard style"""
        if not certifications:
            return ""
        
        formatted = []
        for cert in certifications:
            if isinstance(cert, dict):
                name = cert.get('name', cert.get('title', ''))
                issuer = cert.get('issuer', cert.get('organization', ''))
                year = cert.get('year', cert.get('date', ''))
                
                cert_parts = []
                if name:
                    cert_parts.append(name)
                if issuer:
                    cert_parts.append(issuer)
                if year:
                    cert_parts.append(str(year))
                
                if cert_parts:
                    formatted.append(' | '.join(cert_parts))
        
        return '\n'.join(formatted)
    
    def _format_languages_harvard(self, languages: list) -> str:
        """Format languages section in Harvard style"""
        if not languages:
            return ""
        
        formatted = []
        for lang in languages:
            if isinstance(lang, dict):
                name = lang.get('language', lang.get('name', ''))
                level = lang.get('proficiency', lang.get('level', ''))
                if name:
                    lang_str = name
                    if level:
                        lang_str += f" ({level})"
                    formatted.append(lang_str)
            else:
                formatted.append(str(lang))
        
        return ', '.join(formatted)
    
    def _format_awards_harvard(self, awards: list) -> str:
        """Format awards section in Harvard style"""
        if not awards:
            return ""
        
        formatted = []
        for award in awards:
            if isinstance(award, dict):
                name = award.get('name', award.get('title', ''))
                organization = award.get('organization', award.get('issuer', ''))
                year = award.get('year', award.get('date', ''))
                
                award_parts = []
                if name:
                    award_parts.append(name)
                if organization:
                    award_parts.append(organization)
                if year:
                    award_parts.append(str(year))
                
                if award_parts:
                    formatted.append(' | '.join(award_parts))
            else:
                formatted.append(str(award))
        
        return '\n'.join(formatted)
