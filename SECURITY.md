# Security Guidelines 🔒

This document outlines security measures implemented in the AI CV Optimizer to protect your personal data and credentials.

## 🛡️ Built-in Security Features

### 1. Environment Variable Protection
- All API keys and sensitive configuration stored in `.env` file
- `.env` is in `.gitignore` - never committed to version control
- Uses `.env.example` as a template with placeholder values

### 2. Credential Isolation
- Google Service Account credentials stored separately (`credentials.json`)
- Personal CV data excluded from repository
- Generated CVs stored locally only

### 3. Secure API Key Management
- **macOS Keychain integration** - API keys stored securely outside code
- OpenAI API keys never stored in plain text files
- Secure credential retrieval through system APIs

### 4. Data Privacy
- Base CV template not committed to repository
- Generated CVs stored in ignored `output/` directory
- No logging of personal information

## 🚀 Safe Setup Instructions

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/ai-cv-optimizer.git
cd ai-cv-optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Safely)
```bash
# Copy template
cp .env.example .env

# Edit with your values (NEVER commit this file)
nano .env
```

### 3. Add Google Credentials (Securely)
1. Download your Google Service Account JSON
2. Rename it to `credentials.json` 
3. Place in project root (automatically ignored by git)

### 4. Verify Security
```bash
# Check what would be committed
git status

# Should NOT see:
# - .env
# - credentials.json
# - templates/base_cv.json
# - output/ folder
```

## ⚠️ Security Checklist Before Pushing

- [ ] `.env` file is in `.gitignore`
- [ ] `credentials.json` is in `.gitignore`
- [ ] No API keys in code files
- [ ] Personal CV data not included
- [ ] Generated CVs not tracked

## 🔍 What's Safe to Commit

✅ **Safe to commit:**
- Source code files (`*.py`)
- Configuration templates (`.env.example`)
- Documentation (`*.md`)
- Requirements (`requirements.txt`)
- Tests (`tests/`)

❌ **NEVER commit:**
- `.env` file with real values
- `credentials.json`
- Your personal CV data
- Generated CV files
- API keys or tokens

## 🛠️ Additional Security Measures

### For Extra Paranoia:
1. **Use separate Google project** for this tool
2. **Limit Google API scopes** to minimum required
3. **Regular credential rotation** (Google Console)
4. **Review commit history** before pushing

### Environment Variables Used:
```bash
# AI Configuration
AI_PROVIDER=openai
OPENAI_MODEL=gpt-3.5-turbo

# Sensitive (keep secret - use Keychain instead)
# OPENAI_API_KEY stored in macOS Keychain
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_CREDENTIALS_PATH=oauth_credentials.json
```

## 🚨 If You Accidentally Commit Secrets

1. **Don't panic** - remove them immediately:
```bash
# Remove file from git but keep locally
git rm --cached .env

# Commit the removal
git commit -m "Remove accidentally committed secrets"

# Push the fix
git push
```

2. **Rotate compromised credentials**:
   - Generate new Google Service Account key
   - Generate new API keys if exposed
   - Update your `.env` file

3. **For serious leaks**: Consider repository history cleanup tools

## 📞 Security Contact

If you discover security vulnerabilities, please:
1. **Don't** create public issues
2. **Do** contact privately via email
3. Allow reasonable time for fixes

## 🎯 Privacy by Design

This tool is designed with privacy in mind:
- **Local processing** when possible
- **Minimal data collection**
- **No telemetry or analytics**
- **User controls all data**

Remember: The best security is being aware of what you're sharing! 🔐
