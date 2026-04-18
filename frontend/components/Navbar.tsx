"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { useState } from "react";

const links = [
  { href: "/", label: "Overview" },
  { href: "/by-service", label: "Par service" },
  { href: "/by-tag", label: "Par equipe" },
  { href: "/anomalies", label: "Anomalies" },
  { href: "/recommendations", label: "Recommandations" },
];

export default function Navbar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [open, setOpen] = useState(false);

  // Préserve le paramètre ?month= entre les pages
  const month = searchParams.get("month");
  const buildHref = (href: string) => (month ? `${href}?month=${month}` : href);

  return (
    <nav className="bg-white border-b border-[#E0E7FF]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link
            href={buildHref("/")}
            onClick={() => setOpen(false)}
            className="flex items-center gap-2 cursor-pointer"
          >
            <div className="w-8 h-8 rounded-lg bg-[#6366F1] flex items-center justify-center">
              <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
            </div>
            <span className="text-base sm:text-lg font-bold text-[#1E1B4B]">CloudCostPilot</span>
          </Link>

          {/* Menu desktop */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((link) => (
              <Link
                key={link.href}
                href={buildHref(link.href)}
                className={`text-sm px-3 py-2 rounded-lg cursor-pointer transition-colors duration-150 ${
                  pathname === link.href
                    ? "bg-[#6366F1] text-white font-semibold"
                    : "text-[#475569] hover:bg-[#F5F3FF]"
                }`}
              >
                {link.label}
              </Link>
            ))}
            <div className="mx-2 w-px h-5 bg-[#E0E7FF]" aria-hidden="true" />
            <a
              href="https://github.com/Sparctuce-X-X/CloudCostPilot"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub du projet"
              className="p-2 rounded-lg text-[#475569] hover:bg-[#F5F3FF] hover:text-[#1E1B4B] cursor-pointer transition-colors duration-150"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.21.09 1.84 1.24 1.84 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.17 0 0 1.01-.32 3.31 1.23a11.5 11.5 0 016 0c2.3-1.55 3.31-1.23 3.31-1.23.66 1.65.24 2.87.12 3.17.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.62-5.49 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.22.69.83.58C20.56 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z" />
              </svg>
            </a>
          </div>

          {/* Bouton hamburger mobile */}
          <button
            onClick={() => setOpen(!open)}
            aria-label="Toggle menu"
            aria-expanded={open}
            className="md:hidden p-2 rounded-lg hover:bg-[#F5F3FF] cursor-pointer transition-colors duration-150"
          >
            <svg className="w-6 h-6 text-[#1E1B4B]" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
              {open ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Menu mobile déroulant */}
        {open && (
          <div className="md:hidden pb-4 flex flex-col gap-1 border-t border-[#E0E7FF] pt-3">
            {links.map((link) => (
              <Link
                key={link.href}
                href={buildHref(link.href)}
                onClick={() => setOpen(false)}
                className={`text-sm px-3 py-2.5 rounded-lg cursor-pointer transition-colors duration-150 ${
                  pathname === link.href
                    ? "bg-[#6366F1] text-white font-semibold"
                    : "text-[#475569] hover:bg-[#F5F3FF]"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
