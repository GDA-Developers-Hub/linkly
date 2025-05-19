/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
    domains: ['api.dicebear.com', 'avatar.vercel.sh', 'linkly-production.up.railway.app'],
  },
  // Settings for static export that Firebase hosting requires
  output: 'export',
  // Set the output directory to 'out' for Firebase hosting
  distDir: 'out',
  trailingSlash: true,
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : undefined,
  // Set pages that use localStorage to execute only on client-side
  experimental: {
    optimizeFonts: true,
    scrollRestoration: true,
  },
  env: {
    // Define API URL for both development and production
    API_URL: process.env.API_URL,
  },
  // Make API URL available as a public environment variable
  publicRuntimeConfig: {
    API_URL: process.env.API_URL
  },
}

export default nextConfig
