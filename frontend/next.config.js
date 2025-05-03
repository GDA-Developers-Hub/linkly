const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
<<<<<<< Updated upstream
  trailingSlash: true,
=======
>>>>>>> Stashed changes
  images: {
    domains: ['localhost'],
  },
  // Optimize build performance
  webpack: (config, { dev, isServer }) => {
    // Keep only one copy of React in development
    if (dev && !isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        'react': path.resolve('./node_modules/react'),
        'react-dom': path.resolve('./node_modules/react-dom'),
      };
    }
    return config;
  },
  // Performance optimizations
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
<<<<<<< Updated upstream
  distDir: '.next',
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : undefined,
  webpack: (config) => {
    return config;
  },
=======
  // Cache optimization
  onDemandEntries: {
    // period (in ms) where the server will keep pages in the buffer
    maxInactiveAge: 25 * 1000,
    // number of pages that should be kept simultaneously without being disposed
    pagesBufferLength: 2,
  }
>>>>>>> Stashed changes
}

module.exports = nextConfig 