/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  images: {
    unoptimized: true,
    domains: ['api.dicebear.com', 'avatar.vercel.sh'],
  },
  distDir: '.next',
}

module.exports = nextConfig 