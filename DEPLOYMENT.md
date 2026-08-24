# 🚀 Beat Suite AI - Deployment Guide

Complete guide for source code management, Git workflow, and Google Cloud Platform deployment.

---

## 📋 Table of Contents

1. [Source Code Structure](#source-code-structure)
2. [Git Workflow](#git-workflow)
3. [Local Development](#local-development)
4. [Deploy to Google Cloud Platform](#deploy-to-google-cloud-platform)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)

---

## 📁 Source Code Structure

```
hqgoogle/
├── backend/                      # Backend Python application
│   ├── ai/                       # AI/Gemini services
│   │   └── gemini_service.py    # Gemini AI integration
│   ├── api/                      # API route modules
│   │   ├── ai_routes.py         # AI endpoints (analysis, Gemini Live token)
│   │   ├── healthcare_routes.py # Patient, room, vitals management
│   │   └── monitoring_routes.py # Real-time monitoring, alerts
│   ├── auth/                     # Authentication system
│   │   ├── auth.py              # Login/logout handlers
│   │   └── decorators.py        # @login_required, @role_required
│   ├── core/                     # Core business logic
│   │   ├── smartwatch.py        # Smartwatch vitals tracking
│   │   └── alerts.py            # Alert generation system
│   └── app.py                   # Flask application entry point
│
├── frontend/                     # Frontend web application
│   ├── static/
│   │   ├── css/
│   │   │   ├── dashboard.css    # Main dashboard styles
│   │   │   └── login.css        # Login page styles
│   │   ├── js/
│   │   │   ├── dashboard.js     # Dashboard logic & UI
│   │   │   ├── gemini_live.js   # 🎙️ Gemini Live voice chat
│   │   │   ├── smart_assistant.js # AI assistant (text)
│   │   │   └── report_generator.js # Report generation
│   │   └── images/              # Logos and assets
│   └── templates/
│       ├── dashboard.html       # Main dashboard page
│       └── login.html           # Login page
│
├── data/                         # Data storage
│   └── rooms.json               # Patient room data
│
├── app                          # 🔧 Server control script
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .dockerignore               # Docker ignore rules
├── cloudbuild.yaml             # GCP Cloud Build config
├── .env                        # Environment variables (LOCAL ONLY)
└── .gitignore                  # Git ignore rules
```

---

## 🔄 Git Workflow

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/apkirana/beatsuite-ai.git
cd beatsuite-ai

# Check current branch
git branch
```

### Making Changes

```bash
# 1. Check status of modified files
git status

# 2. View changes
git diff

# 3. Stage specific files
git add backend/api/ai_routes.py
git add frontend/static/js/gemini_live.js

# OR stage all changes
git add .

# 4. Commit with descriptive message
git commit -m "feat: Add Gemini Live real-time voice chat feature"

# 5. Push to GitHub
git push origin main
```

### Commit Message Conventions

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `docs:` - Documentation changes
- `style:` - Formatting, CSS changes
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: Add Gemini Live WebSocket integration"
git commit -m "fix: Resolve bottom overlap in assistant modal"
git commit -m "refactor: Consolidate API routes into healthcare module"
git commit -m "docs: Update deployment guide with GCP instructions"
```

### Viewing History

```bash
# View commit history
git log --oneline

# View changes in specific commit
git show <commit-hash>

# View file history
git log --follow frontend/static/js/gemini_live.js
```

---

## 💻 Local Development

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Git
- Google API Key (for Gemini AI)

### Setup

```bash
# 1. Clone repository
git clone https://github.com/apkirana/beatsuite-ai.git
cd beatsuite-ai

# 2. Create .env file with your API key
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env

# 3. Start the server (creates venv, installs deps, starts Flask)
./app start

# Server will run at http://localhost:5001
```

### Server Control Commands

```bash
# Start server
./app start

# Stop server
./app stop

# Restart server (after code changes)
./app restart

# Check server status
./app status
```

### Login Credentials

No accounts ship with the code. Create them on the instance:

```bash
python scripts/seed_users.py
```

The script generates a random password for each role (`admin`, `nurse1`, `nurse2`, `family1`) and
prints them **once** — save them straight into a password manager. Only salted PBKDF2 hashes are
written to `backend/data/users.json`, which is gitignored and must stay that way.

---

## ☁️ Deploy to Google Cloud Platform

### Prerequisites

1. **GCP Account**: https://cloud.google.com
2. **gcloud CLI**: Install from https://cloud.google.com/sdk/docs/install
3. **Docker**: Install from https://www.docker.com/get-started

### One-Time GCP Setup

```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Set your project ID
gcloud config set project beatsuite-675304702130

# 3. Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# 4. Authenticate Docker
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Deployment Methods

#### Method 1: Using gcloud (Recommended)

```bash
# Deploy directly from source code
gcloud run deploy beatsuite \
  --source . \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=your_api_key_here"
```

#### Method 2: Using Cloud Build (with cloudbuild.yaml)

```bash
# 1. Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Build will:
# - Build Docker image
# - Push to Artifact Registry
# - Deploy to Cloud Run
```

#### Method 3: Manual Docker Build & Deploy

```bash
# 1. Build Docker image
docker build -t us-central1-docker.pkg.dev/beatsuite-675304702130/cloud-run-source-deploy/beatsuite .

# 2. Push to Artifact Registry
docker push us-central1-docker.pkg.dev/beatsuite-675304702130/cloud-run-source-deploy/beatsuite

# 3. Deploy to Cloud Run
gcloud run deploy beatsuite \
  --image=us-central1-docker.pkg.dev/beatsuite-675304702130/cloud-run-source-deploy/beatsuite \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=your_api_key_here"
```

### Complete Deployment Workflow

```bash
# 1. Make code changes locally
vim frontend/static/js/gemini_live.js

# 2. Test locally
./app restart
# Test at http://localhost:5001

# 3. Commit and push to GitHub
git add .
git commit -m "feat: Improve Gemini Live UI"
git push origin main

# 4. Deploy to GCP
gcloud run deploy beatsuite \
  --source . \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=your_api_key_here"

# 5. Access deployed app
# URL: https://beatsuite-675304702130.us-central1.run.app
```

### Setting Environment Variables in Cloud Run

```bash
# Set GOOGLE_API_KEY
gcloud run services update beatsuite \
  --region=us-central1 \
  --set-env-vars="GOOGLE_API_KEY=your_api_key_here"

# Add multiple environment variables
gcloud run services update beatsuite \
  --region=us-central1 \
  --set-env-vars="GOOGLE_API_KEY=key1,OTHER_VAR=value2"

# View current environment variables
gcloud run services describe beatsuite \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### View Deployment Logs

```bash
# View recent logs
gcloud run services logs read beatsuite \
  --region=us-central1 \
  --limit=50

# Tail logs in real-time
gcloud run services logs tail beatsuite \
  --region=us-central1
```

---

## 🔐 Environment Variables

### Local Development (.env file)

Create a `.env` file in the project root:

```bash
# .env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
FLASK_ENV=development
FLASK_DEBUG=1
```

⚠️ **NEVER commit .env to Git!** It's in `.gitignore` for security.

### GCP Cloud Run

Set via command line:

```bash
gcloud run services update beatsuite \
  --region=us-central1 \
  --set-env-vars="GOOGLE_API_KEY=your_key_here"
```

Or via GCP Console:
1. Go to Cloud Run → beatsuite
2. Click "Edit & Deploy New Revision"
3. Go to "Variables & Secrets" tab
4. Add environment variable: `GOOGLE_API_KEY`
5. Deploy

---

## 🐛 Troubleshooting

### Local Development Issues

#### Server won't start
```bash
# Check if port 5001 is already in use
lsof -ti:5001

# Kill process using port
kill -9 $(lsof -ti:5001)

# Restart server
./app restart
```

#### Missing dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

#### GOOGLE_API_KEY not loaded
```bash
# Check if .env file exists
cat .env

# Manually load environment variables
source .env

# Restart server
./app restart
```

### Git Issues

#### Accidentally committed .env file
```bash
# Remove from Git but keep local file
git rm --cached .env
git commit -m "chore: Remove .env from Git"
git push origin main

# Make sure .env is in .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: Add .env to .gitignore"
git push origin main
```

#### Need to undo last commit
```bash
# Undo commit but keep changes
git reset --soft HEAD~1

# Undo commit and discard changes
git reset --hard HEAD~1
```

#### Merge conflicts
```bash
# View conflicted files
git status

# Resolve conflicts in editor
vim <conflicted-file>

# Mark as resolved
git add <conflicted-file>
git commit -m "fix: Resolve merge conflicts"
```

### GCP Deployment Issues

#### Build fails
```bash
# Check build logs
gcloud builds log <build-id>

# Common fixes:
# 1. Check Dockerfile syntax
# 2. Ensure requirements.txt is up to date
# 3. Verify all files are committed to Git
```

#### Service Unavailable (503)
```bash
# Check logs
gcloud run services logs read beatsuite --region=us-central1 --limit=100

# Common causes:
# 1. Missing dependencies in requirements.txt
# 2. GOOGLE_API_KEY not set
# 3. Application crashes on startup
```

#### Container fails to start
```bash
# View detailed logs
gcloud run services logs tail beatsuite --region=us-central1

# Check service configuration
gcloud run services describe beatsuite --region=us-central1

# Test locally with Docker
docker build -t beatsuite-test .
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key beatsuite-test
```

---

## 📊 Monitoring & Maintenance

### View Service Status

```bash
# Cloud Run service details
gcloud run services describe beatsuite --region=us-central1

# Recent revisions
gcloud run revisions list --service=beatsuite --region=us-central1

# Current traffic distribution
gcloud run services describe beatsuite \
  --region=us-central1 \
  --format="value(status.traffic)"
```

### Update Service Configuration

```bash
# Update memory/CPU limits
gcloud run services update beatsuite \
  --region=us-central1 \
  --memory=512Mi \
  --cpu=1

# Update timeout
gcloud run services update beatsuite \
  --region=us-central1 \
  --timeout=300s

# Update max instances
gcloud run services update beatsuite \
  --region=us-central1 \
  --max-instances=10
```

---

## 🎯 Quick Reference

### Common Git Commands

```bash
git status                          # Check status
git add .                          # Stage all changes
git commit -m "message"            # Commit changes
git push origin main               # Push to GitHub
git pull origin main               # Pull latest changes
git log --oneline                  # View history
```

### Common GCP Commands

```bash
# Deploy
gcloud run deploy beatsuite --source . --region=us-central1

# View logs
gcloud run services logs read beatsuite --region=us-central1

# Update env vars
gcloud run services update beatsuite --set-env-vars="KEY=value"

# Describe service
gcloud run services describe beatsuite --region=us-central1
```

### Server Commands

```bash
./app start                        # Start server
./app stop                         # Stop server
./app restart                      # Restart server
./app status                       # Check status
tail -f server.log                 # View logs
```

---

## 📝 Additional Resources

- **Google Cloud Run Docs**: https://cloud.google.com/run/docs
- **Cloud Build Docs**: https://cloud.google.com/build/docs
- **Git Documentation**: https://git-scm.com/doc
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Gemini API Docs**: https://ai.google.dev/docs

---

## 🆘 Support

If you encounter issues:

1. Check logs: `tail -f server.log` (local) or `gcloud run services logs` (GCP)
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check Git commits are pushed before deploying
5. Review GCP quota limits and billing

---

**Last Updated**: November 19, 2025  
**Version**: 2.0 (Gemini Live Integration)  
**Deployed URL**: https://beatsuite-675304702130.us-central1.run.app
