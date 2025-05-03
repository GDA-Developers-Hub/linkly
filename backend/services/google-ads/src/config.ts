export const GOOGLE_OAUTH2_CLIENT_CONFIG = {
  web: {
    client_id: "507214707983-ubsf2ev7qkbcre4j4icsm8hvbq7id31a.apps.googleusercontent.com",
    project_id: "linkly-458619",
    auth_uri: "https://accounts.google.com/o/oauth2/auth",
    token_uri: "https://oauth2.googleapis.com/token",
    auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs",
    client_secret: "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",
    redirect_uris: ["http://localhost:8000/auth/google/callback"],
    javascript_origins: ["http://localhost:3000"]
  }
};

// Google Ads API specific configuration
export const GOOGLE_ADS_CONFIG = {
  developer_token: process.env.GOOGLE_ADS_DEVELOPER_TOKEN || '', // You'll need to set this
  login_customer_id: process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID || '', // Optional: Your Google Ads manager account ID
  use_proto_plus: true,
};

// OAuth2 configuration
export const OAUTH2_SCOPES = [
  'https://www.googleapis.com/auth/adwords',
  'https://www.googleapis.com/auth/userinfo.email'
];

// API endpoints
export const API_ENDPOINTS = {
  auth: {
    init: '/api/google-ads/auth/init',
    callback: '/api/google-ads/auth/callback'
  },
  account: '/api/google-ads/account',
  campaigns: '/api/google-ads/campaigns',
  adGroups: '/api/google-ads/ad-groups',
  ads: '/api/google-ads/ads',
  performance: '/api/google-ads/performance',
  keywords: '/api/google-ads/keywords'
}; 