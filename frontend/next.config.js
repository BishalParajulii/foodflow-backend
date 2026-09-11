/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Required for the production Docker image (`frontend/Dockerfile`
  // copies `.next/standalone`). `npm run dev` / `npm run build` are unaffected.
  output: "standalone",
  images: {
    domains: [], // we serve images from /public
  },
};

module.exports = nextConfig;