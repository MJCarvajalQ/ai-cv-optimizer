#!/usr/bin/env python3
"""
AI CV Optimizer Application
Complete solution for generating tailored CVs from job postings
"""
import sys
import os
import json
import argparse
from typing import Dict, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sheets_reader_oauth import SheetsReaderOAuth
from cv_optimizer import CVOptimizer
from cv_generator_oauth import CVGeneratorOAuth

class CVOptimizerApp:
    """
    Main application class that orchestrates the CV optimization process.
    """
    
    def __init__(self, language='english'):
        self.sheets_reader = SheetsReaderOAuth()
        self.cv_generator = CVGeneratorOAuth(language=language)
        self.ai_optimizer = None  # Will be initialized when needed
        self.base_cv = None
        self.language = language.lower()
        self.cv_folder_id = None  # Will store the CV folder ID
        
    def load_base_cv(self, cv_path: str = 'templates/base_cv_english.json') -> Dict:
        """Load the base CV template"""
        try:
            with open(cv_path, 'r', encoding='utf-8') as f:
                self.base_cv = json.load(f)
            print(f"✅ Loaded base CV from {cv_path}")
            return self.base_cv
        except FileNotFoundError:
            print(f"❌ Base CV file not found: {cv_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in base CV file: {e}")
            sys.exit(1)
    
    def initialize_ai_optimizer(self, api_key: str = None):
        """Initialize the AI optimizer with API key"""
        try:
            self.ai_optimizer = CVOptimizer(api_key)
            print("✅ AI Optimizer initialized successfully")
        except ValueError as e:
            print(f"❌ Failed to initialize AI Optimizer: {e}")
            print("Please set OPENAI_API_KEY environment variable or provide API key")
            sys.exit(1)
    
    def list_jobs(self, spreadsheet_id: str):
        """List all jobs in the spreadsheet"""
        print(f"📋 Reading jobs from spreadsheet: {spreadsheet_id}")
        try:
            self.sheets_reader.list_jobs(spreadsheet_id)
        except Exception as e:
            print(f"❌ Error reading jobs: {e}")
            sys.exit(1)
    
    def parse_job_range(self, range_str: str) -> List[int]:
        """Parse job range string into list of row numbers.
        
        Examples:
        - "2-5" -> [2, 3, 4, 5]
        - "2,4,6" -> [2, 4, 6]
        - "2-5,8,10-12" -> [2, 3, 4, 5, 8, 10, 11, 12]
        """
        rows = []
        
        try:
            for part in range_str.split(','):
                part = part.strip()
                if '-' in part:
                    # Handle range like "2-5"
                    start, end = map(int, part.split('-'))
                    rows.extend(range(start, end + 1))
                else:
                    # Handle single number like "3"
                    rows.append(int(part))
            
            # Remove duplicates and sort
            return sorted(list(set(rows)))
            
        except ValueError as e:
            print(f"❌ Invalid range format: {range_str}")
            print("Examples: '2-5', '2,4,6', '2-5,8,10-12'")
            sys.exit(1)
    
    def setup_cv_folder(self) -> str:
        """Create or find the CV folder in Google Drive"""
        if not self.cv_folder_id:
            try:
                import datetime
                folder_name = f"AI Generated CVs - {datetime.datetime.now().strftime('%Y-%m')}"
                self.cv_folder_id = self.cv_generator.find_or_create_folder(folder_name)
                print(f"📁 Using CV folder: {folder_name} (ID: {self.cv_folder_id})")
            except Exception as e:
                print(f"⚠️  Could not create CV folder: {e}")
                print("CVs will be created in the root Drive folder")
                self.cv_folder_id = None
        return self.cv_folder_id

    def generate_cv_for_job(self, spreadsheet_id: str, job_row: int, use_ai: bool = True, language: str = None):
        """Generate a tailored CV for a specific job"""
        print(f"🎯 Generating CV for job in row {job_row}")
        
        # Load base CV if not already loaded
        if not self.base_cv:
            self.load_base_cv()
        
        # Get job data
        try:
            job_data = self.sheets_reader.get_job_by_row(spreadsheet_id, job_row)
            if not job_data:
                print(f"❌ No job found in row {job_row}")
                return
            
            print(f"📝 Found job: {job_data['company']} - {job_data['title']}")
        except Exception as e:
            print(f"❌ Error reading job data: {e}")
            return
        
        # Optimize CV with AI if requested
        if use_ai:
            if not self.ai_optimizer:
                print("⚠️  AI Optimizer not initialized. Using base CV without optimization.")
                optimized_cv = self.base_cv
            else:
                print("🤖 Optimizing CV with AI...")
                try:
                    optimized_cv = self.ai_optimizer.optimize_cv_for_job(self.base_cv, job_data)
                    print("✅ CV optimization completed")
                except Exception as e:
                    print(f"⚠️  AI optimization failed: {e}")
                    print("Using base CV as fallback")
                    optimized_cv = self.base_cv
        else:
            print("📄 Using base CV without AI optimization")
            optimized_cv = self.base_cv
        
        # Set up CV folder
        folder_id = self.setup_cv_folder()
        
        # Generate Google Doc
        try:
            print("📄 Creating Google Document...")
            cv_title = f"{optimized_cv['personal_info']['name']} - CV for {job_data['company']} ({job_data['title']})"
            cv_json = json.dumps(optimized_cv, indent=2)
            
            doc_language = language or self.language
            doc_url = self.cv_generator.create_google_doc(cv_json, cv_title, doc_language, folder_id)
            
            print(f"🎉 SUCCESS!")
            print(f"CV Document URL: {doc_url}")
            print(f"Job: {job_data['company']} - {job_data['title']}")
            
            # Update the job tracking in the sheet with comprehensive info
            print(f"📝 Updating job tracking...")
            try:
                notes = f"AI-optimized CV generated for {job_data['company']} - {job_data['title']}"
                self.sheets_reader.update_job_status(
                    spreadsheet_id, 
                    job_row, 
                    doc_url,  # CV Generated URL
                    "CV Generated",  # Status
                    notes  # Notes
                )
            except Exception as e:
                print(f"⚠️  Could not update tracking: {e}")
            
        except Exception as e:
            print(f"❌ Error creating Google Document: {e}")
    
    def generate_cvs_for_job_range(self, spreadsheet_id: str, job_rows: List[int], use_ai: bool = True, language: str = None):
        """Generate CVs for a range of job rows"""
        print(f"🚀 Generating CVs for job rows: {job_rows}")
        
        # Set up CV folder first
        folder_id = self.setup_cv_folder()
        
        # Load base CV if not already loaded
        if not self.base_cv:
            self.load_base_cv()
        
        successful_cvs = []
        failed_cvs = []
        
        for i, job_row in enumerate(job_rows, 1):
            print(f"\\n--- Processing Job Row {job_row} ({i}/{len(job_rows)}) ---")
            
            try:
                # Get job data
                job_data = self.sheets_reader.get_job_by_row(spreadsheet_id, job_row)
                if not job_data:
                    print(f"❌ No job found in row {job_row}")
                    failed_cvs.append({
                        'job': f"Row {job_row}",
                        'error': 'Job not found'
                    })
                    continue
                
                print(f"📝 Found job: {job_data['company']} - {job_data['title']}")
                
                # Optimize CV with AI if requested
                if use_ai and self.ai_optimizer:
                    print("🤖 Optimizing CV with AI...")
                    optimized_cv = self.ai_optimizer.optimize_cv_for_job(self.base_cv, job_data)
                else:
                    optimized_cv = self.base_cv
                
                # Generate Google Doc
                cv_title = f"{optimized_cv['personal_info']['name']} - CV for {job_data['company']} ({job_data['title']})"
                cv_json = json.dumps(optimized_cv, indent=2)
                
                doc_language = language or self.language
                doc_url = self.cv_generator.create_google_doc(cv_json, cv_title, doc_language, folder_id)
                
                successful_cvs.append({
                    'job': f"Row {job_row}: {job_data['company']} - {job_data['title']}",
                    'url': doc_url
                })
                print(f"✅ Success: {doc_url}")
                
                # Update job status
                try:
                    notes = f"AI-optimized CV generated for {job_data['company']} - {job_data['title']}"
                    self.sheets_reader.update_job_status(
                        spreadsheet_id, 
                        job_row, 
                        doc_url,  # CV Generated URL
                        "CV Generated",  # Status
                        notes  # Notes
                    )
                except Exception as status_error:
                    print(f"⚠️  Could not update status: {status_error}")
                
            except Exception as e:
                failed_cvs.append({
                    'job': f"Row {job_row}",
                    'error': str(e)
                })
                print(f"❌ Failed: {e}")
        
        # Summary
        print(f"\\n🎉 RANGE PROCESSING COMPLETE!")
        print(f"✅ Successful: {len(successful_cvs)} CVs")
        print(f"❌ Failed: {len(failed_cvs)} CVs")
        
        if successful_cvs:
            print(f"\\n📄 Successfully created CVs:")
            for cv in successful_cvs:
                print(f"  • {cv['job']}: {cv['url']}")
        
        if failed_cvs:
            print(f"\\n⚠️  Failed CVs:")
            for cv in failed_cvs:
                print(f"  • {cv['job']}: {cv['error']}")
    
    def generate_cvs_for_all_jobs(self, spreadsheet_id: str, use_ai: bool = True, language: str = None):
        """Generate CVs for all jobs in the spreadsheet"""
        print("🚀 Generating CVs for all jobs in the spreadsheet")
        
        # Set up CV folder first
        folder_id = self.setup_cv_folder()
        
        # Load base CV if not already loaded
        if not self.base_cv:
            self.load_base_cv()
        
        # Get all jobs
        try:
            jobs = self.sheets_reader.read_jobs_from_sheet(spreadsheet_id)
            if not jobs:
                print("❌ No jobs found in the spreadsheet")
                return
            
            print(f"📋 Found {len(jobs)} jobs to process")
        except Exception as e:
            print(f"❌ Error reading jobs: {e}")
            return
        
        # Process each job
        successful_cvs = []
        failed_cvs = []
        
        for i, job_data in enumerate(jobs, 1):
            print(f"\\n--- Processing Job {i}/{len(jobs)} ---")
            print(f"📝 {job_data['company']} - {job_data['title']}")
            
            try:
                # Optimize CV with AI if requested
                if use_ai and self.ai_optimizer:
                    print("🤖 Optimizing CV with AI...")
                    optimized_cv = self.ai_optimizer.optimize_cv_for_job(self.base_cv, job_data)
                else:
                    optimized_cv = self.base_cv
                
                # Generate Google Doc
                cv_title = f"{optimized_cv['personal_info']['name']} - CV for {job_data['company']} ({job_data['title']})"
                cv_json = json.dumps(optimized_cv, indent=2)
                
                doc_language = language or self.language
                doc_url = self.cv_generator.create_google_doc(cv_json, cv_title, doc_language, folder_id)
                
                successful_cvs.append({
                    'job': f"{job_data['company']} - {job_data['title']}",
                    'url': doc_url
                })
                print(f"✅ Success: {doc_url}")
                
                # Update job status
                try:
                    self.sheets_reader.update_job_status(spreadsheet_id, job_data['row_number'], "CV Generated")
                except Exception as status_error:
                    print(f"⚠️  Could not update status: {status_error}")
                
            except Exception as e:
                failed_cvs.append({
                    'job': f"{job_data['company']} - {job_data['title']}",
                    'error': str(e)
                })
                print(f"❌ Failed: {e}")
        
        # Summary
        print(f"\\n🎉 PROCESSING COMPLETE!")
        print(f"✅ Successful: {len(successful_cvs)} CVs")
        print(f"❌ Failed: {len(failed_cvs)} CVs")
        
        if successful_cvs:
            print(f"\\n📄 Successfully created CVs:")
            for cv in successful_cvs:
                print(f"  • {cv['job']}: {cv['url']}")
        
        if failed_cvs:
            print(f"\\n⚠️  Failed CVs:")
            for cv in failed_cvs:
                print(f"  • {cv['job']}: {cv['error']}")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='AI CV Optimizer - Generate tailored CVs from job postings')
    parser.add_argument('spreadsheet_id', help='Google Sheets ID containing job data')
    parser.add_argument('--list', action='store_true', help='List all jobs in the spreadsheet')
    parser.add_argument('--job-row', type=int, help='Generate CV for specific job row number')
    parser.add_argument('--job-range', help='Generate CVs for job row range (e.g., "2-15" or "5,7,9-12")')
    parser.add_argument('--all-jobs', action='store_true', help='Generate CVs for all jobs')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI optimization (use base CV)')
    parser.add_argument('--cv-template', default='templates/base_cv_english.json', help='Path to base CV template')
    parser.add_argument('--language', choices=['english', 'spanish'], default='english', help='CV language (default: english)')
    parser.add_argument('--openai-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Initialize application
    app = CVOptimizerApp(language=args.language)
    
    # Load base CV
    app.load_base_cv(args.cv_template)
    
    # Initialize AI optimizer if needed
    if not args.no_ai:
        app.initialize_ai_optimizer(args.openai_key)
    
    # Execute requested action
    if args.list:
        app.list_jobs(args.spreadsheet_id)
    elif args.job_row:
        app.generate_cv_for_job(args.spreadsheet_id, args.job_row, use_ai=not args.no_ai, language=args.language)
    elif args.job_range:
        job_rows = app.parse_job_range(args.job_range)
        print(f"📋 Parsed job range: {job_rows}")
        app.generate_cvs_for_job_range(args.spreadsheet_id, job_rows, use_ai=not args.no_ai, language=args.language)
    elif args.all_jobs:
        app.generate_cvs_for_all_jobs(args.spreadsheet_id, use_ai=not args.no_ai, language=args.language)
    else:
        print("❌ Please specify an action: --list, --job-row, --job-range, or --all-jobs")
        parser.print_help()

if __name__ == '__main__':
    main()
