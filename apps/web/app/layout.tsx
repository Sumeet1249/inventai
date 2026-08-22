import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

const googleSans = {
  style: {
    fontFamily: '"Google Sans", sans-serif',
    fontOpticalSizing: "auto",
    fontVariationSettings: '"GRAD" 0',
  }
};

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
        <style>
          {`@import url('https://fonts.googleapis.com/css2?family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&family=Instrument+Serif:ital@0;1&display=swap');`}
        </style>
        <style>
          {`.google-sans-body {
  font-family: "Google Sans", sans-serif;
  font-optical-sizing: auto;
  font-weight: 400;
  font-style: normal;
  font-variation-settings: "GRAD" 0;
}

.google-sans-heading {
  font-family: "Google Sans", sans-serif;
  font-optical-sizing: auto;
  font-weight: 700;
  font-style: normal;
  font-variation-settings: "GRAD" 0;
}

.instrument-serif-regular {
  font-family: "Instrument Serif", serif;
  font-weight: 400;
  font-style: normal;
}

.instrument-serif-regular-italic {
  font-family: "Instrument Serif", serif;
  font-weight: 400;
  font-style: italic;
}`}
        </style>
      </head>
      <body style={{ margin: 0, padding: 0, fontFamily: '"Google Sans"', background: '#F8FAFC' }}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
