import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "InventAI – Autonomous Engineering Platform",
  description: "From idea to Patent, 3D CAD and Physics Simulation in minutes. Powered by 6 AI agents.",
  keywords: "AI engineering, CAD generation, patent analysis, physics simulation, invention tool",
};

import Providers from "../providers/query-provider";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ margin: 0, padding: 0, fontFamily: 'Inter, -apple-system, sans-serif', background: '#F8FAFC' }}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
