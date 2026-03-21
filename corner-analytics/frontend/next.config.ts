import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    domains: ["media.api-sports.io"],
  },
};

export default nextConfig;
