"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-zinc-950 to-black text-gray-200 font-sans selection:bg-blue-500/30 flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl w-full space-y-12">
        
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 pb-2">
            Competitive Intelligence
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Automated intelligence gathering, extraction, and strategic synthesis for the UK Pallet Network industry.
          </p>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Network Intelligence Card */}
          <Link href="/network" className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur opacity-25 group-hover:opacity-60 transition duration-500"></div>
            <div className="relative h-full bg-black/50 backdrop-blur-xl border border-white/10 p-8 rounded-2xl hover:border-blue-500/50 transition-all duration-300 flex flex-col items-center text-center gap-4 shadow-2xl">
              <div className="p-4 bg-blue-500/10 rounded-full text-blue-400 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white">Network Intelligence</h2>
              <p className="text-gray-400 text-sm">
                Tactical event extraction covering footprint, hubs, capacity, and partnerships across Europe.
              </p>
              <div className="mt-auto pt-4 flex items-center text-blue-400 text-sm font-semibold group-hover:text-blue-300">
                View Dashboard <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>

          {/* Strategy Intelligence Card */}
          <Link href="/strategy" className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-amber-600 rounded-2xl blur opacity-25 group-hover:opacity-60 transition duration-500"></div>
            <div className="relative h-full bg-black/50 backdrop-blur-xl border border-white/10 p-8 rounded-2xl hover:border-orange-500/50 transition-all duration-300 flex flex-col items-center text-center gap-4 shadow-2xl">
              <div className="p-4 bg-orange-500/10 rounded-full text-orange-400 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white">Strategy Intelligence</h2>
              <p className="text-gray-400 text-sm">
                High-level AI synthesis interpreting strategic direction, capabilities, and market positioning.
              </p>
              <div className="mt-auto pt-4 flex items-center text-orange-400 text-sm font-semibold group-hover:text-orange-300">
                View Dashboard <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          </Link>

        </div>
      </div>
    </div>
  );
}
