"""
Professional CV Formatter for Google Docs
Creates clean, professional CV formatting without markdown symbols
"""

import json
from typing import List, Dict, Any

class ProfessionalCVFormatter:
    """
    Creates professional CV formatting using proper Google Docs API formatting.
    No markdown symbols - just clean, professional text with proper styling.
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
                'references_available': 'Referencias y documentación detallada de proyectos disponibles bajo solicitud',
                'previous_roles': 'Roles Anteriores',
                'present': 'Presente'
            }
        }

    def build_professional_cv_requests(self, cv_data: dict) -> list:
        """Build formatting requests for professional CV layout"""
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
        
        name = personal_info.get('name', '')
        title = personal_info.get('professional_title', 'Junior Backend Developer')
        
        if not name:
            return requests
        
        # Name - large, bold, clean
        name_text = f"{name}\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': name_text
            }
        })
        
        # Style the name - large and bold
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(name)
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': 18, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        })
        
        # Center align the name
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(name_text)
                },
                'paragraphStyle': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        })
        
        self.current_index += len(name_text)
        
        # Professional title - bold, centered
        title_text = f"{title}\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': title_text
            }
        })
        
        # Style the title
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(title)
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': 14, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        })
        
        # Center align the title
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(title_text) - 1
                },
                'paragraphStyle': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        })
        
        self.current_index += len(title_text)
        
        # Add separator line
        separator_text = "―――――――――――――――――――――――――――――――――――――――――――――――――\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': separator_text
            }
        })
        
        # Center align separator
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(separator_text) - 2
                },
                'paragraphStyle': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        })
        
        self.current_index += len(separator_text)
        
        return requests

    def _create_contact_section(self, personal_info: dict) -> list:
        """Create the contact information section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        requests.extend(self._add_section_header(t['contact_information']))
        
        # Contact details
        contact_parts = []
        
        if personal_info.get('location'):
            contact_parts.append(f"{t['location']}: {personal_info['location']}")
        if personal_info.get('email'):
            contact_parts.append(f"{t['email']}: {personal_info['email']}")
        if personal_info.get('phone'):
            contact_parts.append(f"{t['phone']}: {personal_info['phone']}")
        if personal_info.get('linkedin'):
            contact_parts.append(f"{t['linkedin']}: {personal_info['linkedin']}")
        if personal_info.get('github'):
            contact_parts.append(f"{t['github']}: {personal_info['github']}")
        
        if contact_parts:
            contact_text = '\n'.join(contact_parts) + '\n\n'
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
        requests.extend(self._add_section_header(t['professional_summary']))
        
        # Summary content
        summary_text = f"{summary}\n\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': summary_text
            }
        })
        self.current_index += len(summary_text)
        
        return requests

    def _create_core_competencies(self, skills: list) -> list:
        """Create the core competencies section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        requests.extend(self._add_section_header(t['core_competencies']))
        
        # Process skills
        if skills and isinstance(skills[0], dict):
            # Categorized skills
            for skill_group in skills:
                category = skill_group.get('category', '')
                skill_list = skill_group.get('skills', [])
                if category and skill_list:
                    # Category header (bold)
                    category_text = f"{category}\n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': category_text
                        }
                    })
                    
                    # Make category bold
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': self.current_index,
                                'endIndex': self.current_index + len(category)
                            },
                            'textStyle': {
                                'bold': True
                            },
                            'fields': 'bold'
                        }
                    })
                    
                    self.current_index += len(category_text)
                    
                    # Skills list
                    skills_text = ' • '.join(skill_list) + '\n\n'
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': skills_text
                        }
                    })
                    self.current_index += len(skills_text)
        else:
            # Simple skill list
            skills_text = ', '.join(str(skill) for skill in skills if skill) + '\n\n'
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': skills_text
                }
            })
            self.current_index += len(skills_text)
        
        return requests

    def _create_technical_projects(self, projects: list) -> list:
        """Create the technical projects section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        requests.extend(self._add_section_header(t['technical_projects']))
        
        for project in projects:
            if isinstance(project, dict):
                name = project.get('name', '')
                dates = project.get('dates', project.get('duration', ''))
                technologies = project.get('technologies', [])
                description = project.get('description', '')
                repository = project.get('repository', project.get('github', ''))
                
                # Project name and dates
                if name:
                    if dates:
                        project_header = f"{name} | {dates}\n"
                    else:
                        project_header = f"{name}\n"
                    
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': project_header
                        }
                    })
                    
                    # Make project name bold
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': self.current_index,
                                'endIndex': self.current_index + len(name)
                            },
                            'textStyle': {
                                'bold': True
                            },
                            'fields': 'bold'
                        }
                    })
                    
                    self.current_index += len(project_header)
                
                # Technologies
                if technologies:
                    tech_str = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
                    tech_text = f"{t['technologies']}: {tech_str}\n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': tech_text
                        }
                    })
                    
                    # Make "Technologies:" bold
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': self.current_index,
                                'endIndex': self.current_index + len(t['technologies']) + 1
                            },
                            'textStyle': {
                                'bold': True
                            },
                            'fields': 'bold'
                        }
                    })
                    
                    self.current_index += len(tech_text)
                
                # Description
                if description:
                    if isinstance(description, list):
                        for desc_point in description:
                            point_text = f"• {desc_point}\n"
                            requests.append({
                                'insertText': {
                                    'location': {'index': self.current_index},
                                    'text': point_text
                                }
                            })
                            self.current_index += len(point_text)
                    else:
                        desc_text = f"• {description}\n"
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': desc_text
                            }
                        })
                        self.current_index += len(desc_text)
                
                # Repository
                if repository:
                    repo_text = f"{t['repository']}: {repository}\n\n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': repo_text
                        }
                    })
                    
                    # Make "Repository:" bold
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': self.current_index,
                                'endIndex': self.current_index + len(t['repository']) + 1
                            },
                            'textStyle': {
                                'bold': True
                            },
                            'fields': 'bold'
                        }
                    })
                    
                    self.current_index += len(repo_text)
                else:
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

    def _create_professional_experience(self, experience: list) -> list:
        """Create the professional experience section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        requests.extend(self._add_section_header(t['professional_experience']))
        
        for exp in experience:
            if isinstance(exp, dict):
                position = exp.get('position', exp.get('title', ''))
                company = exp.get('company', '')
                location = exp.get('location', '')
                duration = exp.get('duration', exp.get('dates', ''))
                
                # Job header
                job_parts = []
                if position:
                    job_parts.append(position)
                if company:
                    job_parts.append(company)
                if duration:
                    job_parts.append(duration)
                
                if job_parts:
                    header_text = ' | '.join(job_parts) + '\n'
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': header_text
                        }
                    })
                    
                    # Make position and company bold
                    if position:
                        requests.append({
                            'updateTextStyle': {
                                'range': {
                                    'startIndex': self.current_index,
                                    'endIndex': self.current_index + len(position)
                                },
                                'textStyle': {
                                    'bold': True
                                },
                                'fields': 'bold'
                            }
                        })
                    
                    self.current_index += len(header_text)
                
                # Responsibilities/achievements
                responsibilities = exp.get('responsibilities', exp.get('description', exp.get('achievements', [])))
                if isinstance(responsibilities, str):
                    responsibilities = [responsibilities]
                
                for resp in responsibilities:
                    if resp.strip():
                        resp_text = f"• {resp.strip()}\n"
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': resp_text
                            }
                        })
                        self.current_index += len(resp_text)
                
                # Add spacing between jobs
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
        requests.extend(self._add_section_header(t['education_development']))
        
        # Academic Background
        if education:
            subsection_text = f"{t['academic_background']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            
            # Make subsection bold
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': self.current_index,
                        'endIndex': self.current_index + len(t['academic_background'])
                    },
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            })
            
            self.current_index += len(subsection_text)
            
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', edu.get('school', ''))
                    year = edu.get('year', edu.get('graduation_year', ''))
                    
                    edu_parts = []
                    if degree:
                        edu_parts.append(degree)
                    if institution:
                        edu_parts.append(institution)
                    if year:
                        edu_parts.append(str(year))
                    
                    if edu_parts:
                        edu_text = ' | '.join(edu_parts) + '\n\n'
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': edu_text
                            }
                        })
                        self.current_index += len(edu_text)
        
        # Continuous Learning
        if certifications:
            subsection_text = f"{t['continuous_learning']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            
            # Make subsection bold
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': self.current_index,
                        'endIndex': self.current_index + len(t['continuous_learning'])
                    },
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            })
            
            self.current_index += len(subsection_text)
            
            for cert in certifications:
                if isinstance(cert, dict):
                    name = cert.get('name', cert.get('title', ''))
                    status = cert.get('status', '')
                    provider = cert.get('provider', '')
                    
                    cert_parts = []
                    if name:
                        cert_parts.append(name)
                    if status:
                        cert_parts.append(f"({status})")
                    if provider:
                        cert_parts.append(provider)
                    
                    if cert_parts:
                        cert_text = f"• {' '.join(cert_parts)}\n"
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': cert_text
                            }
                        })
                        self.current_index += len(cert_text)
            
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

    def _create_achievements_languages(self, awards: list, languages: list) -> list:
        """Create the achievements and languages section"""
        requests = []
        t = self.translations[self.language]
        
        # Section header
        requests.extend(self._add_section_header(t['achievements_languages']))
        
        # Professional Recognition
        if awards:
            subsection_text = f"{t['professional_recognition']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            
            # Make subsection bold
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': self.current_index,
                        'endIndex': self.current_index + len(t['professional_recognition'])
                    },
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            })
            
            self.current_index += len(subsection_text)
            
            for award in awards:
                if isinstance(award, dict):
                    name = award.get('name', award.get('title', ''))
                    organization = award.get('organization', award.get('issuer', ''))
                    description = award.get('description', '')
                    
                    award_parts = []
                    if name:
                        award_parts.append(name)
                    if organization:
                        award_parts.append(f"({organization})")
                    if description:
                        award_parts.append(f"- {description}")
                    
                    if award_parts:
                        award_text = f"• {' '.join(award_parts)}\n\n"
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': award_text
                            }
                        })
                        self.current_index += len(award_text)
        
        # Language Proficiency
        if languages:
            subsection_text = f"{t['language_proficiency']}\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': subsection_text
                }
            })
            
            # Make subsection bold
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': self.current_index,
                        'endIndex': self.current_index + len(t['language_proficiency'])
                    },
                    'textStyle': {
                        'bold': True
                    },
                    'fields': 'bold'
                }
            })
            
            self.current_index += len(subsection_text)
            
            for lang in languages:
                if isinstance(lang, dict):
                    name = lang.get('language', lang.get('name', ''))
                    level = lang.get('proficiency', lang.get('level', ''))
                    
                    if name and level:
                        lang_text = f"• {name}: {level}\n"
                        requests.append({
                            'insertText': {
                                'location': {'index': self.current_index},
                                'text': lang_text
                            }
                        })
                        self.current_index += len(lang_text)
                elif isinstance(lang, str):
                    lang_text = f"• {lang}\n"
                    requests.append({
                        'insertText': {
                            'location': {'index': self.current_index},
                            'text': lang_text
                        }
                    })
                    self.current_index += len(lang_text)
            
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

    def _create_footer(self) -> list:
        """Create the footer section"""
        requests = []
        t = self.translations[self.language]
        
        # Add separator line
        separator_text = "―――――――――――――――――――――――――――――――――――――――――――――――――\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': separator_text
            }
        })
        
        # Center align separator
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(separator_text) - 1
                },
                'paragraphStyle': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        })
        
        self.current_index += len(separator_text)
        
        # Footer text
        footer_text = f"{t['references_available']}"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': footer_text
            }
        })
        
        # Style footer as italic and center
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(footer_text)
                },
                'textStyle': {
                    'italic': True
                },
                'fields': 'italic'
            }
        })
        
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(footer_text)
                },
                'paragraphStyle': {
                    'alignment': 'CENTER'
                },
                'fields': 'alignment'
            }
        })
        
        self.current_index += len(footer_text)
        
        return requests

    def _add_section_header(self, header_text: str) -> list:
        """Add a formatted section header"""
        requests = []
        
        full_header = f"{header_text}\n"
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': full_header
            }
        })
        
        # Make header bold and larger
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': self.current_index,
                    'endIndex': self.current_index + len(header_text)
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': 12, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        })
        
        self.current_index += len(full_header)
        
        return requests
