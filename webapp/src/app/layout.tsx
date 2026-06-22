import "./globals.css";
import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { IBM_Plex_Sans_Arabic } from "next/font/google";

// Arabic UI/content face — metrically paired intent with Geist; loaded for the
// bilingual content the console renders RTL. Real weights only (no faux-bold).
const arabic = IBM_Plex_Sans_Arabic({
  subsets: ["arabic"],
  weight: ["400", "500", "600"],
  variable: "--font-arabic",
  display: "swap",
});

export const metadata: Metadata = {
  title: "MAS Console",
  description: "Operator console — digital growth for Gulf travel agencies.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable} ${arabic.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
