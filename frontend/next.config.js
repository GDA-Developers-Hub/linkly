/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
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

module.exports = nextConfig 