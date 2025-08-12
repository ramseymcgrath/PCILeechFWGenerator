#!/bin/bash

# Cloudflare Workers Deployment Script for Datadog Config API
# Usage: ./deploy.sh [production|development]

set -e

ENVIRONMENT=${1:-production}

echo "🚀 Deploying Datadog Config API to $ENVIRONMENT environment..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found. Please install it:"
    echo "   npm install -g wrangler"
    exit 1
fi

# Check if user is logged in
if ! wrangler whoami &> /dev/null; then
    echo "❌ Not logged in to Cloudflare. Please run:"
    echo "   wrangler login"
    exit 1
fi

# Validate environment
if [[ "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "development" ]]; then
    echo "❌ Invalid environment. Use 'production' or 'development'"
    exit 1
fi

# Change to the cloudflare-workers directory
cd "$(dirname "$0")"

echo "📦 Deploying to $ENVIRONMENT environment..."

# Deploy the worker
if wrangler deploy --env "$ENVIRONMENT"; then
    echo "✅ Successfully deployed Datadog Config API to $ENVIRONMENT"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        ENDPOINT="https://api.ramseymcgrath.com/datadog-config"
    else
        ENDPOINT="https://dev-api.ramseymcgrath.com/datadog-config"
    fi
    
    echo "🔗 Endpoint: $ENDPOINT"
    echo ""
    echo "🧪 Test the deployment:"
    echo "   curl -H \"Origin: https://pcileechfwgenerator.ramseymcgrath.com\" $ENDPOINT"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Verify the endpoint returns the expected JSON"
    echo "   2. Update your site's JavaScript to use this endpoint"
    echo "   3. Test the integration on your documentation site"
else
    echo "❌ Deployment failed"
    exit 1
fi
