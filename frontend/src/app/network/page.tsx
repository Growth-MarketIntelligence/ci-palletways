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
  citations?: string[];
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
  const [expandedSignalId, setExpandedSignalId] = useState<string | null>(null);
  const [selectedSummary, setSelectedSummary] = useState<{competitor: string, type: string} | null>(null);

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
    <div className="min-h-screen bg-gray-50 bg-gradient-to-b from-gray-50 via-gray-100 to-white text-gray-800 font-sans selection:bg-blue-200">
      <main className="p-8 max-w-[1600px] mx-auto space-y-8">
        
        {/* Header Section (Full Width) */}
        <header className="flex flex-col md:flex-row justify-between items-center bg-white/80 border border-gray-200 p-5 rounded-2xl shadow-lg sticky top-4 z-50 backdrop-blur-xl">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">
              2. Network Expansion
            </h1>
          </div>
          
          <nav className="hidden lg:flex gap-6 items-center bg-gray-50 px-6 py-2 rounded-full border border-gray-200">
            <a href="#dashboard" className="text-gray-600 hover:text-blue-600 text-sm font-semibold transition-colors">Dashboard</a>
            <a href="#signals" className="text-gray-600 hover:text-blue-600 text-sm font-semibold transition-colors">Signals</a>
            <a href="#summary" className="text-gray-600 hover:text-blue-600 text-sm font-semibold transition-colors">Summary</a>
            <a href="#news" className="text-gray-600 hover:text-blue-600 text-sm font-semibold transition-colors">News</a>
          </nav>

          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-md px-3 py-1.5 shadow-sm">
              <span className="text-sm text-gray-500">Time Filter:</span>
              <select 
                value={startDate === "" ? "null" : [7, 30, 90].find(d => startDate.includes(new Date(new Date().setDate(new Date().getDate() - d)).toISOString().split('T')[0]))?.toString() || "null"}
                onChange={(e) => setFilter(e.target.value === "null" ? null : parseInt(e.target.value))}
                className="bg-transparent text-gray-900 text-sm outline-none cursor-pointer font-medium"
              >
                <option value="7">Last 7 Days</option>
                <option value="30">Last 30 Days</option>
                <option value="90">Last 90 Days</option>
                <option value="null">All Time</option>
              </select>
            </div>
            <Link 
              href="/" 
              className="px-5 py-2 rounded-md bg-white hover:bg-gray-50 border border-gray-200 transition-all text-sm font-medium flex items-center gap-2 text-gray-700 shadow-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
              Back to Home
            </Link>
          </div>
        </header>

        {/* Main Layout Stack */}
        <div className="flex flex-col gap-8 mt-4">
          
          {/* Dashboard (Full Width) */}
          <div id="dashboard" className="flex flex-col gap-4 scroll-mt-32">
             <div className="w-full min-h-[350px] bg-white border border-gray-200 shadow-sm rounded-xl flex flex-col items-center justify-center p-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-50 to-transparent"></div>
                <h2 className="text-4xl font-bold text-gray-300 mb-4 tracking-widest uppercase z-10">Dashboard</h2>
                <p className="text-gray-500 text-center max-w-md z-10 text-sm">
                  KPI Monitoring & Statistical Visualization Area.<br/>
                  (Geomapping explicitly disabled per requirements).
                </p>
             </div>
             {/* Action buttons */}
             <div className="flex gap-4">
               <button className="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-medium py-3 px-4 rounded-md transition-colors shadow-lg">
                 Comparison X vs Y
               </button>
               <button className="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-medium py-3 px-4 rounded-md transition-colors shadow-lg">
                 Feature 2
               </button>
             </div>
          </div>

          {/* Signals (Full Width) */}
          <section id="signals" className="bg-white border border-gray-200 rounded-xl p-5 shadow-lg flex flex-col max-h-[600px] scroll-mt-32">
            <div className="flex justify-between items-center mb-4 border-b border-gray-100 pb-2">
              <h2 className="text-xl font-bold text-gray-900">Signals</h2>
              <div className="flex gap-2">
                <button className="bg-orange-600 hover:bg-orange-500 text-white font-medium py-1.5 px-3 rounded-md transition-colors text-xs shadow-sm">Download PDF</button>
                <button className="bg-orange-600 hover:bg-orange-500 text-white font-medium py-1.5 px-3 rounded-md transition-colors text-xs shadow-sm">Ask AI</button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2" style={{ maskImage: 'linear-gradient(to bottom, black 90%, transparent 100%)', WebkitMaskImage: 'linear-gradient(to bottom, black 90%, transparent 100%)', paddingBottom: '2rem' }}>
              {signals.length === 0 ? (
                <div className="text-sm text-gray-500 italic text-center mt-10">No signals detected.</div>
              ) : (
                <div className="columns-1 md:columns-2 lg:columns-3 xl:columns-4 gap-4 space-y-4">
                  {signals.map(s => {
                    const isExpanded = expandedSignalId === s.id;
                    return (
                      <div 
                        key={s.id} 
                        onClick={() => setExpandedSignalId(isExpanded ? null : s.id)}
                        className={`text-sm text-gray-700 flex flex-col items-start bg-gray-50 border border-gray-100 p-3 rounded-lg cursor-pointer transition-all hover:bg-white break-inside-avoid ${isExpanded ? 'ring-1 ring-blue-400 shadow-md' : 'shadow-sm'}`}
                      >
                        <div className="flex items-start justify-between w-full">
                          <div className="flex items-start">
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 mr-2 shrink-0"></span>
                            <span className="leading-tight font-semibold text-gray-900">{s.title}</span>
                          </div>
                          <svg className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                        </div>
                        <span className={`mt-2 text-gray-600 pl-3 border-l-2 border-orange-200 ${isExpanded ? '' : 'line-clamp-2'}`}>{s.summary}</span>
                        
                        {s.citations && s.citations.length > 0 && (
                          <div className="mt-3 w-full pl-3">
                            <div className="text-xs font-semibold text-blue-600 mb-1 flex items-center gap-1">
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                              Source Citations ({s.citations.length})
                            </div>
                            <div className="flex flex-col gap-1">
                              {(isExpanded ? s.citations : s.citations.slice(0, 3)).map((url, i) => (
                                <a key={i} href={url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:text-blue-700 hover:underline truncate max-w-full inline-block" onClick={(e) => e.stopPropagation()}>
                                  {url}
                                </a>
                              ))}
                              {!isExpanded && s.citations.length > 3 && (
                                <span className="text-xs text-gray-400 italic">...and {s.citations.length - 3} more sources</span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </section>

          {/* Competitor Summary (Full Width) */}
          <section id="summary" className="bg-white border border-gray-200 rounded-xl p-5 shadow-lg flex flex-col max-h-[600px] scroll-mt-32">
            <h2 className="text-xl font-bold text-gray-900 mb-4 border-b border-gray-100 pb-2">Competitor Summary</h2>
            {Object.keys(summary).length === 0 ? (
              <div className="flex h-32 items-center justify-center text-gray-500 italic text-sm text-center">
                {!status ? "Loading..." : (!status.has_run ? "No intelligence collected yet." : "No actionable network changes detected.")}
              </div>
            ) : (
              <div className="overflow-y-auto custom-scrollbar pr-2 flex-1 relative" style={{ maskImage: 'linear-gradient(to bottom, black 90%, transparent 100%)', WebkitMaskImage: 'linear-gradient(to bottom, black 90%, transparent 100%)', paddingBottom: '2rem' }}>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                  {Object.entries(summary).map(([comp, types]) => (
                    <div key={comp} className="bg-gray-50 p-4 rounded-lg border border-gray-200 shadow-sm">
                      <h3 className="font-semibold text-gray-900 mb-3 text-lg border-b border-gray-200 pb-2">{comp}</h3>
                      <ul className="space-y-1">
                        {Object.entries(types).map(([type, count]) => (
                          <li 
                            key={type} 
                            className="flex justify-between items-center text-sm text-gray-700 cursor-pointer hover:bg-gray-200/50 p-1.5 -mx-1.5 rounded transition-colors group"
                            onClick={() => setSelectedSummary({ competitor: comp, type })}
                          >
                            <span className="flex items-center group-hover:text-blue-700 transition-colors">
                              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-2 group-hover:scale-125 transition-transform"></span>
                              {type.replace(/_/g, ' ')}
                            </span>
                            <strong className="text-gray-900 bg-gray-200 px-2 py-0.5 rounded-md group-hover:bg-blue-100 group-hover:text-blue-800 transition-colors">{count}</strong>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </div>

        {/* BOTTOM: Expandable News Section */}
        <section id="news" className="pt-4 scroll-mt-32">
           <button 
             onClick={() => setIsNewsExpanded(!isNewsExpanded)} 
             className="w-full bg-white hover:bg-gray-50 border border-gray-200 rounded-xl p-5 flex justify-between items-center transition-all shadow-lg group"
           >
             <span className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
               News (Intelligence Feed)
             </span>
             <div className={`p-2 rounded-full bg-gray-100 group-hover:bg-blue-100 transition-all ${isNewsExpanded ? 'rotate-180' : ''}`}>
               <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
             </div>
           </button>
           
           {isNewsExpanded && (
             <div className="mt-4 bg-white border border-gray-200 rounded-2xl shadow-xl overflow-hidden animate-in slide-in-from-top-2 fade-in duration-200">
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                   <thead>
                     <tr className="bg-gray-50 text-gray-600 text-sm uppercase tracking-wider border-b border-gray-200">
                       <th className="p-4 font-medium">Timeline</th>
                       <th className="p-4 font-medium">Target</th>
                       <th className="p-4 font-medium">Vector</th>
                       <th className="p-4 font-medium">Analysis</th>
                       <th className="p-4 font-medium text-right">Source</th>
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
                       <tr key={e.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                         <td className="p-4 align-top whitespace-nowrap">
                           <span className="block font-medium text-gray-900">
                             {e.event_date || (e.source_updated_at ? e.source_updated_at.split('T')[0] : 'Unknown')}
                           </span>
                           <span className="text-xs text-gray-500">
                             {e.event_date ? 'Event Date' : 'Discovered'}
                           </span>
                         </td>
                         <td className="p-4 align-top font-semibold text-gray-900">{e.competitor_name}</td>
                         <td className="p-4 align-top">
                           <span className="inline-block px-2.5 py-1 bg-emerald-100 text-emerald-700 border border-emerald-200 text-xs font-bold rounded-md mb-2 shadow-sm">
                             {e.event_type}
                           </span>
                           {e.location && <div className="text-gray-600 flex items-start gap-1 mt-1">
                             <svg className="w-4 h-4 text-gray-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                             <span className="leading-tight">{e.location}</span>
                           </div>}
                         </td>
                         <td className="p-4 align-top max-w-md">
                           <p className="text-gray-700 leading-relaxed">{e.description}</p>
                           <div className="mt-3 text-xs text-gray-600 border-l-2 border-blue-400 pl-3 py-1 bg-gradient-to-r from-blue-50 to-transparent rounded-r-md italic">
                             "{e.evidence_excerpt}"
                           </div>
                         </td>
                         <td className="p-4 align-top text-right">
                           <a href={e.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-500 hover:underline transition-colors">
                             View Origin
                             <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                           </a>
                           <div className="text-xs text-gray-500 mt-2 font-mono">
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

        {/* Modal for Summary Click */}
        {selectedSummary && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm animate-in fade-in duration-200" onClick={() => setSelectedSummary(null)}>
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[80vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()}>
              <div className="flex justify-between items-center p-5 border-b border-gray-100 bg-gray-50">
                <h3 className="font-bold text-lg text-gray-900">
                  Citations: {selectedSummary.competitor} - {selectedSummary.type.replace(/_/g, ' ')}
                </h3>
                <button onClick={() => setSelectedSummary(null)} className="text-gray-500 hover:text-gray-700 bg-gray-200 hover:bg-gray-300 p-1.5 rounded-full transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
              </div>
              <div className="p-5 overflow-y-auto custom-scrollbar flex-1 bg-white">
                {events.filter(e => e.competitor_name === selectedSummary.competitor && e.event_type === selectedSummary.type).length === 0 ? (
                  <div className="text-center text-gray-500 italic py-8">No specific citations found for this category.</div>
                ) : (
                  <div className="flex flex-col gap-4">
                    {events.filter(e => e.competitor_name === selectedSummary.competitor && e.event_type === selectedSummary.type).map(e => (
                      <div key={e.id} className="border border-gray-100 rounded-xl p-4 bg-gray-50/50 hover:bg-gray-50 transition-colors">
                        <div className="flex justify-between items-start gap-4 mb-2">
                          <p className="text-sm text-gray-800 font-medium">{e.description}</p>
                          <span className="text-xs text-gray-500 whitespace-nowrap bg-white px-2 py-1 border border-gray-200 rounded shadow-sm">{e.event_date || (e.source_updated_at ? e.source_updated_at.split('T')[0] : 'Unknown')}</span>
                        </div>
                        {e.evidence_excerpt && (
                           <div className="text-xs text-gray-600 border-l-2 border-blue-400 pl-3 py-1 bg-gradient-to-r from-blue-50 to-transparent rounded-r-md italic mb-3">
                             "{e.evidence_excerpt}"
                           </div>
                        )}
                        <a href={e.source_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-semibold hover:underline">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                          View Original Source
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.03);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.15);
          border-radius: 4px;
        }
      `}} />
    </div>
  );
}
