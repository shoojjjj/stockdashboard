import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stock Managment — 투자 대시보드",
  description: "아카이브 기반 주식 투자 관제탑",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="antialiased min-h-screen">{children}</body>
    </html>
  );
}
