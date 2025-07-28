"""
AI Provider Interface - Swappable between Ollama and OpenAI
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass

@dataclass
class AIResponse:
    """Standardized AI response format"""
    content: str
    tokens_used: int
    model: str
    provider: str

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def generate_cv_optimization(self, job_description: str, base_cv: Dict[str, Any]) -> AIResponse:
        """Generate optimized CV content for a specific job"""
        pass
    
    @abstractmethod
    def extract_keywords(self, job_description: str) -> AIResponse:
        """Extract key skills and requirements from job description"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available and configured"""
        pass

class OllamaProvider(AIProvider):
    """Ollama local AI provider"""
    
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of Ollama client"""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.base_url)
            except ImportError:
                raise ImportError("ollama package not installed. Run: pip install ollama")
        return self._client
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            client = self._get_client()
            # Try to list models to check if Ollama is running
            models = client.list()
            available_models = [model['name'] for model in models['models']]
            return self.model in available_models
        except Exception as e:
            print(f"Ollama not available: {e}")
            return False
    
    def generate_cv_optimization(self, job_description: str, base_cv: Dict[str, Any]) -> AIResponse:
        """Generate optimized CV using Ollama"""
        prompt = self._build_cv_optimization_prompt(job_description, base_cv)
        
        try:
            client = self._get_client()
            response = client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            return AIResponse(
                content=response['message']['content'],
                tokens_used=response.get('eval_count', 0),
                model=self.model,
                provider="ollama"
            )
        
        except Exception as e:
            raise Exception(f"Ollama CV generation failed: {e}")
    
    def extract_keywords(self, job_description: str) -> AIResponse:
        """Extract keywords using Ollama"""
        prompt = f"""
        Analyze this job description and extract:
        1. Required technical skills
        2. Preferred qualifications  
        3. Key responsibilities
        4. Important keywords for ATS systems
        
        Job Description:
        {job_description}
        
        Return the results in JSON format:
        {{
            "required_skills": ["skill1", "skill2"],
            "preferred_qualifications": ["qual1", "qual2"],
            "key_responsibilities": ["resp1", "resp2"],
            "ats_keywords": ["keyword1", "keyword2"]
        }}
        """
        
        try:
            client = self._get_client()
            response = client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            return AIResponse(
                content=response['message']['content'],
                tokens_used=response.get('eval_count', 0),
                model=self.model,
                provider="ollama"
            )
        
        except Exception as e:
            raise Exception(f"Ollama keyword extraction failed: {e}")
    
    def _build_cv_optimization_prompt(self, job_description: str, base_cv: Dict[str, Any]) -> str:
        """Build comprehensive CV optimization prompt"""
        return f"""
        You are an expert CV optimizer specializing in ATS (Applicant Tracking System) optimization.
        
        TASK: Optimize the provided CV for the specific job description to maximize ATS compatibility and relevance.
        
        JOB DESCRIPTION:
        {job_description}
        
        BASE CV DATA:
        {base_cv}
        
        OPTIMIZATION REQUIREMENTS:
        1. Match key skills and requirements from the job description
        2. Use ATS-friendly keywords naturally
        3. Highlight relevant experience and achievements
        4. Maintain truthfulness - don't add fake experience
        5. Optimize section order for this specific role
        6. Ensure clean, scannable formatting
        
        Return the optimized CV in JSON format with these sections:
        {{
            "personal_info": {{"name": "...", "email": "...", "phone": "...", "location": "..."}},
            "professional_summary": "Optimized 2-3 sentence summary",
            "skills": ["skill1", "skill2", "skill3"],
            "experience": [
                {{"title": "...", "company": "...", "duration": "...", "achievements": ["...", "..."]}}
            ],
            "education": [...],
            "optimization_notes": "Summary of changes made for this job"
        }}
        
        Focus on relevance, ATS compatibility, and truthful enhancement of existing experience.
        """

class OpenAIProvider(AIProvider):
    """OpenAI provider for future migration"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        return self._client
    
    def is_available(self) -> bool:
        """Check if OpenAI API is configured and accessible"""
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return False
        
        try:
            client = self._get_client()
            # Test with a minimal request
            client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            print(f"OpenAI not available: {e}")
            return False
    
    def generate_cv_optimization(self, job_description: str, base_cv: Dict[str, Any]) -> AIResponse:
        """Generate optimized CV using OpenAI"""
        prompt = self._build_cv_optimization_prompt(job_description, base_cv)
        
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=self.model,
                provider="openai"
            )
        
        except Exception as e:
            raise Exception(f"OpenAI CV generation failed: {e}")
    
    def extract_keywords(self, job_description: str) -> AIResponse:
        """Extract keywords using OpenAI"""
        prompt = f"""
        Analyze this job description and extract:
        1. Required technical skills
        2. Preferred qualifications  
        3. Key responsibilities
        4. Important keywords for ATS systems
        
        Job Description:
        {job_description}
        
        Return the results in JSON format:
        {{
            "required_skills": ["skill1", "skill2"],
            "preferred_qualifications": ["qual1", "qual2"],
            "key_responsibilities": ["resp1", "resp2"],
            "ats_keywords": ["keyword1", "keyword2"]
        }}
        """
        
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=self.model,
                provider="openai"
            )
        
        except Exception as e:
            raise Exception(f"OpenAI keyword extraction failed: {e}")
    
    def _build_cv_optimization_prompt(self, job_description: str, base_cv: Dict[str, Any]) -> str:
        """Build comprehensive CV optimization prompt"""
        return f"""
        You are an expert CV optimizer specializing in ATS (Applicant Tracking System) optimization.
        
        TASK: Optimize the provided CV for the specific job description to maximize ATS compatibility and relevance.
        
        JOB DESCRIPTION:
        {job_description}
        
        BASE CV DATA:
        {base_cv}
        
        OPTIMIZATION REQUIREMENTS:
        1. Match key skills and requirements from the job description
        2. Use ATS-friendly keywords naturally
        3. Highlight relevant experience and achievements
        4. Maintain truthfulness - don't add fake experience
        5. Optimize section order for this specific role
        6. Ensure clean, scannable formatting
        
        Return the optimized CV in JSON format with these sections:
        {{
            "personal_info": {{"name": "...", "email": "...", "phone": "...", "location": "..."}},
            "professional_summary": "Optimized 2-3 sentence summary",
            "skills": ["skill1", "skill2", "skill3"],
            "experience": [
                {{"title": "...", "company": "...", "duration": "...", "achievements": ["...", "..."]}}
            ],
            "education": [...],
            "optimization_notes": "Summary of changes made for this job"
        }}
        
        Focus on relevance, ATS compatibility, and truthful enhancement of existing experience.
        """

def get_ai_provider() -> AIProvider:
    """Factory function to get configured AI provider"""
    provider_type = os.getenv('AI_PROVIDER', 'ollama').lower()
    
    if provider_type == 'ollama':
        model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        return OllamaProvider(model=model, base_url=base_url)
    
    elif provider_type == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        return OpenAIProvider(api_key=api_key, model=model)
    
    else:
        raise ValueError(f"Unsupported AI provider: {provider_type}")
