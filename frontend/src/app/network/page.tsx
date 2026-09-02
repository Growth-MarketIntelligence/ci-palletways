"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

type Event = {
  id: string;
  competitor_name: string;
  event_type: string;
  description: string;
  location: string | null;
  event_date: string | null;
  evidence_excerpt: string;
  confidence: number;
  source_url: string;
  source_published_at: string | null;
  source_updated_at: string | null;
  collected_at: string;
};

type Signal = {
  id: string;
  title: string;
  summary: string;
  competitor_name: string;
  generated_at: string;
  event_count: number;
};

type Summary = Record<string, Record<string, number>>;

type Status = {
  total_collection_runs: number;
  failed_collection_runs: number;
  total_documents: number;
  has_run: boolean;
};

export default function NetworkPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [summary, setSummary] = useState<Summary>({});
  const [status, setStatus] = useState<Status | null>(null);
  
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [isNewsExpanded, setIsNewsExpanded] = useState<boolean>(false);

  useEffect(() => {
    fetchData();
  }, [startDate, endDate]);

  const fetchData = async () => {
    try {
      let query = "";
      if (startDate) query += `?start_date=${startDate}`;
      if (endDate) query += (query ? "&" : "?") + `end_date=${endDate}`;
      
      const [eventsRes, signalsRes, summaryRes, statusRes] = await Promise.all([
        fetch(`http://localhost:8000/network/events${query}`),
        fetch(`http://localhost:8000/network/signals`),
        fetch(`http://localhost:8000/network/summary${query}`),
        fetch(`http://localhost:8000/network/status`)
      ]);

      if (eventsRes.ok) setEvents(await eventsRes.json());
      if (signalsRes.ok) setSignals(await signalsRes.json());
      if (summaryRes.ok) setSummary(await summaryRes.json());
      if (statusRes.ok) setStatus(await statusRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  const setFilter = (days: number | null) => {
    if (days === null) {
      setStartDate("");
      setEndDate("");
      return;
    }
    const d = new Date();
    d.setDate(d.getDate() - days);
    setStartDate(d.toISOString().split("T")[0]);
    setEndDate("");
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-zinc-950 to-black text-gray-200 font-sans selection:bg-blue-500/30">
      <main className="p-8 max-w-[1600px] mx-auto space-y-8">
        
        {/* Header Section (Full Width) */}
        <header className="flex flex-col md:flex-row justify-between items-center bg-blue-900/30 border border-blue-500/20 p-5 rounded-2xl shadow-lg">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">
              2. Network Expansion
            </h1>
          </div>
          <Link 
            href="/" 
            className="px-5 py-2 rounded-md bg-white/5 hover:bg-white/10 border border-white/10 transition-all text-sm font-medium flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Back to Home
          </Link>
        </header>

        {/* Main Layout Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* LEFT SIDEBAR (Span 3 or 4) */}
          <div className="lg:col-span-3 flex flex-col gap-6">
            
            {/* Filters (Vertical) */}
            <section className="bg-blue-900/20 border border-blue-500/20 rounded-xl p-5 shadow-lg">
              <h2 className="text-lg font-semibold text-white mb-4 border-b border-white/10 pb-2">Time (update filters)</h2>
              <div className="flex flex-col gap-2">
                {[
                  { label: 'Last 7 Days', val: 7 },
                  { label: 'Last 30 Days', val: 30 },
                  { label: 'Last 90 Days', val: 90 },
                  { label: 'All Time', val: null }
                ].map((btn) => {
                  const isActive = btn.val === null ? startDate === "" : startDate.includes(new Date(new Date().setDate(new Date().getDate() - (btn.val as number))).toISOString().split('T')[0]);
                  return (
                    <button 
                      key={btn.label}
                      onClick={() => setFilter(btn.val)} 
                      className={`px-4 py-2 text-left rounded-md text-sm font-medium transition-all ${
                        isActive 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                      }`}
                    >
                      {btn.label}
                    </button>
                  )
                })}
              </div>
            </section>

            {/* Competitor Summary */}
            <section className="bg-blue-900/20 border border-blue-500/20 rounded-xl p-5 shadow-lg flex-1">
              {Object.keys(summary).length === 0 ? (
                <div className="flex h-32 items-center justify-center text-gray-500 italic text-sm text-center">
                  {!status ? "Loading..." : (!status.has_run ? "No intelligence collected yet." : "No actionable network changes detected.")}
                </div>
              ) : (
                <div className="space-y-5">
                  {Object.entries(summary).map(([comp, types]) => (
                    <div key={comp} className="border-b border-white/5 pb-3 last:border-0 last:pb-0">
                      <h3 className="font-semibold text-white mb-2">{comp} summary</h3>
                      <ul className="space-y-1">
                        {Object.entries(types).map(([type, count]) => (
                          <li key={type} className="flex items-center text-sm text-gray-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mr-2"></span>
                            {type} — <strong className="ml-1 text-white">{count} News</strong>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </section>

          </div>

          {/* MIDDLE COLUMN: Signals (Span 3) */}
          <div className="lg:col-span-3 flex flex-col gap-6">
            <section className="bg-blue-900/20 border border-blue-500/20 rounded-xl p-5 shadow-lg flex-1 flex flex-col">
              <h2 className="text-xl font-bold text-white mb-4 border-b border-white/10 pb-2 text-center">Signal</h2>
              
              <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 mb-4 space-y-3 max-h-[400px]">
                {signals.length === 0 ? (
                  <div className="text-sm text-gray-500 italic text-center mt-10">No signals detected.</div>
                ) : (
                  signals.map(s => (
                    <div key={s.id} className="text-sm text-gray-300 flex items-start">
                      <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 mr-2 shrink-0"></span>
                      <span className="leading-tight">{s.title} ({s.competitor_name})</span>
                    </div>
                  ))
                )}
              </div>

              {/* Action Buttons (Placeholders) */}
              <div className="flex flex-col gap-2 mt-auto pt-4 border-t border-white/10">
                <button className="w-full bg-orange-600 hover:bg-orange-500 text-white font-medium py-2 px-4 rounded-md transition-colors text-sm shadow-lg">
                  Download PDF
                </button>
                <button className="w-full bg-orange-600 hover:bg-orange-500 text-white font-medium py-2 px-4 rounded-md transition-colors text-sm shadow-lg">
                  Ask AI
                </button>
                <button className="w-full bg-orange-600 hover:bg-orange-500 text-white font-medium py-2 px-4 rounded-md transition-colors text-sm shadow-lg">
                  Feature X?
                </button>
              </div>
            </section>
          </div>

          {/* RIGHT COLUMN: Dashboard (Span 6) */}
          <div className="lg:col-span-6 flex flex-col gap-4">
             {/* Huge Dashboard Placeholder */}
             <div className="flex-1 min-h-[500px] bg-blue-900/10 border-2 border-dashed border-blue-500/30 rounded-xl flex flex-col items-center justify-center p-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-500/5 to-transparent"></div>
                <h2 className="text-4xl font-bold text-blue-300/50 mb-4 tracking-widest uppercase z-10">Dashboard</h2>
                <p className="text-blue-200/40 text-center max-w-md z-10 text-sm">
                  KPI Monitoring & Statistical Visualization Area.<br/>
                  (Geomapping explicitly disabled per requirements).
                </p>
             </div>
             
             {/* Bottom right action buttons */}
             <div className="flex gap-4">
               <button className="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-medium py-3 px-4 rounded-md transition-colors shadow-lg">
                 Comparison X vs Y
               </button>
               <button className="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-medium py-3 px-4 rounded-md transition-colors shadow-lg">
                 Feature 2
               </button>
             </div>
          </div>
        </div>

        {/* BOTTOM: Expandable News Section */}
        <section className="pt-4">
           <button 
             onClick={() => setIsNewsExpanded(!isNewsExpanded)} 
             className="w-full bg-blue-900/40 hover:bg-blue-800/40 border border-blue-500/30 rounded-xl p-5 flex justify-between items-center transition-all shadow-lg group"
           >
             <span className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors">
               News (Intelligence Feed)
             </span>
             <div className={`p-2 rounded-full bg-white/5 group-hover:bg-blue-500/20 transition-all ${isNewsExpanded ? 'rotate-180' : ''}`}>
               <svg className="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
             </div>
           </button>
           
           {isNewsExpanded && (
             <div className="mt-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden animate-in slide-in-from-top-2 fade-in duration-200">
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                   <thead>
                     <tr className="bg-black/40 text-gray-400 text-sm uppercase tracking-wider">
                       <th className="p-4 font-medium border-b border-white/10">Timeline</th>
                       <th className="p-4 font-medium border-b border-white/10">Target</th>
                       <th className="p-4 font-medium border-b border-white/10">Vector</th>
                       <th className="p-4 font-medium border-b border-white/10">Analysis</th>
                       <th className="p-4 font-medium border-b border-white/10 text-right">Source</th>
                     </tr>
                   </thead>
                   <tbody className="text-sm">
                     {events.length === 0 && (
                       <tr>
                         <td colSpan={5} className="p-8 text-center text-gray-500 italic">
                           {!status ? "Loading..." : (!status.has_run ? "No intelligence collected yet." : "No actionable network changes detected in this period.")}
                         </td>
                       </tr>
                     )}
                     {events.map(e => (
                       <tr key={e.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                         <td className="p-4 align-top whitespace-nowrap">
                           <span className="block font-medium text-gray-200">
                             {e.event_date || (e.source_updated_at ? e.source_updated_at.split('T')[0] : 'Unknown')}
                           </span>
                           <span className="text-xs text-gray-500">
                             {e.event_date ? 'Event Date' : 'Discovered'}
                           </span>
                         </td>
                         <td className="p-4 align-top font-semibold text-white">{e.competitor_name}</td>
                         <td className="p-4 align-top">
                           <span className="inline-block px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold rounded-md mb-2 shadow-sm">
                             {e.event_type}
                           </span>
                           {e.location && <div className="text-gray-400 flex items-start gap-1 mt-1">
                             <svg className="w-4 h-4 text-gray-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                             <span className="leading-tight">{e.location}</span>
                           </div>}
                         </td>
                         <td className="p-4 align-top max-w-md">
                           <p className="text-gray-300 leading-relaxed">{e.description}</p>
                           <div className="mt-3 text-xs text-gray-400 border-l-2 border-blue-500/50 pl-3 py-1 bg-gradient-to-r from-blue-500/5 to-transparent rounded-r-md italic">
                             "{e.evidence_excerpt}"
                           </div>
                         </td>
                         <td className="p-4 align-top text-right">
                           <a href={e.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 hover:underline transition-colors">
                             View Origin
                             <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                           </a>
                           <div className="text-xs text-gray-600 mt-2 font-mono">
                             {new Date(e.collected_at).toLocaleDateString()}
                           </div>
                         </td>
                       </tr>
                     ))}
                   </tbody>
                 </table>
               </div>
             </div>
           )}
        </section>
      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.02);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
        }
      `}} />
    </div>
  );
}
