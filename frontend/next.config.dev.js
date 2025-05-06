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
  },
  experimental: {
    scrollRestoration: true,
  },
};

module.exports = nextConfig;
