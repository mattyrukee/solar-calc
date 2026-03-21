import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Corner Analytics — Football Corner Kick Predictions",
  description:
    "AI-powered corner kick predictions for Premier League, La Liga, Bundesliga, and Serie A.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        {/* Navbar */}
        <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
          <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-brand-600 text-xl font-black tracking-tight">
                CornerIQ
              </span>
              <span className="hidden sm:inline text-xs text-gray-400 font-medium bg-gray-100 px-2 py-0.5 rounded-full">
                Beta
              </span>
            </Link>

            <nav className="flex items-center gap-6 text-sm font-medium text-gray-500">
              <Link href="/" className="hover:text-gray-900 transition-colors">
                Fixtures
              </Link>
              <Link href="/leagues" className="hover:text-gray-900 transition-colors">
                Leagues
              </Link>
            </nav>
          </div>
        </header>

        {/* Page content */}
        <main className="max-w-5xl mx-auto px-4 py-8">{children}</main>

        {/* Footer */}
        <footer className="border-t border-gray-100 mt-16 py-8 text-center text-xs text-gray-400">
          <p>CornerIQ · Predictions powered by XGBoost · Data: StatsBomb Open Data + API-Football</p>
          <p className="mt-1">For informational purposes only. Not financial advice.</p>
        </footer>
      </body>
    </html>
  );
}
