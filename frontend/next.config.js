/** @type {import('next').NextConfig} */

// Determine if we're in development mode
const isDev = process.env.NODE_ENV === 'development';

const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: !isDev, // Only unoptimize in production
    domains: ['api.dicebear.com', 'avatar.vercel.sh'],
  },
  // Only use static export in production, not in development
  ...(isDev ? {} : { output: 'export' }),
  // Only set custom output directory in production
  ...(isDev ? {} : { distDir: 'out' }),
  // Enable trailing slashes for Firebase hosting
  trailingSlash: true,
  // Use relative paths if not in production
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : undefined,
  // Other experimental features
  experimental: {
    scrollRestoration: true,
  },
};

module.exports = nextConfig;