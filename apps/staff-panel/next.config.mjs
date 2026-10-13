/** @type {import('next').NextConfig} */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig = {
  basePath,
  assetPrefix: basePath || undefined,
  typedRoutes: true,
};

export default nextConfig;
