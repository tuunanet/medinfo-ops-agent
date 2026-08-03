// story: e01s01
import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";


export const metadata: Metadata = {
  description: "Synthetic medical-information workflow demonstration",
  title: "medinfo-ops-agent",
};

type RootLayoutProps = Readonly<{
  children: ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
