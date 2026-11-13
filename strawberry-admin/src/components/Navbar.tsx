import React from 'react';
import { ShieldCheck, AlertCircle } from 'lucide-react';
import { isSupabaseConfigured } from '../lib/supabase';

export const Navbar: React.FC = () => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🍓</span>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              Strawberry <span className="text-xs bg-rose-500/20 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded-full font-medium">Faculty Admin</span>
            </h1>
            <p className="text-xs text-slate-400">Department Laboratory Program Catalog</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {isSupabaseConfigured ? (
            <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-md">
              <ShieldCheck className="w-4 h-4" />
              <span>Supabase Connected</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-md">
              <AlertCircle className="w-4 h-4" />
              <span>Local Demo Mode (Add Supabase URL & Publishable Key to connect)</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
