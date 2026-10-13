import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Golden Bite Loyalty",
    short_name: "Golden Bite",
    description: "Golden Bite loyalty card and member dashboard.",
    start_url: "/",
    display: "standalone",
    background_color: "#f6efe4",
    theme_color: "#b35a2b",
    icons: [
      {
        src: "/icon-192.png",
        sizes: "192x192",
        type: "image/png",
      },
      {
        src: "/icon-512.png",
        sizes: "512x512",
        type: "image/png",
      },
    ],
  };
}
