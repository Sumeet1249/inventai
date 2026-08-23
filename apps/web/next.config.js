/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy /api/* → nginx backend using internal Docker network name.
  //
  // Two separate URLs:
  //   NEXT_PUBLIC_API_URL  = browser-facing  (http://localhost:8080/api/v1)
  //   BACKEND_URL          = server-side SSR (http://nginx:80)  ← Docker network
  //
  // Next.js rewrites run server-side, so they MUST use the Docker service name,
  // not localhost (which inside the container points to the container itself).
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_URL ||          // Docker internal — preferred
      process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') ||
      'http://nginx:80';

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
