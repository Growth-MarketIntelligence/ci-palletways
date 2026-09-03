"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

type SupportingEvent = {
  id: string;
  url: string | null;
  source_name: string | null;
  description: string | null;
  event_type: string | null;
  event_subtype: string | null;
  location: string | null;
  event_date: string | null;
};

type StrategyInsight = {
  id: string;
  competitor_id: string;
  competitor_name: string;
  strategy_category: string;
  strategy_theme: string;
  assessment: string;
  interpretation: string;
  confidence: number;
  supporting_events: SupportingEvent[];
  generated_at: string;
};

export default function StrategyPage() {
  const [insights, setInsights] = useState<StrategyInsight[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCompetitor, setSelectedCompetitor] = useState<string>("All");

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://localhost:8000/strategy/insights`);
      if (res.ok) {
        const data = await res.json();
        setInsights(data);
      }
    } catch (e) {
      console.error("Failed to fetch strategy insights:", e);
    } finally {
      setLoading(false);
    }
  };

  const competitors = ["All", ...Array.from(new Set(insights.map(i => i.competitor_name)))];
  const filteredInsights = selectedCompetitor === "All" 
    ? insights 
    : insights.filter(i => i.competitor_name === selectedCompetitor);

  // Helper to map category to color theme
  const getCategoryTheme = (category: string) => {
    switch(category) {
      case "NETWORK_STRATEGY": return "from-blue-500 to-cyan-500 text-blue-700 bg-blue-50 border-blue-200";
      case "INFRASTRUCTURE_STRATEGY": return "from-orange-500 to-amber-500 text-orange-700 bg-orange-50 border-orange-200";
      case "COMMERCIAL_STRATEGY": return "from-emerald-500 to-green-500 text-emerald-700 bg-emerald-50 border-emerald-200";
      case "TECHNOLOGY_STRATEGY": return "from-purple-500 to-fuchsia-500 text-purple-700 bg-purple-50 border-purple-200";
      case "GEOGRAPHIC_MARKET_EXPANSION": return "from-pink-500 to-rose-500 text-pink-700 bg-pink-50 border-pink-200";
      case "COMPETITIVE_POSITIONING": return "from-red-500 to-rose-600 text-red-700 bg-red-50 border-red-200";
      case "OPERATIONAL_POSITIONING": return "from-indigo-500 to-blue-600 text-indigo-700 bg-indigo-50 border-indigo-200";
      default: return "from-gray-500 to-zinc-500 text-gray-700 bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 bg-gradient-to-b from-gray-50 via-gray-100 to-white text-gray-800 font-sans selection:bg-orange-200">
      <main className="p-8 max-w-[1600px] mx-auto space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-center bg-white border border-gray-200 p-5 rounded-2xl shadow-lg">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 flex items-center gap-3">
              <span className="p-2 bg-orange-100 rounded-lg text-orange-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              </span>
              Strategy & Market Positioning
            </h1>
          </div>
          <Link 
            href="/" 
            className="px-5 py-2 rounded-md bg-gray-50 hover:bg-gray-100 border border-gray-200 transition-all text-sm font-medium flex items-center gap-2 text-gray-700"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Back to Home
          </Link>
        </header>

        {/* Main Layout Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* LEFT SIDEBAR (Span 3) */}
          <div className="lg:col-span-3 flex flex-col gap-6">
            
            {/* Competitor Filter */}
            <section className="bg-white border border-gray-200 rounded-xl p-5 shadow-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 border-b border-gray-100 pb-2">Competitor Analysis</h2>
              <div className="flex flex-col gap-2">
                {competitors.map((comp) => (
                  <button 
                    key={comp}
                    onClick={() => setSelectedCompetitor(comp)} 
                    className={`px-4 py-2 text-left rounded-md text-sm font-medium transition-all ${
                      selectedCompetitor === comp 
                      ? 'bg-orange-600 text-white shadow-md' 
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    {comp}
                  </button>
                ))}
              </div>
            </section>

            {/* Context Box */}
            <section className="bg-orange-50 border border-orange-200 rounded-xl p-5 shadow-sm flex-1">
              <h3 className="font-semibold text-gray-900 mb-2">Phase 2 Intelligence Layer</h3>
              <p className="text-sm text-gray-600 leading-relaxed mb-4">
                This dashboard synthesizes strategic meaning from the raw events captured in the Network Intelligence layer.
              </p>
              <div className="p-3 bg-white rounded-lg border border-orange-100 text-xs text-gray-600">
                AI interprets the events to identify patterns such as structural expansion, commercial pivots, or capability shifts.
              </div>
            </section>

          </div>

          {/* MAIN COLUMN: Insights Feed (Span 9) */}
          <div className="lg:col-span-9 flex flex-col gap-6">
            
            {loading ? (
              <div className="flex h-64 items-center justify-center text-gray-500 text-lg">
                <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-orange-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Synthesizing Intelligence...
              </div>
            ) : filteredInsights.length === 0 ? (
              <div className="flex flex-col h-64 items-center justify-center text-gray-500 bg-white rounded-2xl border border-gray-200">
                <svg className="w-12 h-12 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <p>No strategic insights found for {selectedCompetitor}.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6">
                {filteredInsights.map(insight => {
                  const themeClasses = getCategoryTheme(insight.strategy_category);
                  const confidencePct = Math.round(insight.confidence * 100);
                  
                  return (
                    <div key={insight.id} className="bg-white border border-gray-200 rounded-2xl p-6 shadow-xl hover:border-gray-300 transition-all duration-300 group">
                      
                      {/* Card Header */}
                      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-6">
                        <div>
                          <div className="flex items-center gap-3 mb-2">
                            <h2 className="text-2xl font-bold text-gray-900">{insight.competitor_name}</h2>
                            <span className={`px-3 py-1 text-xs font-bold rounded-full border ${themeClasses}`}>
                              {insight.strategy_category.replace(/_/g, " ")}
                            </span>
                          </div>
                          <h3 className="text-lg text-gray-700 font-medium">
                            {insight.strategy_theme}
                          </h3>
                        </div>
                        
                        {/* Confidence Gauge */}
                        <div className="flex flex-col items-end shrink-0 bg-gray-50 p-3 rounded-xl border border-gray-200">
                          <span className="text-xs text-gray-500 uppercase tracking-wider mb-1 font-semibold">AI Confidence</span>
                          <div className="flex items-center gap-3">
                            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className={`h-full bg-gradient-to-r ${themeClasses.split(' ').find(c => c.startsWith('from-'))} ${themeClasses.split(' ').find(c => c.startsWith('to-'))}`} 
                                style={{ width: `${confidencePct}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-bold text-gray-900">{confidencePct}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Card Body (Assessment & Interpretation) */}
                      <div className="grid md:grid-cols-2 gap-6 bg-gray-50 p-5 rounded-xl border border-gray-200">
                        
                        {/* Assessment */}
                        <div>
                          <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
                            Factual Assessment
                          </h4>
                          <p className="text-gray-700 text-sm leading-relaxed">
                            {insight.assessment}
                          </p>
                        </div>

                        {/* Interpretation */}
                        <div className="relative">
                          <div className="absolute -left-3 top-0 bottom-0 w-px bg-gray-200 hidden md:block"></div>
                          <h4 className="text-xs font-bold text-orange-600 uppercase tracking-wider mb-2 flex items-center gap-2">
                            <svg className="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
                            Strategic Interpretation
                          </h4>
                          <p className="text-gray-900 font-medium text-sm leading-relaxed">
                            {insight.interpretation}
                          </p>
                        </div>
                      </div>

                      {/* Footer: Supporting Events count and Sources */}
                      <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-4">
                        <div className="flex flex-col gap-3 w-full">
                          <div className="flex items-center justify-between w-full mb-1">
                            <div className="text-xs text-gray-500 flex items-center gap-2">
                              <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                              Derived from <strong>{insight.supporting_events.length}</strong> validated strategy event{insight.supporting_events.length !== 1 ? 's' : ''}
                            </div>
                            <div className="text-xs font-mono text-gray-500">
                              {new Date(insight.generated_at || insight.created_at || Date.now()).toLocaleDateString()}
                            </div>
                          </div>
                          
                          {/* Raw Events List */}
                          <div className="flex flex-col gap-3">
                            {insight.supporting_events.map((ev) => (
                              <div key={ev.id} className="bg-gray-50 border border-gray-200 p-3.5 rounded-lg flex flex-col gap-2">
                                <div className="flex justify-between items-start gap-4">
                                  <div className="flex flex-wrap gap-2 items-center">
                                    <span className="text-xs font-semibold text-gray-700 bg-white px-2 py-0.5 rounded border border-gray-200">
                                      {ev.event_type?.replace(/_/g, " ")}
                                    </span>
                                    {ev.event_subtype && <span className="text-[11px] text-gray-500">{ev.event_subtype}</span>}
                                  </div>
                                  {ev.url && (
                                    <a href={ev.url} target="_blank" rel="noopener noreferrer" className="text-[10px] font-medium bg-blue-50 text-blue-600 border border-blue-200 px-2 py-1 rounded hover:bg-blue-100 transition-colors flex items-center gap-1 shrink-0">
                                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                                      {ev.source_name || "Source"}
                                    </a>
                                  )}
                                </div>
                                <p className="text-sm text-gray-600 italic">"{ev.description}"</p>
                                {(ev.location || ev.event_date) && (
                                  <div className="flex gap-4 text-[11px] text-gray-500 font-mono mt-1">
                                    {ev.location && <span className="flex items-center gap-1">📍 {ev.location}</span>}
                                    {ev.event_date && <span className="flex items-center gap-1">📅 {ev.event_date}</span>}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
