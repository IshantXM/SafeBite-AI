import React from 'react';
import { ShieldCheck, Bell, Camera } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 text-white flex items-center justify-between px-6 sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="p-2 bg-blue-600 rounded-lg shadow-md shadow-blue-600/30 group-hover:bg-blue-500 transition">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-extrabold text-lg tracking-tight text-white">SafetyBite-AI</h1>
              <span className="text-[10px] bg-blue-500/20 text-blue-300 font-semibold px-2 py-0.5 rounded border border-blue-400/30">
                DOCA GOVT OF INDIA
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Packaged Food Compliance &amp; Metrology Enforcement</p>
          </div>
        </Link>
      </div>

      <div className="flex items-center space-x-4">
        {/* Quick Launch Camera Scanner Button */}
        <Link
          to="/scanner"
          className="flex items-center space-x-2 text-xs font-extrabold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 px-3.5 py-2 rounded-xl shadow-md shadow-blue-600/25 transition border border-blue-400/30"
        >
          <Camera className="h-4 w-4 text-sky-200" />
          <span>Scan Food Package</span>
        </Link>

        <div className="hidden lg:flex items-center space-x-2 text-xs text-slate-300 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Camera Vision: 60 FPS</span>
        </div>

        <button className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
        </button>

        <div className="flex items-center space-x-3 pl-2 border-l border-slate-800">
          <div className="h-9 w-9 rounded-full bg-blue-700/60 border border-blue-500/40 flex items-center justify-center font-bold text-sm text-blue-200">
            IS
          </div>
          <div className="hidden md:block text-left">
            <div className="text-xs font-semibold text-white leading-tight">Inspector Sharma</div>
            <div className="text-[10px] text-slate-400">Delhi Food Safety &amp; Metrology</div>
          </div>
        </div>
      </div>
    </header>
  );
};
