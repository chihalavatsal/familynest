import { useState, useEffect } from 'react';
import { Users, HeartHandshake, Network, ShieldCheck, Home, CheckCircle2 } from 'lucide-react';

export function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    fetch(`${apiUrl}/health`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setBackendStatus('connected');
        } else {
          setBackendStatus('disconnected');
        }
      })
      .catch(() => {
        setBackendStatus('disconnected');
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#fdfaf7] text-slate-800 flex flex-col font-sans selection:bg-amber-100">
      {/* Header / Brand Bar */}
      <header className="border-b border-amber-900/10 bg-white/70 backdrop-blur-md sticky top-0 z-50 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-700 to-amber-600 flex items-center justify-center text-white shadow-sm shadow-amber-900/10">
            <Home className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-serif font-semibold tracking-tight text-slate-900">FamilyNest</h1>
            <p className="text-[11px] text-amber-800/80 font-medium tracking-wide uppercase">Private Digital Home</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border bg-amber-50/50 border-amber-200/60 text-amber-900">
            <span className={`w-2 h-2 rounded-full mr-2 ${
              backendStatus === 'connected' ? 'bg-emerald-500' :
              backendStatus === 'checking' ? 'bg-amber-400 animate-pulse' : 'bg-rose-400'
            }`} />
            API: {backendStatus}
          </span>
        </div>
      </header>

      {/* Hero / Overview Section */}
      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-16 w-full flex flex-col items-center">
        <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-amber-100/60 text-amber-900 text-xs font-medium mb-5">
            <ShieldCheck className="w-3.5 h-3.5 text-amber-700" />
            <span>Phase 0: Project Setup Initialized</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-serif font-bold text-slate-900 tracking-tight leading-tight mb-4">
            A quiet, private sanctuary for your family story.
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-light">
            Designed from the ground up around real human relationships: living memories, multi-generational networks, and lasting privacy.
          </p>
        </div>

        {/* 3 Core Architecture Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mb-12">
          {/* People */}
          <div className="bg-white rounded-2xl p-6 sm:p-7 border border-amber-900/10 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-800 flex items-center justify-center mb-5">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-serif font-semibold text-slate-900 mb-2">People</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Every person exists as an independent human record. Accounts can claim existing records without duplicating identities.
            </p>
          </div>

          {/* Relationships */}
          <div className="bg-white rounded-2xl p-6 sm:p-7 border border-amber-900/10 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-800 flex items-center justify-center mb-5">
              <HeartHandshake className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-serif font-semibold text-slate-900 mb-2">Relationships</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Stores fundamental ties (parent, spouse, child, sibling) and preserves historical records. Derived relations are calculated naturally.
            </p>
          </div>

          {/* Family Networks */}
          <div className="bg-white rounded-2xl p-6 sm:p-7 border border-amber-900/10 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-800 flex items-center justify-center mb-5">
              <Network className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-serif font-semibold text-slate-900 mb-2">Family Networks</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Members can belong to multiple distinct circles (maternal, paternal, in-laws) without artificially merging family boundaries.
            </p>
          </div>
        </div>

        {/* Readiness Checklist Card */}
        <div className="w-full bg-white rounded-2xl p-6 sm:p-8 border border-amber-900/10 shadow-sm">
          <h4 className="text-base font-semibold text-slate-900 uppercase tracking-wider text-xs mb-4 text-amber-800">
            System Initialization Status
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>Modular FastAPI backend architecture</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>SQLAlchemy 2.x &amp; Alembic configuration</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>React, TypeScript &amp; Tailwind CSS</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>Local PostgreSQL with Docker Compose volume</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>Environment configuration (.env, .env.example)</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>Capacitor &amp; mobile responsive readiness</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-amber-900/10 py-6 px-4 text-center text-xs text-slate-500">
        FamilyNest &copy; {new Date().getFullYear()} &bull; A Private Digital Home for Families
      </footer>
    </div>
  );
}

export default App;
