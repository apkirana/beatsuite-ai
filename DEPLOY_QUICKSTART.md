# 🚀 Quick Start: Deploy to Google Cloud in 5 Minutes

## Prerequisites
```bash
# 1. Install gcloud CLI
brew install google-cloud-sdk

# 2. Login
gcloud auth login

# 3. Create/select project
gcloud projects create beatsuite-ai-prod
gcloud config set project beatsuite-ai-prod
```

## One-Command Deployment

```bash
# Run the deployment script
./deploy-to-gcp.sh
```

That's it! ✅

## What It Does

1. ✅ Enables required Google Cloud APIs
2. ✅ Builds your Docker container
3. ✅ Deploys to Cloud Run (serverless)
4. ✅ Gives you a public HTTPS URL
5. ✅ Auto-scales based on traffic

## After Deployment

### 1. Add Your API Keys (IMPORTANT!)

```bash
# Add Google Gemini API key
echo -n "your_google_api_key" | \
  gcloud secrets create GOOGLE_API_KEY --data-file=-

# Add secret key
echo -n "$(openssl rand -hex 32)" | \
  gcloud secrets create SECRET_KEY --data-file=-

# Update Cloud Run service to use secrets
gcloud run services update beatsuite-ai \
  --region us-central1 \
  --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SECRET_KEY=SECRET_KEY:latest"
```

### 2. Get Your URL

```bash
# Get service URL
gcloud run services describe beatsuite-ai \
  --region us-central1 \
  --format='value(status.url)'

# Example output:
# https://beatsuite-ai-abc123-uc.a.run.app
```

### 3. Test It

```bash
# Test health endpoint
curl https://YOUR-URL.run.app/api/health

# Open in browser
open https://YOUR-URL.run.app/login
```

### 4. Update Google Home

```bash
# Update your Google Actions Console webhook to:
https://YOUR-URL.run.app/api/google-home/fulfillment
```

## Cost Estimate

**Free tier covers:**
- 2 million requests/month
- 360,000 GB-seconds/month
- 180,000 vCPU-seconds/month

**Typical usage (~1000 users/day):**
- ~$5-10/month
- Scales to zero when not used
- No minimum cost!

## Customization

Edit `deploy-to-gcp.sh` to change:
- Project ID
- Region (default: us-central1)
- Service name
- Memory/CPU allocation

## Full Documentation

For advanced setup, see: [GOOGLE_CLOUD_DEPLOYMENT.md](GOOGLE_CLOUD_DEPLOYMENT.md)

## Troubleshooting

### Issue: "Project not found"
```bash
# Create project first
gcloud projects create beatsuite-ai-prod
```

### Issue: "Billing not enabled"
```bash
# Enable billing at:
https://console.cloud.google.com/billing
```

### Issue: "Permission denied"
```bash
# Make sure you're logged in
gcloud auth login
```

## Need Help?

- Full Guide: [GOOGLE_CLOUD_DEPLOYMENT.md](GOOGLE_CLOUD_DEPLOYMENT.md)
- Complete Docs: [docs/COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md)
- GitHub Issues: https://github.com/apkirana/beatsuite-ai/issues

---

**That's it! You're now running on Google Cloud! 🎉**
