# 🌐 Beat Suite AI - Google Cloud Deployment Guide

Complete step-by-step guide to deploy Beat Suite AI to Google Cloud Platform.

---

## 📋 Table of Contents

1. [Deployment Options](#deployment-options)
2. [Prerequisites](#prerequisites)
3. [Cloud Run Deployment (Recommended)](#cloud-run-deployment-recommended)
4. [App Engine Deployment](#app-engine-deployment)
5. [Compute Engine (VM) Deployment](#compute-engine-vm-deployment)
6. [Database Setup (Cloud SQL)](#database-setup-cloud-sql)
7. [Environment Configuration](#environment-configuration)
8. [Domain & SSL Setup](#domain--ssl-setup)
9. [Monitoring & Logging](#monitoring--logging)
10. [Cost Optimization](#cost-optimization)

---

## 🎯 Deployment Options

### Option 1: Cloud Run (Serverless) ⭐ RECOMMENDED
- **Best for**: Production, Auto-scaling, Pay-per-use
- **Setup time**: 10-15 minutes
- **Cost**: ~$5-20/month (scales to zero)
- **Pros**: Automatic HTTPS, auto-scaling, easy deployment
- **Cons**: Cold starts (1-2 seconds)

### Option 2: App Engine (PaaS)
- **Best for**: Simple deployment, managed infrastructure
- **Setup time**: 15-20 minutes
- **Cost**: ~$25-50/month (always running)
- **Pros**: Zero configuration, automatic scaling
- **Cons**: Less control, higher cost

### Option 3: Compute Engine (VMs)
- **Best for**: Full control, hybrid deployments
- **Setup time**: 30-45 minutes
- **Cost**: ~$30-100/month
- **Pros**: Complete control, SSH access
- **Cons**: Manual management, more complex

---

## ✅ Prerequisites

### 1. Google Cloud Account
```bash
# Sign up at: https://console.cloud.google.com
# New accounts get $300 free credits for 90 days
```

### 2. Install Google Cloud CLI
```bash
# macOS
brew install google-cloud-sdk

# Or download from:
# https://cloud.google.com/sdk/docs/install

# Verify installation
gcloud --version
```

### 3. Authenticate & Setup
```bash
# Login to Google Cloud
gcloud auth login

# Create new project (or use existing)
gcloud projects create beatsuite-ai-prod --name="Beat Suite AI"

# Set as active project
gcloud config set project beatsuite-ai-prod

# Enable billing (required)
# Go to: https://console.cloud.google.com/billing

# Link project to billing account
gcloud beta billing projects link beatsuite-ai-prod \
  --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### 4. Enable Required APIs
```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com

# Enable Secret Manager (for API keys)
gcloud services enable secretmanager.googleapis.com

# Optional: Cloud SQL (for production database)
gcloud services enable sqladmin.googleapis.com
```

---

## 🚀 Cloud Run Deployment (RECOMMENDED)

Cloud Run is serverless, scales automatically, and only charges when requests are being processed.

### Step 1: Prepare Your Application

Create `Dockerfile` in project root:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p backend/data/backup

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 run:app
```

### Step 2: Add Gunicorn to Requirements

```bash
# Add to requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt
```

### Step 3: Update run.py for Production

Create/update `run.py`:

```python
# run.py
import os
from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Step 4: Create .dockerignore

```bash
# .dockerignore
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.gitignore
.DS_Store
.env
.env.local
*.log
node_modules/
.vscode/
.idea/
```

### Step 5: Build & Deploy to Cloud Run

```bash
# Set your project ID
export PROJECT_ID="beatsuite-ai-prod"
export REGION="us-central1"
export SERVICE_NAME="beatsuite-ai"

# Build container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "ENVIRONMENT=production"

# You'll get a URL like:
# https://beatsuite-ai-xxxxx-uc.a.run.app
```

### Step 6: Add Environment Variables (Secrets)

```bash
# Create secrets in Secret Manager
echo -n "your_google_api_key_here" | \
  gcloud secrets create GOOGLE_API_KEY --data-file=-

echo -n "your_strong_secret_key_here" | \
  gcloud secrets create SECRET_KEY --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding SECRET_KEY \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run service with secrets
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SECRET_KEY=SECRET_KEY:latest"
```

### Step 7: Test Your Deployment

```bash
# Get service URL
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)'

# Test health endpoint
curl https://YOUR-SERVICE-URL.run.app/api/health

# Open in browser
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)' | xargs open
```

### Step 8: Update Google Home Webhook

```bash
# Get your Cloud Run URL
export CLOUD_RUN_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)')

echo "Update Google Actions Console webhook to:"
echo "$CLOUD_RUN_URL/api/google-home/fulfillment"

# Go to: https://console.actions.google.com
# Update webhook URL to your Cloud Run URL
```

---

## 🏗️ App Engine Deployment

Simpler but less flexible than Cloud Run.

### Step 1: Create app.yaml

```yaml
# app.yaml
runtime: python311

env: standard
instance_class: F1

entrypoint: gunicorn -b :$PORT run:app

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 10
  min_pending_latency: 30ms
  max_pending_latency: automatic
  max_concurrent_requests: 50

env_variables:
  ENVIRONMENT: 'production'

handlers:
- url: /static
  static_dir: frontend/static
  secure: always

- url: /.*
  script: auto
  secure: always
```

### Step 2: Deploy

```bash
# Deploy to App Engine
gcloud app deploy app.yaml

# Set environment variables
gcloud app deploy --set-env-vars GOOGLE_API_KEY=your_key,SECRET_KEY=your_secret

# View application
gcloud app browse
```

---

## 💻 Compute Engine (VM) Deployment

Full control with a virtual machine.

### Step 1: Create VM Instance

```bash
# Create VM
gcloud compute instances create beatsuite-ai-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --tags=http-server,https-server

# Create firewall rules
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --target-tags http-server

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --target-tags https-server
```

### Step 2: SSH and Setup

```bash
# SSH into VM
gcloud compute ssh beatsuite-ai-vm --zone=us-central1-a

# Once inside VM:
sudo apt update
sudo apt install -y python3.11 python3-pip git nginx

# Clone repository
git clone https://github.com/apkirana/beatsuite-ai.git
cd beatsuite-ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
EOF

# Test application
python run.py
```

### Step 3: Configure Nginx

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/beatsuite-ai

# Add configuration:
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/YOUR_USERNAME/beatsuite-ai/frontend/static;
        expires 30d;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/beatsuite-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 4: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/beatsuite-ai.service

# Add content:
[Unit]
Description=Beat Suite AI Application
After=network.target

[Service]
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/beatsuite-ai
Environment="PATH=/home/YOUR_USERNAME/beatsuite-ai/.venv/bin"
ExecStart=/home/YOUR_USERNAME/beatsuite-ai/.venv/bin/gunicorn \
    --bind 127.0.0.1:5001 \
    --workers 4 \
    --timeout 120 \
    run:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable beatsuite-ai
sudo systemctl start beatsuite-ai
sudo systemctl status beatsuite-ai
```

---

## 🗄️ Database Setup (Cloud SQL)

For production, use Cloud SQL instead of JSON files.

### Step 1: Create PostgreSQL Instance

```bash
# Create Cloud SQL instance
gcloud sql instances create beatsuite-ai-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=STRONG_PASSWORD_HERE

# Create database
gcloud sql databases create beatsuite_prod \
  --instance=beatsuite-ai-db

# Create user
gcloud sql users create beatsuite_user \
  --instance=beatsuite-ai-db \
  --password=USER_PASSWORD_HERE
```

### Step 2: Connect Cloud Run to Cloud SQL

```bash
# Get connection name
gcloud sql instances describe beatsuite-ai-db \
  --format='value(connectionName)'

# Update Cloud Run with Cloud SQL connection
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --add-cloudsql-instances=PROJECT_ID:REGION:beatsuite-ai-db \
  --set-env-vars="DATABASE_URL=postgresql://beatsuite_user:USER_PASSWORD@/beatsuite_prod?host=/cloudsql/PROJECT_ID:REGION:beatsuite-ai-db"
```

### Step 3: Migrate JSON to PostgreSQL

Update `backend/database/db.py` to use PostgreSQL:

```python
# backend/database/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///beatsuite.db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

## ⚙️ Environment Configuration

### Production Environment Variables

```bash
# Set all required environment variables
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-env-vars="
ENVIRONMENT=production,
LOG_LEVEL=INFO,
SECRET_KEY=your_secret_key,
GOOGLE_API_KEY=your_gemini_api_key,
DATABASE_URL=postgresql://user:pass@host/db,
ALLOWED_ORIGINS=https://yourdomain.com
"
```

### Using Secret Manager (Best Practice)

```bash
# Store sensitive data in Secret Manager
echo -n "your_api_key" | gcloud secrets create GOOGLE_API_KEY --data-file=-
echo -n "your_secret" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "db_password" | gcloud secrets create DB_PASSWORD --data-file=-

# Use in Cloud Run
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-secrets="
GOOGLE_API_KEY=GOOGLE_API_KEY:latest,
SECRET_KEY=SECRET_KEY:latest,
DB_PASSWORD=DB_PASSWORD:latest
"
```

---

## 🌐 Domain & SSL Setup

### Option 1: Cloud Run Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service $SERVICE_NAME \
  --domain api.yourdomain.com \
  --region $REGION

# Get DNS records to add
gcloud run domain-mappings describe \
  --domain api.yourdomain.com \
  --region $REGION

# Add DNS records at your domain provider:
# - Type: A
# - Name: api
# - Value: (IP from above command)
```

### Option 2: Cloud Load Balancer + SSL

```bash
# Create SSL certificate
gcloud compute ssl-certificates create beatsuite-ssl \
  --domains=api.yourdomain.com

# Create backend service
gcloud compute backend-services create beatsuite-backend \
  --global

# Create load balancer
# Follow: https://cloud.google.com/load-balancing/docs/https
```

---

## 📊 Monitoring & Logging

### Enable Cloud Monitoring

```bash
# View logs
gcloud run logs read $SERVICE_NAME \
  --region $REGION \
  --limit 50

# Follow logs in real-time
gcloud run logs tail $SERVICE_NAME \
  --region $REGION

# View in console
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)' | sed 's/https:\/\//https:\/\/console.cloud.google.com\/run\/detail\//g'
```

### Set Up Alerts

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

### Add Health Checks

```python
# backend/app.py - Add health endpoint
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })
```

---

## 💰 Cost Optimization

### Cloud Run Cost Estimates

```
Pricing (as of 2025):
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million requests

Example (1000 users/day):
- ~100,000 requests/month
- Average 500ms response time
- 1 vCPU, 1GB memory
= ~$5-10/month
```

### Optimization Tips

```bash
# 1. Set max instances (prevent runaway costs)
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --max-instances 10

# 2. Set min instances (reduce cold starts, increases cost)
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --min-instances 1

# 3. Adjust CPU allocation
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --cpu 1 \
  --memory 1Gi

# 4. Set timeout
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --timeout 60
```

---

## 🎯 Complete Deployment Script

Save as `deploy-to-gcp.sh`:

```bash
#!/bin/bash
# deploy-to-gcp.sh - Complete deployment script

set -e

# Configuration
PROJECT_ID="beatsuite-ai-prod"
REGION="us-central1"
SERVICE_NAME="beatsuite-ai"

echo "🚀 Deploying Beat Suite AI to Google Cloud..."

# 1. Set project
gcloud config set project $PROJECT_ID

# 2. Build container
echo "📦 Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 3. Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SECRET_KEY=SECRET_KEY:latest"

# 4. Get URL
URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 URL: $URL"
echo "🏥 Dashboard: $URL/dashboard"
echo "🎮 IoT Simulator: $URL/iot-simulator"
echo ""
echo "📝 Next steps:"
echo "1. Update Google Home webhook to: $URL/api/google-home/fulfillment"
echo "2. Test: curl $URL/api/health"
echo "3. Login at: $URL/login"
```

Run it:
```bash
chmod +x deploy-to-gcp.sh
./deploy-to-gcp.sh
```

---

## ✅ Post-Deployment Checklist

- [ ] Test health endpoint: `/api/health`
- [ ] Test login: `/login` with admin credentials
- [ ] Test dashboard: `/dashboard`
- [ ] Test IoT simulator: `/iot-simulator`
- [ ] Update Google Home webhook URL
- [ ] Test voice commands: "Hey Google, check room 101"
- [ ] Check logs for errors
- [ ] Set up monitoring alerts
- [ ] Configure custom domain (optional)
- [ ] Enable Cloud CDN (optional)
- [ ] Set up automated backups
- [ ] Document production URLs for team

---

## 🐛 Troubleshooting

### Issue: Build fails
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID

# Common fixes:
# 1. Check Dockerfile syntax
# 2. Verify requirements.txt
# 3. Check .dockerignore
```

### Issue: Deployment fails
```bash
# Check service logs
gcloud run logs read $SERVICE_NAME --region $REGION

# Common fixes:
# 1. Check PORT environment variable (must be 8080)
# 2. Verify secrets are created
# 3. Check IAM permissions
```

### Issue: 502 Bad Gateway
```bash
# Check application logs
gcloud run logs tail $SERVICE_NAME --region $REGION

# Common causes:
# 1. Application not binding to 0.0.0.0
# 2. Port mismatch (use $PORT env var)
# 3. Application crash on startup
```

---

## 📚 Additional Resources

- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud SQL Quickstart](https://cloud.google.com/sql/docs/postgres/quickstart)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)
- [Cloud Monitoring](https://cloud.google.com/monitoring/docs)

---

**🎉 You're now running Beat Suite AI on Google Cloud Platform!**

For questions: Check [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) or create a GitHub issue.
