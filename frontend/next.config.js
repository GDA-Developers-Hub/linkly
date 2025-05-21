/** @type {import('next').NextConfig} */

const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    domains: ['api.dicebear.com', 'avatar.vercel.sh'],
    unoptimized: true,
  },
  experimental: {
    scrollRestoration: true,
  },
  output: 'export',
};

module.exports = nextConfig;
