#!/bin/bash
# deploy-to-gcp.sh - Quick deployment script for Google Cloud Run

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Beat Suite AI - Google Cloud Deployment${NC}"
echo "=============================================="
echo ""

# Configuration (customize these)
PROJECT_ID="${GCP_PROJECT_ID:-beatsuite-ai-prod}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-beatsuite-ai}"

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service Name: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found!${NC}"
    echo "Install it: brew install google-cloud-sdk"
    exit 1
fi

echo -e "${GREEN}✓ gcloud CLI found${NC}"

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
    echo -e "${RED}❌ Not logged in to gcloud${NC}"
    echo "Run: gcloud auth login"
    exit 1
fi

echo -e "${GREEN}✓ Authenticated${NC}"

# Set project
echo ""
echo "🔧 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo "🔌 Enabling required APIs..."
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
echo -e "${GREEN}✓ APIs enabled${NC}"

# Build container
echo ""
echo "📦 Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME --quiet

echo -e "${GREEN}✓ Container built${NC}"

# Deploy to Cloud Run
echo ""
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
  --set-env-vars "ENVIRONMENT=production" \
  --quiet

echo -e "${GREEN}✓ Deployed successfully!${NC}"

# Get service URL
URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)')

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo "🌐 Service URL: $URL"
echo ""
echo "📱 Access Points:"
echo "   Login:         $URL/login"
echo "   Dashboard:     $URL/dashboard"
echo "   IoT Simulator: $URL/iot-simulator"
echo "   Admin Panel:   $URL/admin"
echo ""
echo "🔗 API Endpoints:"
echo "   Health:        $URL/api/health"
echo "   Google Home:   $URL/api/google-home/fulfillment"
echo ""
echo "📝 Next Steps:"
echo "1. Test health: curl $URL/api/health"
echo "2. Login with: admin / admin123"
echo "3. Update Google Home webhook to: $URL/api/google-home/fulfillment"
echo ""
echo "⚠️  Don't forget to add secrets:"
echo "   gcloud secrets create GOOGLE_API_KEY --data-file=-"
echo "   gcloud secrets create SECRET_KEY --data-file=-"
echo ""
echo "🎉 Happy deploying!"
