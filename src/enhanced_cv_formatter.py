"""
Enhanced CV Formatter for Google Docs
Creates the exact CV layout requested with support for English and Spanish
"""

import json
from typing import List, Dict, Any

class EnhancedCVFormatter:
    """
    Enhanced CV formatter that creates the specific layout requested by the user.
    Supports both English and Spanish languages.
    """
    
    def __init__(self, language='english'):
        self.current_index = 1
        self.language = language.lower()
        self.translations = self._get_translations()
        
    def _get_translations(self):
        """Get translations for section headers and common terms"""
        return {
            'english': {
                'contact_information': 'CONTACT INFORMATION',
                'professional_summary': 'PROFESSIONAL SUMMARY',
                'core_competencies': 'CORE COMPETENCIES',
                'technical_projects': 'TECHNICAL PROJECTS',
                'professional_experience': 'PROFESSIONAL EXPERIENCE',
                'education_development': 'EDUCATION & PROFESSIONAL DEVELOPMENT',
                'achievements_languages': 'ACHIEVEMENTS & LANGUAGES',
                'location': 'Location',
                'email': 'Email',
                'phone': 'Phone',
                'linkedin': 'LinkedIn',
                'github': 'GitHub',
                'programming_languages': 'Programming Languages',
                'frameworks_technologies': 'Frameworks & Technologies',
                'database_systems': 'Database Systems',
                'development_tools': 'Development Tools',
                'data_analytics': 'Data Analytics',
                'technical_concepts': 'Technical Concepts',
                'technologies': 'Technologies',
                'repository': 'Repository',
                'academic_background': 'Academic Background',
                'continuous_learning': 'Continuous Learning',
                'current_coursework': 'Current Coursework',
                'mentorship_program': 'Mentorship Program',
                'professional_recognition': 'Professional Recognition',
                'language_proficiency': 'Language Proficiency',
                'native_fluency': 'Native Fluency',
                'advanced': 'Advanced',
                'professional_working_proficiency': 'Professional Working Proficiency',
                'references_available': 'References and detailed project documentation available upon request',
                'previous_roles': 'Previous Roles',
                'present': 'Present'
            },
            'spanish': {
                'contact_information': 'INFORMACIÓN DE CONTACTO',
                'professional_summary': 'RESUMEN PROFESIONAL',
                'core_competencies': 'COMPETENCIAS PRINCIPALES',
                'technical_projects': 'PROYECTOS TÉCNICOS',
                'professional_experience': 'EXPERIENCIA PROFESIONAL',
                'education_development': 'EDUCACIÓN Y DESARROLLO PROFESIONAL',
                'achievements_languages': 'LOGROS E IDIOMAS',
                'location': 'Ubicación',
                'email': 'Correo',
                'phone': 'Teléfono',
                'linkedin': 'LinkedIn',
                'github': 'GitHub',
                'programming_languages': 'Lenguajes de Programación',
                'frameworks_technologies': 'Frameworks y Tecnologías',
                'database_systems': 'Sistemas de Base de Datos',
                'development_tools': 'Herramientas de Desarrollo',
                'data_analytics': 'Análisis de Datos',
                'technical_concepts': 'Conceptos Técnicos',
                'technologies': 'Tecnologías',
                'repository': 'Repositorio',
                'academic_background': 'Formación Académica',
                'continuous_learning': 'Aprendizaje Continuo',
                'current_coursework': 'Cursos Actuales',
                'mentorship_program': 'Programa de Mentoría',
                'professional_recognition': 'Reconocimiento Profesional',
                'language_proficiency': 'Competencia Lingüística',
                'native_fluency': 'Fluidez Nativa',
                'advanced': 'Avanzado',
                'professional_working_proficiency': 'Competencia Profesional de Trabajo',
                'references_available': 'Referencias y documentación detallada de proyectos disponibles bajo solicitud',
                'previous_roles': 'Roles Anteriores',
                'present': 'Presente'
            }
        }

    def build_enhanced_cv_requests(self, cv_data: dict) -> list:
        """Build formatting requests for the enhanced CV layout"""
        requests = []
        self.current_index = 1
        
        # Handle raw content fallback
        if 'raw_content' in cv_data:
            return self._handle_raw_content(cv_data['raw_content'])
        
        # 1. Name and Title Header
        requests.extend(self._create_name_title_header(cv_data.get('personal_info', {})))
        
        # 2. Contact Information Section
        requests.extend(self._create_contact_section(cv_data.get('personal_info', {})))
        
        # 3. Professional Summary
        if cv_data.get('professional_summary'):
            requests.extend(self._create_professional_summary(cv_data['professional_summary']))
        
        # 4. Core Competencies
        if cv_data.get('skills'):
            requests.extend(self._create_core_competencies(cv_data['skills']))
        
        # 5. Technical Projects
        if cv_data.get('projects'):
            requests.extend(self._create_technical_projects(cv_data['projects']))
        
        # 6. Professional Experience
        if cv_data.get('experience'):
            requests.extend(self._create_professional_experience(cv_data['experience']))
        
        # 7. Education & Professional Development
        if cv_data.get('education') or cv_data.get('certifications_courses'):
            requests.extend(self._create_education_development(
                cv_data.get('education', []), 
                cv_data.get('certifications_courses', [])
            ))
        
        # 8. Achievements & Languages
        if cv_data.get('awards') or cv_data.get('languages'):
            requests.extend(self._create_achievements_languages(
                cv_data.get('awards', []), 
                cv_data.get('languages', [])
            ))
        
        # 9. Footer
        requests.extend(self._create_footer())
        
        return requests

    def _handle_raw_content(self, content: str) -> list:
        """Handle raw text content with basic formatting"""
        return [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
    
    def _create_name_title_header(self, personal_info: dict) -> list:
        """Create the name and professional title header"""
        requests = []
        t = self.translations[self.language]
        
        name = personal_info.get('name', '')
        title = personal_info.get('professional_title', 'Junior Backend Developer')
        
        if not name:
            return requests
        
        # Name - large, bold, with markdown-style formatting
        name_text = f"# {name}\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': name_text
            }
        })
        
        # Style the name (excluding the # symbol)
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index + 2,  # Skip "# "
                    'endIndex': self.current_index + len(name_text) - 1
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': 18, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        })
        
        self.current_index += len(name_text)
        
        # Professional title - bold
        title_text = f"**{title}**\n\n---\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': title_text
            }
        })
        
        # Style the title (excluding the ** symbols)
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index + 2,  # Skip "**"
                    'endIndex': self.current_index + 2 + len(title)
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': 14, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        })
        
        self.current_index += len(title_text)
        
        return requests

    def _create_contact_section(self, personal_info: dict) -> list:
        """Create the contact information section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        header_text = f"## {t['contact_information']}\n"
        requests.extend(self._add_section_header(header_text))
        
        # Contact details with specific formatting
        contact_lines = []
        
        if personal_info.get('location'):
            contact_lines.append(f"**{t['location']}:** {personal_info['location']}")
        if personal_info.get('email'):
            contact_lines.append(f"**{t['email']}:** {personal_info['email']}")
        if personal_info.get('phone'):
            contact_lines.append(f"**{t['phone']}:** {personal_info['phone']}")
        if personal_info.get('linkedin'):
            contact_lines.append(f"**{t['linkedin']}:** [Profile Link]")
        if personal_info.get('github'):
            contact_lines.append(f"**{t['github']}:** [Portfolio Link]")
        
        if contact_lines:
            contact_text = '  \n'.join(contact_lines) + '\n\n---\n\n'
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': contact_text
                }
            })
            self.current_index += len(contact_text)
        
        return requests

    def _create_professional_summary(self, summary: str) -> list:
        """Create the professional summary section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        header_text = f"## {t['professional_summary']}\n\n"
        requests.extend(self._add_section_header(header_text))
        
        # Summary content
        summary_text = f"{summary}\n\n---\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': summary_text
            }
        })
        self.current_index += len(summary_text)
        
        return requests

    def _create_core_competencies(self, skills: list) -> list:
        """Create the core competencies section with proper categorization"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        header_text = f"## {t['core_competencies']}\n\n"
        requests.extend(self._add_section_header(header_text))
        
        # Skill categories with proper formatting
        skill_categories = [
            (t['programming_languages'], ['Java', 'SQL', 'Python (Foundational)']),
            (t['frameworks_technologies'], ['Spring Boot', 'Spring MVC', 'Spring Data JPA', 'Apache POI']),
            (t['database_systems'], ['MySQL', 'H2', 'Oracle SQL Developer']),
            (t['development_tools'], ['Git/GitHub', 'Postman', 'IntelliJ IDEA', 'Maven']),
            (t['data_analytics'], ['Power BI', 'Tableau']),
            (t['technical_concepts'], ['REST API Design', 'Validation & Exception Handling', 'CRUD Operations', 'MVC Architecture', 'Agile Methodologies'])
        ]
        
        # Process categorized skills or use provided skills structure
        if skills and isinstance(skills[0], dict):
            # Use provided skill structure
            for skill_group in skills:
                category = skill_group.get('category', '')
                skill_list = skill_group.get('skills', [])
                if category and skill_list:
                    skills_text = f"**{category}**  \n{' • '.join(skill_list)}\n\n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': skills_text
                        }
                    })
                    self.current_index += len(skills_text)
        else:
            # Use default categorization
            for category, skill_list in skill_categories:
                skills_text = f"**{category}**  \n{' • '.join(skill_list)}\n\n"
                requests.append({
                    'insertText': {
                        'location': {'index': self.current_index},
                        'text': skills_text
                    }
                })
                self.current_index += len(skills_text)
        
        # Add separator
        separator_text = "---\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': separator_text
            }
        })
        self.current_index += len(separator_text)
        
        return requests

    def _create_technical_projects(self, projects: list) -> list:
        """Create the technical projects section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        header_text = f"## {t['technical_projects']}\n\n"
        requests.extend(self._add_section_header(header_text))
        
        for project in projects:
            if isinstance(project, dict):
                name = project.get('name', '')
                dates = project.get('dates', project.get('duration', ''))
                technologies = project.get('technologies', [])
                description = project.get('description', '')
                repository = project.get('repository', project.get('url', ''))
                
                # Project header with dates
                if name and dates:
                    project_header = f"### {name} | *{dates}*\n"
                elif name:
                    project_header = f"### {name}\n"
                else:
                    continue
                
                requests.append({
                    'insertText': {
                        'location': {'index': self.current_index},
                        'text': project_header
                    }
                })
                self.current_index += len(project_header)
                
                # Technologies
                if technologies:
                    tech_str = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
                    tech_text = f"**{t['technologies']}:** {tech_str}  \n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': tech_text
                        }
                    })
                    self.current_index += len(tech_text)
                
                # Description points
                if description:
                    if isinstance(description, list):
                        for desc_point in description:
                            point_text = f"- {desc_point}\n"
                            requests.append({
                                'insertText': {
                                    'location': {'index': self.current_index},
                                    'text': point_text
                                }
                            })
                            self.current_index += len(point_text)
                    else:
                        desc_text = f"- {description}\n"
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': desc_text
                            }
                        })
                        self.current_index += len(desc_text)
                
                # Repository link
                if repository:
                    repo_text = f"- **{t['repository']}:** {repository}\n\n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': repo_text
                        }
                    })
                    self.current_index += len(repo_text)
                else:
                    # Just add spacing
                    spacing_text = "\n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': spacing_text
                        }
                    })
                    self.current_index += len(spacing_text)
        
        # Add separator
        separator_text = "---\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': separator_text
            }
        })
        self.current_index += len(separator_text)
        
        return requests

    def _create_professional_experience(self, experience: list) -> list:
        """Create the professional experience section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        header_text = f"## {t['professional_experience']}\n\n"
        requests.extend(self._add_section_header(header_text))
        
        # Group current and previous roles
        current_roles = []
        previous_roles = []
        
        for exp in experience:
            if isinstance(exp, dict):
                end_date = exp.get('end_date', exp.get('duration', ''))
                if t['present'].lower() in str(end_date).lower() or 'present' in str(end_date).lower():
                    current_roles.append(exp)
                else:
                    previous_roles.append(exp)
        
        # Add current roles first
        for exp in current_roles:
            requests.extend(self._format_experience_entry(exp))
        
        # Add previous roles with subheader if there are both current and previous
        if current_roles and previous_roles:
            subheader_text = f"### {t['previous_roles']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subheader_text
                }
            })
            self.current_index += len(subheader_text)
        
        for exp in previous_roles:
            requests.extend(self._format_experience_entry(exp))
        
        # Add separator
        separator_text = "---\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': separator_text
            }
        })
        self.current_index += len(separator_text)
        
        return requests

    def _format_experience_entry(self, exp: dict) -> list:
        """Format a single experience entry"""
        requests = []
        
        position = exp.get('position', exp.get('title', ''))
        company = exp.get('company', '')
        location = exp.get('location', '')
        duration = exp.get('duration', exp.get('dates', ''))
        
        # Job header
        if position and company and duration:
            header_text = f"### {position} | *{company}* | **{duration}**\n"
        elif position and company:
            header_text = f"### {position} | *{company}*\n"
        elif position:
            header_text = f"### {position}\n"
        else:
            return requests
        
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': header_text
            }
        })
        self.current_index += len(header_text)
        
        # Responsibilities/achievements
        responsibilities = exp.get('responsibilities', exp.get('description', []))
        if isinstance(responsibilities, str):
            responsibilities = [responsibilities]
        
        for resp in responsibilities:
            if resp.strip():
                resp_text = f"- {resp.strip()}\n"
                requests.append({
                    'insertText': {
                        'location': {'index': self.current_index},
                        'text': resp_text
                    }
                })
                self.current_index += len(resp_text)
        
        # Add spacing
        spacing_text = "\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': spacing_text
            }
        })
        self.current_index += len(spacing_text)
        
        return requests

    def _create_education_development(self, education: list, certifications: list) -> list:
        """Create the education and professional development section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        header_text = f"## {t['education_development']}\n\n"
        requests.extend(self._add_section_header(header_text))
        
        # Academic Background subsection
        if education:
            subsection_text = f"### {t['academic_background']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            self.current_index += len(subsection_text)
            
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    year = edu.get('year', edu.get('graduation_year', ''))
                    
                    if degree and institution and year:
                        edu_text = f"**{degree}**  \n*{institution}* | **{year}**\n\n"
                    elif degree and institution:
                        edu_text = f"**{degree}**  \n*{institution}*\n\n"
                    else:
                        continue
                    
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': edu_text
                        }
                    })
                    self.current_index += len(edu_text)
        
        # Continuous Learning subsection
        if certifications:
            subsection_text = f"### {t['continuous_learning']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            self.current_index += len(subsection_text)
            
            # Current Coursework
            coursework_text = f"**{t['current_coursework']}:**\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': coursework_text
                }
            })
            self.current_index += len(coursework_text)
            
            for cert in certifications:
                if isinstance(cert, dict):
                    name = cert.get('name', cert.get('title', ''))
                    description = cert.get('description', '')
                    
                    if name:
                        cert_text = f"- {name}"
                        if description:
                            cert_text += f" ({description})"
                        cert_text += "\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': cert_text
                            }
                        })
                        self.current_index += len(cert_text)
            
            # Mentorship program
            mentorship_text = f"\n**{t['mentorship_program']}**  \nGuided weekly by a self-taught software developer mentor with focus on code reviews and best practices.\n\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': mentorship_text
                }
            })
            self.current_index += len(mentorship_text)
        
        # Add separator
        separator_text = "---\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': separator_text
            }
        })
        self.current_index += len(separator_text)
        
        return requests

    def _create_achievements_languages(self, awards: list, languages: list) -> list:
        """Create the achievements and languages section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        header_text = f"## {t['achievements_languages']}\n\n"
        requests.extend(self._add_section_header(header_text))
        
        # Professional Recognition
        if awards:
            subsection_text = f"### {t['professional_recognition']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            self.current_index += len(subsection_text)
            
            for award in awards:
                if isinstance(award, dict):
                    name = award.get('name', award.get('title', ''))
                    organization = award.get('organization', award.get('issuer', ''))
                    description = award.get('description', '')
                    
                    if name and organization:
                        award_text = f"**{name}** | *{organization}*"
                        if description:
                            award_text += f" - {description}"
                        award_text += "\n\n"
                        
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': award_text
                            }
                        })
                        self.current_index += len(award_text)
        
        # Language Proficiency
        if languages:
            subsection_text = f"### {t['language_proficiency']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            self.current_index += len(subsection_text)
            
            for lang in languages:
                if isinstance(lang, dict):
                    name = lang.get('language', lang.get('name', ''))
                    level = lang.get('proficiency', lang.get('level', ''))
                    
                    if name and level:
                        lang_text = f"**{name}:** {level}  \n"
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': lang_text
                            }
                        })
                        self.current_index += len(lang_text)
                elif isinstance(lang, str):
                    lang_text = f"**{lang}**  \n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': lang_text
                        }
                    })
                    self.current_index += len(lang_text)
        
        return requests

    def _create_footer(self) -> list:
        """Create the footer section"""
        requests = []
        t = self.translations[self.language]
        
        # Add separator and footer
        footer_text = f"\n---\n\n*{t['references_available']}*"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': footer_text
            }
        })
        self.current_index += len(footer_text)
        
        return requests

    def _add_section_header(self, header_text: str) -> list:
        """Add a formatted section header"""
        requests = []
        
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': header_text
            }
        })
        
        self.current_index += len(header_text)
        
        return requests
