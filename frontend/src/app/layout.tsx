import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Activity } from "lucide-react";
import ErrorBoundary from "@/components/ErrorBoundary";
import { Sidebar } from "@/components/Sidebar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LLM Monitor — Cost & Latency",
  description:
    "Self-hosted LLM observability dashboard: token usage, cost, latency percentiles, error rates, daily reports, and budget alerts.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}
      >
        <header className="sticky top-0 z-10 border-b border-gray-200 bg-white">
          <div className="flex items-center justify-between px-6 py-3">
            <a href="/" className="flex items-center gap-2">
              <span className="rounded-lg bg-brand-600 p-1.5 text-white">
                <Activity className="h-5 w-5" />
              </span>
              <span className="text-lg font-bold text-gray-900">
                LLM&nbsp;Monitor
              </span>
            </a>
            <span className="hidden text-xs text-gray-400 sm:block">
              Cost &amp; latency observability
            </span>
          </div>
        </header>
        <div className="flex flex-col md:flex-row">
          <Sidebar />
          <main className="min-w-0 flex-1 px-6 py-8">
            <div className="mx-auto max-w-6xl">
              <ErrorBoundary>{children}</ErrorBoundary>
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
