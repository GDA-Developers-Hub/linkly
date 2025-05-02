/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  output: 'export',
  images: {
    unoptimized: true,
    domains: ['api.dicebear.com', 'avatar.vercel.sh'],
  },
}

module.exports = nextConfig 