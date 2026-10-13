import { ImageResponse } from "next/og";

export const size = {
  width: 512,
  height: 512,
};

export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #1f140d 0%, #5a2b13 45%, #b35a2b 100%)",
          color: "white",
          fontSize: 120,
          fontWeight: 700,
        }}
      >
        GB
      </div>
    ),
    size,
  );
}
