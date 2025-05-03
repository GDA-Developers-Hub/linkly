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
    domains: ['api.dicebear.com', 'avatar.vercel.sh'],
  },
  distDir: '.next',
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : undefined,
  webpack: (config) => {
    return config;
  },
}

export default nextConfig
