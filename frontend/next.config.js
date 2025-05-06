/** @type {import('next').NextConfig} */
module.exports = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
    domains: ['api.dicebear.com', 'avatar.vercel.sh'],
  },
  // Set output to 'export' for static site generation
  output: 'export',
  // Set the output directory to be 'out' for Firebase hosting
  distDir: 'out',
  // Enable trailing slashes for Firebase hosting
  trailingSlash: true,
  // Use relative paths if not in production
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : undefined,
  // Other experimental features
  experimental: {
    scrollRestoration: true,
  },
}