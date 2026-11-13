import React from 'react';
import { Database, Calendar, Shield, Download, Plus } from 'lucide-react';
import { isSupabaseConfigured } from '../lib/supabase';

interface NavbarProps {
  onNewSubject: () => void;
  onExportManifest: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onNewSubject, onExportManifest }) => {
  return (
    <header className="bg-[#051424] border-b border-[#273647] flex justify-between items-center w-full px-5 h-14 shrink-0 z-30 select-none">
      {/* Brand & Telemetry */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 bg-[#f43f5e] rounded-xs shadow-[0_0_8px_rgba(244,63,94,0.4)]" />
          <span className="font-mono text-xs tracking-wider font-bold text-white flex items-center gap-1.5">
            STRAWBERRY <span className="text-[#f43f5e] font-semibold">//</span> REGISTRY
          </span>
        </div>

        <div className="h-3.5 w-[1px] bg-[#273647]" />

        <div className="flex items-center gap-1.5 bg-[#0d1c2d] border border-[#273647] px-2.5 py-1 rounded-xs text-[11px] font-mono text-[#bec6e0]">
          <Calendar className="w-3 h-3 text-[#94a3b8]" />
          <span>AY 2026-27</span>
        </div>

        <div className="flex items-center gap-2 bg-[#0d1c2d] border border-[#273647] px-2.5 py-1 rounded-xs text-[11px] font-mono">
          {isSupabaseConfigured ? (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
              <span className="text-[#10b981] font-medium flex items-center gap-1">
                <Database className="w-3 h-3 text-[#10b981]" />
                DB_LIVE
              </span>
            </>
          ) : (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b]" />
              <span className="text-[#f59e0b] font-medium">LOCAL_STANDALONE</span>
            </>
          )}
        </div>
      </div>

      {/* Operator Status & Actions */}
      <div className="flex items-center space-x-3">
        <div className="hidden sm:flex items-center gap-1.5 bg-[#0d1c2d] px-2.5 py-1 rounded-xs border border-[#273647] text-[11px] font-mono text-[#bec6e0]">
          <Shield className="w-3 h-3 text-[#f43f5e]" />
          <span>FACULTY_CONTROL_PLANE</span>
        </div>

        <button
          onClick={onExportManifest}
          className="bg-[#122131] hover:bg-[#1c2b3c] active:translate-y-[0.5px] border border-[#273647] text-[#d4e4fa] px-3 py-1 rounded-xs text-[11px] font-mono transition-colors flex items-center gap-1.5 cursor-pointer"
          title="Export JSON manifest of all registered programs and SHA-256 hashes"
        >
          <Download className="w-3 h-3 text-[#94a3b8]" />
          <span>EXPORT_MANIFEST</span>
        </button>

        <button
          onClick={onNewSubject}
          className="bg-[#f43f5e] hover:bg-[#e11d48] active:translate-y-[0.5px] text-[#051424] font-bold px-3 py-1 rounded-xs text-[11px] font-mono transition-colors flex items-center gap-1.5 shadow-sm cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>NEW_SUBJECT</span>
        </button>
      </div>
    </header>
  );
};
