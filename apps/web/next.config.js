/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy /api/* → backend nginx so GLTF files load from the same origin,
  // avoiding CORS issues and making the URL work both in browser and SSR.
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://nginx:80';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
