import React, { useState } from 'react';
import { Globe, Factory, Activity, Cpu, Heart, Zap, Satellite, Map as MapIcon, Network, Bot, Shield } from 'lucide-react';
import MapComponent from './components/MapComponent';
import { IntelligenceFeed, CascadeAnalysis, RouteOptimizer, ActionTerminal, RerouteProposals, GlobalMacroAnalytics, ContextualThreatSimulator } from './components/DashboardComponents';

const SECTORS = [
  { id: 'energy', name: 'Energy & Oil', icon: Factory, colorClass: 'text-amber-500', bgClass: 'bg-amber-500/10', borderClass: 'border-amber-500/30', glowClass: 'shadow-[0_0_50px_-12px_rgba(245,158,11,0.15)]' },
  { id: 'health', name: 'Health & Vaccines', icon: Activity, colorClass: 'text-emerald-400', bgClass: 'bg-emerald-400/10', borderClass: 'border-emerald-400/30', glowClass: 'shadow-[0_0_50px_-12px_rgba(52,211,153,0.15)]' },
  { id: 'industrial', name: 'Industrial', icon: Cpu, colorClass: 'text-cyan-400', bgClass: 'bg-cyan-400/10', borderClass: 'border-cyan-400/30', glowClass: 'shadow-[0_0_50px_-12px_rgba(34,211,238,0.15)]' },
  { id: 'humanitarian', name: 'Rescue', icon: Heart, colorClass: 'text-rose-500', bgClass: 'bg-rose-500/10', borderClass: 'border-rose-500/30', glowClass: 'shadow-[0_0_50px_-12px_rgba(244,63,94,0.15)]' }
];

function App() {
  const [activeSector, setActiveSector] = useState(SECTORS[0]);
  const [selectedVessel, setSelectedVessel] = useState(null);
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const [rightTab, setRightTab] = useState('optimizer');
  const [hoveredVesselId, setHoveredVesselId] = useState(null);

  React.useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className={`h-screen w-screen bg-transparent text-slate-200 overflow-hidden font-sans flex flex-col p-3 gap-3 transition-all duration-700 ${activeSector.glowClass}`}>
      
      {/* Background Decorative Element */}
      <div className="fixed inset-0 pointer-events-none opacity-20 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]"></div>
      
      {/* Header */}
      <header className="h-16 glass-panel rounded-xl flex justify-between items-center px-6 shrink-0 relative overflow-hidden group">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
        <div className="flex items-center gap-4">
          <div className={`p-2 rounded-lg ${activeSector.bgClass} ${activeSector.borderClass} border`}>
            <Globe className={`${activeSector.colorClass} animate-pulse-soft`} size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white leading-tight">ResilientLogix</h1>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-[10px] font-mono text-slate-500 tracking-widest uppercase">System Operational // Level 5 Security</span>
            </div>
          </div>
        </div>
        
        <div className="flex gap-8 items-center">
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase mb-0.5">Active Protocol</span>
            <span className={`${activeSector.colorClass} font-bold text-sm tracking-wide`}>{activeSector.name.toUpperCase()}</span>
          </div>
          <div className="h-8 w-px bg-slate-800"></div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase mb-0.5">Chronos Sync</span>
            <span className="text-white font-mono text-sm">{time} UTC</span>
          </div>
        </div>
      </header>

      {/* Main Grid Content */}
      <div className="flex-1 flex gap-3 overflow-hidden">
        
        {/* Far-Left: Strategic Sector Sidebar */}
        <aside className="w-20 glass-panel rounded-xl flex flex-col items-center py-8 gap-8">
          {SECTORS.map((sector) => {
            const Icon = sector.icon;
            const isActive = activeSector.id === sector.id;
            return (
              <button
                key={sector.id}
                onClick={() => {
                  setActiveSector(sector);
                  setSelectedVessel(null);
                }}
                className={`group relative w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-500 ${isActive ? `${sector.bgClass} ${sector.borderClass} border shadow-lg scale-110` : 'hover:bg-white/5 border border-transparent'}`}
                title={sector.name}
              >
                {isActive && <div className={`absolute -left-3 w-1 h-8 rounded-r-full ${sector.colorClass.replace('text', 'bg')} animate-pulse`}></div>}
                <Icon className={`${isActive ? sector.colorClass : 'text-slate-500 group-hover:text-slate-300'} w-7 h-7 transition-colors`} />
                <div className={`absolute left-full ml-4 px-3 py-1.5 rounded bg-slate-900 text-white text-[10px] font-bold whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity border border-slate-700 z-50`}>
                  {sector.name.toUpperCase()}
                </div>
              </button>
            );
          })}
        </aside>

        {/* Left: Live Intelligence */}
        <aside className="w-80 glass-panel rounded-xl flex flex-col overflow-hidden">
           <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
             <div className="flex items-center gap-3">
               <Zap className={activeSector.colorClass} size={20} />
               <h2 className="font-bold text-sm tracking-tight text-slate-200">LIVE INTELLIGENCE</h2>
             </div>
             <div className="flex gap-1">
               <div className="w-1 h-1 rounded-full bg-slate-700"></div>
               <div className="w-1 h-1 rounded-full bg-slate-700"></div>
             </div>
           </div>
           <div className="flex-1 p-4 overflow-y-auto custom-scrollbar">
             <IntelligenceFeed colorClass={activeSector.colorClass} onHoverVessel={setHoveredVesselId} />
           </div>
        </aside>

        {/* Center: Interactive Map */}
        <main className="flex-1 glass-panel rounded-xl relative overflow-hidden">
           <div className="absolute top-4 left-4 z-[1000] pointer-events-none">
             <div className="bg-slate-900/80 backdrop-blur-md border border-white/10 p-3 rounded-lg flex flex-col gap-1">
               <div className="flex items-center gap-2">
                 <Satellite className="text-cyan-400" size={14} />
                 <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-widest">Global Theater Link</span>
               </div>
               <span className="text-[9px] text-slate-500 font-mono italic">Sat-ID: GX-7782 // Latency: 14ms</span>
             </div>
           </div>
           <MapComponent 
             activeSector={activeSector} 
             onSelectVessel={setSelectedVessel}
             hoveredVesselId={hoveredVesselId}
           />
        </main>

        {/* Right: Cascade & Route Optimizer */}
        <aside className="w-80 flex flex-col gap-3">
          
          <div className="flex-[0.8] glass-panel rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-white/5 flex items-center gap-3 bg-white/[0.02]">
             <Network className={activeSector.colorClass} size={20} />
             <h2 className="font-bold text-sm tracking-tight text-slate-200">{selectedVessel ? 'NODE IMPACT' : 'STRATEGIC MACRO'}</h2>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              {selectedVessel ? (
                <div className="flex flex-col">
                  <CascadeAnalysis selectedVessel={selectedVessel} colorClass={activeSector.colorClass} />
                  <ContextualThreatSimulator 
                    selectedVessel={selectedVessel} 
                    colorClass={activeSector.colorClass} 
                    onSimulate={() => setRightTab('proposals')}
                  />
                </div>
              ) : (
                <GlobalMacroAnalytics colorClass={activeSector.colorClass} />
              )}
            </div>
          </div>

          <div className="flex-1 glass-panel rounded-xl flex flex-col overflow-hidden">
            <div className="flex border-b border-white/5 bg-white/[0.01]">
              <button 
                onClick={() => setRightTab('optimizer')}
                className={`flex-1 p-4 flex flex-col items-center gap-1 transition-all relative ${rightTab === 'optimizer' ? '' : 'opacity-40 grayscale hover:opacity-100 hover:grayscale-0'}`}
              >
                <MapIcon size={18} className={activeSector.colorClass} />
                <span className="text-[10px] font-bold tracking-widest">OPTIMIZER</span>
                {rightTab === 'optimizer' && <div className={`absolute bottom-0 left-0 w-full h-1 ${activeSector.colorClass.replace('text', 'bg')}`}></div>}
              </button>
              <button 
                onClick={() => setRightTab('proposals')}
                className={`flex-1 p-4 flex flex-col items-center gap-1 transition-all relative ${rightTab === 'proposals' ? '' : 'opacity-40 grayscale hover:opacity-100 hover:grayscale-0'}`}
              >
                <Shield size={18} className="text-red-500" />
                <span className="text-[10px] font-bold tracking-widest">MITIGATIONS</span>
                {rightTab === 'proposals' && <div className="absolute bottom-0 left-0 w-full h-1 bg-red-500"></div>}
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              {rightTab === 'optimizer' ? (
                <RouteOptimizer selectedVessel={selectedVessel} colorClass={activeSector.colorClass} />
              ) : (
                <RerouteProposals selectedVessel={selectedVessel} colorClass={activeSector.colorClass} />
              )}
            </div>
          </div>

        </aside>

      </div>

      {/* Bottom: Automated Actions Center */}
      <footer className="h-36 glass-panel rounded-xl shrink-0 flex flex-col overflow-hidden">
         <div className="p-3 border-b border-white/5 flex items-center justify-between bg-white/[0.03]">
           <div className="flex items-center gap-3">
            <div className="p-1 rounded bg-slate-800 border border-slate-700">
              <Bot className={activeSector.colorClass} size={16} />
            </div>
            <h2 className="font-bold text-xs tracking-widest text-slate-400 uppercase">Automated Intelligence Logs</h2>
           </div>
           <div className="flex gap-3">
             <div className="flex items-center gap-1.5">
               <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
               <span className="text-[10px] font-mono text-slate-500 uppercase tracking-tighter">AI Core // Stable</span>
             </div>
           </div>
         </div>
         <div className="flex-1 p-4 overflow-y-auto custom-scrollbar font-mono">
            <ActionTerminal colorClass={activeSector.colorClass} />
         </div>
      </footer>

    </div>
  );
}

export default App;
