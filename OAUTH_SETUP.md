# Switch to OAuth Authentication

The service account approach won't work because service accounts don't have Google Drive storage. We need to use OAuth to create documents in your personal Google Drive.

## Steps to Switch to OAuth:

### 1. Create OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop application"
4. Name it "CV Optimizer Desktop"
5. Download the credentials JSON file and save it as `oauth_credentials.json`

### 2. Update the Code
We'll modify the code to use OAuth instead of service account authentication.

### 3. First-time Setup
- The first time you run the application, it will open a browser
- You'll need to grant permissions to access your Google Drive and Docs
- After that, it will work automatically

## Benefits of OAuth:
- ✅ Uses your personal Google Drive storage
- ✅ Documents appear in your Drive
- ✅ No quota issues
- ✅ More straightforward permissions

The service account approach is better for server applications, but for personal tools like this CV optimizer, OAuth is the right choice.
