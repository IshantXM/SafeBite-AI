import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LiveScanner } from './pages/LiveScanner';
import { CommandCenter } from './pages/CommandCenter';
import { CaseManagement } from './pages/CaseManagement';
import { VisualEvidenceInspector } from './pages/VisualEvidenceInspector';
import { BrandSelfCheck } from './pages/BrandSelfCheck';
import { RuleAdminConsole } from './pages/RuleAdminConsole';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
        <Navbar />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-6 overflow-y-auto max-w-7xl mx-auto w-full">
            <Routes>
              <Route path="/" element={<LiveScanner />} />
              <Route path="/scanner" element={<LiveScanner />} />
              <Route path="/command" element={<CommandCenter />} />
              <Route path="/cases" element={<CaseManagement />} />
              <Route path="/inspector" element={<VisualEvidenceInspector />} />
              <Route path="/self-check" element={<BrandSelfCheck />} />
              <Route path="/rules-admin" element={<RuleAdminConsole />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};
