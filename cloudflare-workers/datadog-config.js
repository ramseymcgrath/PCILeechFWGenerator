/**
 * Cloudflare Workers script to serve Datadog configuration
 * Deploy this to https://api.ramseymcgrath.com/datadog-config
 * 
 * Environment variables to set in Cloudflare Workers:
 * - DATADOG_CLIENT_TOKEN: Your Datadog RUM client token
 * - DATADOG_APPLICATION_ID: Your Datadog application ID
 * - DATADOG_ENV: Environment (prd, dev, etc.)
 * - ALLOWED_ORIGINS: Comma-separated list of allowed origins
 */

export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return handleCORS(request, env);
    }

    // Only allow GET requests
    if (request.method !== 'GET') {
      return new Response('Method not allowed', { 
        status: 405,
        headers: {
          'Allow': 'GET, OPTIONS',
          ...getCORSHeaders(request, env)
        }
      });
    }

    try {
      // Validate origin
      const origin = request.headers.get('Origin');
      if (!isValidOrigin(origin, env)) {
        return new Response('Forbidden', { 
          status: 403,
          headers: getCORSHeaders(request, env)
        });
      }

      // Get configuration from environment variables
      const config = {
        clientToken: env.DATADOG_CLIENT_TOKEN,
        applicationId: env.DATADOG_APPLICATION_ID,
        site: 'datadoghq.com',
        service: 'pcileechfwgenerator',
        env: env.DATADOG_ENV || 'prd',
        sessionSampleRate: 100,
        sessionReplaySampleRate: 20,
        defaultPrivacyLevel: 'mask-user-input',
        version: env.APP_VERSION || '1.0.0',
      };

      // Validate that required environment variables are set
      if (!config.clientToken || !config.applicationId) {
        console.error('Missing required Datadog configuration');
        return new Response('Configuration error', { 
          status: 500,
          headers: getCORSHeaders(request, env)
        });
      }

      return new Response(JSON.stringify(config), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=300', // Cache for 5 minutes
          ...getCORSHeaders(request, env)
        },
      });

    } catch (error) {
      console.error('Error serving Datadog config:', error);
      return new Response('Internal server error', { 
        status: 500,
        headers: getCORSHeaders(request, env)
      });
    }
  },
};

function isValidOrigin(origin, env) {
  const allowedOrigins = [
    'https://pcileechfwgenerator.ramseymcgrath.com',
    'https://ramseymcgrath.github.io',
    'http://localhost:8000', // For local development
    'http://127.0.0.1:8000',
  ];

  // Add custom allowed origins from environment
  if (env.ALLOWED_ORIGINS) {
    allowedOrigins.push(...env.ALLOWED_ORIGINS.split(',').map(o => o.trim()));
  }

  return allowedOrigins.includes(origin);
}

function getCORSHeaders(request, env) {
  const origin = request.headers.get('Origin');
  
  const headers = {
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400', // 24 hours
  };

  if (isValidOrigin(origin, env)) {
    headers['Access-Control-Allow-Origin'] = origin;
  }

  return headers;
}

function handleCORS(request, env) {
  return new Response(null, {
    status: 204,
    headers: getCORSHeaders(request, env),
  });
}
