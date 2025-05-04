const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  trailingSlash: true,
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      }
    ],
  },
  // Disable experimental features
  experimental: {
    // Avoiding all experimental features
  },
  // Production optimizations
  swcMinify: true,
  poweredByHeader: false
};

module.exports = nextConfig;