import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MAS Digital Revamped",
  description: "Operator console (foundation build)",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
