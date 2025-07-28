"""
AI CV Optimizer - Tailors CV content to specific job requirements using OpenAI
"""
import os
import sys
import json
from openai import OpenAI
from typing import Dict, Optional

# Add scripts directory to path for secure key retrieval
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from get_api_key import get_api_key_from_keychain
    KEYCHAIN_AVAILABLE = True
except ImportError:
    KEYCHAIN_AVAILABLE = False

class CVOptimizer:
    """
    Uses AI to optimize CV content for specific job requirements.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize with OpenAI API key.
        
        Args:
            api_key: OpenAI API key. If not provided, will try multiple secure sources.
            model: OpenAI model to use (gpt-3.5-turbo is much cheaper than gpt-4)
        """
        # Try multiple sources for API key (in order of preference)
        if not api_key:
            # 1. Try environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            
            # 2. Try macOS Keychain (most secure)
            if not api_key and KEYCHAIN_AVAILABLE:
                try:
                    api_key = get_api_key_from_keychain()
                    if api_key:
                        print("✅ Using API key from macOS Keychain (secure)")
                except Exception as e:
                    print(f"⚠️  Could not retrieve from Keychain: {e}")
        
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. Try one of these options:\n"
                "1. Set OPENAI_API_KEY environment variable\n"
                "2. Store in macOS Keychain: security add-generic-password -a $USER -s 'openai-api-key' -w 'your-key'\n"
                "3. Pass directly via --openai-key argument"
            )
        
        self.model = model  # Use cheaper gpt-3.5-turbo by default
        self.client = OpenAI(api_key=api_key)
    
    def optimize_cv_for_job(self, base_cv: Dict, job_data: Dict) -> Dict:
        """
        Optimize CV content for a specific job.
        
        Args:
            base_cv: Base CV data as dictionary
            job_data: Job data with company, title, description, requirements
            
        Returns:
            Optimized CV as dictionary
        """
        
        # Create the optimization prompt
        prompt = self._create_optimization_prompt(base_cv, job_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,  # Use configurable model (cheaper gpt-3.5-turbo by default)
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CV optimizer. Tailor CVs to job requirements while keeping all information truthful. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,  # Reduced tokens to save cost
                temperature=0.3   # Lower temperature for more consistent results
            )
            
            # Parse the AI response
            optimized_cv_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON, fall back to structured parsing
            try:
                optimized_cv = json.loads(optimized_cv_text)
            except json.JSONDecodeError:
                optimized_cv = self._parse_ai_response_to_cv(optimized_cv_text, base_cv)
            
            return optimized_cv
            
        except Exception as e:
            print(f"Error optimizing CV: {e}")
            print("Returning base CV as fallback...")
            return base_cv
    
    def _create_optimization_prompt(self, base_cv: Dict, job_data: Dict) -> str:
        """Create the optimization prompt for the AI"""
        
        prompt = f"""
Please optimize this CV for the following job opportunity:

**JOB DETAILS:**
Company: {job_data.get('company', 'N/A')}
Position: {job_data.get('title', 'N/A')}
Description: {job_data.get('description', 'N/A')}
Requirements: {job_data.get('requirements', 'N/A')}

**CURRENT CV:**
{json.dumps(base_cv, indent=2)}

**OPTIMIZATION INSTRUCTIONS:**
1. Tailor the professional summary to emphasize skills and experiences most relevant to this role
2. Reorder and highlight the most relevant skills for this position
3. Adjust experience descriptions to emphasize achievements relevant to the job requirements
4. Ensure all information remains truthful - do not invent experience or skills
5. Maintain the same JSON structure as the input CV
6. Focus on keywords and requirements mentioned in the job description

**OUTPUT FORMAT:**
Return the optimized CV as a valid JSON object with the same structure as the input CV.

Optimized CV:
"""
        return prompt
    
    def _parse_ai_response_to_cv(self, ai_response: str, base_cv: Dict) -> Dict:
        """
        Parse AI response when JSON parsing fails.
        Extract key sections and create structured CV.
        """
        # This is a fallback method if the AI doesn't return valid JSON
        # For now, we'll return the base CV with a modified summary
        optimized_cv = base_cv.copy()
        
        # Try to extract professional summary from AI response
        lines = ai_response.split('\n')
        for i, line in enumerate(lines):
            if 'professional summary' in line.lower() or 'summary' in line.lower():
                # Look for the next few lines that might contain the summary
                summary_lines = []
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and not lines[j].startswith(('**', '#', 'SKILLS', 'EXPERIENCE')):
                        summary_lines.append(lines[j].strip())
                    elif summary_lines:  # Stop if we hit a new section
                        break
                
                if summary_lines:
                    optimized_cv['professional_summary'] = ' '.join(summary_lines)
                break
        
        return optimized_cv
    
    def create_cv_variants(self, base_cv: Dict, jobs_list: list) -> Dict[str, Dict]:
        """
        Create multiple CV variants for different jobs.
        
        Args:
            base_cv: Base CV data
            jobs_list: List of job dictionaries
            
        Returns:
            Dictionary mapping job identifiers to optimized CVs
        """
        variants = {}
        
        for job in jobs_list:
            job_id = f"{job.get('company', 'Unknown')}_{job.get('title', 'Position')}".replace(' ', '_')
            print(f"\\nOptimizing CV for: {job.get('company')} - {job.get('title')}")
            
            try:
                optimized_cv = self.optimize_cv_for_job(base_cv, job)
                variants[job_id] = {
                    'job_info': job,
                    'optimized_cv': optimized_cv
                }
                print(f"✅ Successfully optimized CV for {job_id}")
            except Exception as e:
                print(f"❌ Failed to optimize CV for {job_id}: {e}")
                variants[job_id] = {
                    'job_info': job,
                    'optimized_cv': base_cv,  # Fallback to base CV
                    'error': str(e)
                }
        
        return variants
