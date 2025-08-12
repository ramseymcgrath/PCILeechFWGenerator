# Cloudflare Workers Deployment

This directory contains Cloudflare Workers scripts for the PCILeech Firmware Generator project.

## Setup

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Authenticate with Cloudflare

```bash
wrangler login
```

### 3. Create wrangler.toml

Create a `wrangler.toml` file in this directory:

```toml
name = "datadog-config-api"
main = "datadog-config.js"
compatibility_date = "2024-01-01"

[env.production]
route = "api.ramseymcgrath.com/datadog-config"

[env.development]
route = "dev-api.ramseymcgrath.com/datadog-config"
```

### 4. Set Environment Variables

Set the required environment variables in Cloudflare Dashboard or via CLI:

```bash
# Production environment
wrangler secret put DATADOG_CLIENT_TOKEN --env production
wrangler secret put DATADOG_APPLICATION_ID --env production
wrangler secret put DATADOG_ENV --env production  # Set to "prd"

# Development environment (optional)
wrangler secret put DATADOG_CLIENT_TOKEN --env development
wrangler secret put DATADOG_APPLICATION_ID --env development
wrangler secret put DATADOG_ENV --env development  # Set to "dev"
```

### 5. Deploy

```bash
# Deploy to production
wrangler deploy --env production

# Deploy to development
wrangler deploy --env development
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATADOG_CLIENT_TOKEN` | Yes | Your Datadog RUM client token |
| `DATADOG_APPLICATION_ID` | Yes | Your Datadog application ID |
| `DATADOG_ENV` | No | Environment name (defaults to "prd") |
| `ALLOWED_ORIGINS` | No | Comma-separated list of additional allowed origins |
| `APP_VERSION` | No | Application version for tracking |

## Security Features

- **CORS Protection**: Only allows requests from specified origins
- **Method Restriction**: Only allows GET and OPTIONS requests
- **Environment Variables**: Sensitive data stored securely in Cloudflare
- **Error Handling**: Graceful error handling without exposing internal details
- **Caching**: 5-minute cache to reduce API calls

## Testing

Test the endpoint:

```bash
curl -H "Origin: https://pcileechfwgenerator.ramseymcgrath.com" \
     https://api.ramseymcgrath.com/datadog-config
```

Expected response:
```json
{
  "clientToken": "pub...",
  "applicationId": "eba2cf10-...",
  "site": "datadoghq.com",
  "service": "pcileechfwgenerator",
  "env": "prd",
  "sessionSampleRate": 100,
  "sessionReplaySampleRate": 20,
  "defaultPrivacyLevel": "mask-user-input",
  "version": "1.0.0"
}
```
