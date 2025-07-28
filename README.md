# 🤖 AI CV Optimizer

**Automatically generate tailored CVs for job applications using OpenAI and Google Workspace integration**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-green.svg)](https://openai.com)
[![Google APIs](https://img.shields.io/badge/Google-Sheets%20%7C%20Docs%20%7C%20Drive-yellow.svg)](https://developers.google.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🌟 Overview

AI CV Optimizer is a powerful automation tool that helps job seekers create personalized CVs for multiple job applications. It integrates with Google Sheets for job tracking, uses OpenAI's GPT models for CV optimization, and automatically generates formatted CVs as Google Documents.

### ✨ Key Features

- **🎯 AI-Powered CV Tailoring**: Uses OpenAI GPT-3.5-turbo to customize CVs for specific job requirements
- **📊 Google Sheets Integration**: Manages job applications through a centralized spreadsheet
- **📄 Automated Document Creation**: Generates professional CVs as Google Docs
- **🔒 Secure Credential Management**: Uses macOS Keychain for API key storage
- **🌍 Multi-language Support**: Supports English and Spanish CV generation
- **📁 Organized File Management**: Automatically organizes generated CVs in Google Drive folders
- **📈 Application Tracking**: Updates job application status and maintains application history

## 🛠️ Technology Stack

- **Python 3.10+** - Core application
- **OpenAI GPT-3.5-turbo** - AI-powered CV optimization
- **Google Sheets API** - Job tracking and management
- **Google Docs API** - CV document generation
- **Google Drive API** - File organization
- **OAuth 2.0** - Secure Google account authentication
- **macOS Keychain** - Secure API key storage

## 📋 Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher
- A Google Cloud Platform account
- An OpenAI API account
- macOS (for Keychain integration)

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-cv-optimizer.git
cd ai-cv-optimizer
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Google Cloud Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Docs API
   - Google Drive API
4. Create OAuth 2.0 credentials
5. Download the credentials file and save it as `oauth_credentials.json`

### 5. Set Up OpenAI API Key

Store your OpenAI API key securely in macOS Keychain:

```bash
security add-generic-password -a "$USER" -s "openai-api-key" -w "your-openai-api-key" -T ""
```

### 6. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Google Sheets ID and other configuration
```

### 7. Set Up Your Base CV Templates

Create your base CV files using the provided templates:

```bash
# Copy templates and customize with your information
cp templates/example_cv.json templates/base_cv_english.json
cp templates/base_cv_spanish.json templates/base_cv_spanish.json  # If using Spanish

# Edit the files with your personal information
```

## 🎯 Usage

### Basic Commands

#### List Jobs in Spreadsheet
```bash
python cv_optimizer_app.py [SPREADSHEET_ID] --list
```

#### Generate CV for Specific Job
```bash
python cv_optimizer_app.py [SPREADSHEET_ID] --job-row 5
```

#### Generate CVs for All Jobs
```bash
python cv_optimizer_app.py [SPREADSHEET_ID] --all-jobs
```

#### Generate Without AI Optimization
```bash
python cv_optimizer_app.py [SPREADSHEET_ID] --job-row 5 --no-ai
```

#### Generate Spanish CV
```bash
python cv_optimizer_app.py [SPREADSHEET_ID] --job-row 5 --language spanish --cv-template templates/base_cv_spanish.json
```

### Google Sheets Format

Your Google Sheet should have the following columns:

| Column | Description |
|--------|-------------|
| A | Job Title |
| B | Company |
| C | Job Description |
| D | Job URL |
| E | Location |
| F | CV Generated (URL) |
| G | Status |
| H | Notes |
| I | Last Updated |

## 🏗️ Project Structure

```
ai-cv-optimizer/
├── src/                          # Source code
│   ├── cv_optimizer.py          # AI CV optimization logic
│   ├── sheets_reader_oauth.py   # Google Sheets integration
│   └── cv_generator_oauth.py    # Google Docs generation
├── scripts/                     # Utility scripts
│   └── get_api_key.py          # Secure API key retrieval
├── templates/                   # CV templates
│   ├── example_cv.json         # Example CV structure
│   ├── base_cv_english.json    # English CV template (create from example)
│   └── base_cv_spanish.json    # Spanish CV template
├── cv_optimizer_app.py         # Main application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore file
├── SECURITY.md               # Security guidelines
└── README.md                  # This file
```

## 🔒 Security Features

- **API Key Protection**: OpenAI API keys stored securely in macOS Keychain
- **OAuth 2.0**: Secure Google account authentication
- **Git Protection**: Comprehensive .gitignore prevents credential leaks
- **Token Management**: Automatic OAuth token refresh
- **Environment Isolation**: All sensitive data in environment variables

## 💰 Cost Estimation

- **OpenAI API**: ~$0.002 per 1K tokens (approximately $0.10-0.50 per CV optimization)
- **Google APIs**: Free (within generous quotas)
- **Total**: ~$2-10/month for moderate usage (20-50 CV generations)

## 🚧 Future Enhancements

- [ ] Web interface using Streamlit
- [ ] Resume parsing from PDF files
- [ ] A/B testing for CV variations
- [ ] Analytics dashboard for success tracking
- [ ] LinkedIn integration
- [ ] Cover letter generation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is designed to help optimize existing CV content based on job requirements. It does not create false information and should be used responsibly. Always review generated content before submission.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/ai-cv-optimizer/issues) section
2. Create a new issue with detailed information about your problem
3. Provide relevant logs and system information

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- Google for the Workspace APIs
- The Python community for excellent libraries

---

⭐ **If this project helped you land your dream job, please give it a star!** ⭐
