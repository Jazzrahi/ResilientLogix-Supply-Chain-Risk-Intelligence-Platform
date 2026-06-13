import React, { useEffect, useState } from 'react';
import { AlertTriangle, Info, CheckCircle, Zap, TrendingUp, ShieldAlert, BarChart3, Activity, Shield } from 'lucide-react';

export const GlobalMacroAnalytics = ({ colorClass }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const initialData = Array.from({ length: 40 }, (_, i) => ({
      riskValue: Math.floor(40 + Math.random() * 60)
    }));
    setData(initialData);

    const interval = setInterval(() => {
      setData(prev => {
        const next = [...prev.slice(1)];
        const last = next[next.length - 1];
        next.push({
          riskValue: Math.max(20, Math.min(100, last.riskValue + (Math.random() - 0.5) * 30))
        });
        return next;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full p-5 gap-8">
      {/* Risk Index Section */}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-between items-end mb-3">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase mb-1">Global Value at Risk</span>
            <span className="text-xl font-bold text-white flex items-center gap-2">
              $4.2B <TrendingUp className="text-red-500" size={16} />
            </span>
          </div>
          <span className="text-red-400 font-mono text-[9px] font-bold animate-pulse px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20 uppercase tracking-tighter">Live Analysis</span>
        </div>
        
        <div className="flex-1 flex items-end gap-1 border-b border-l border-white/10 p-2 relative min-h-[120px] bg-gradient-to-tr from-white/[0.02] to-transparent rounded-bl-lg">
          {data.map((d, i) => (
            <div 
              key={i} 
              className="flex-1 bg-gradient-to-t from-red-500/20 via-red-500/50 to-red-500 transition-all duration-500 ease-linear rounded-t-[1px] hover:brightness-125"
              style={{ height: `${d.riskValue}%` }}
            ></div>
          ))}
          {/* Horizontal Grid Lines */}
          <div className="absolute top-0 left-0 w-full border-t border-white/5 border-dashed pointer-events-none"></div>
          <div className="absolute top-1/2 left-0 w-full border-t border-white/5 border-dashed pointer-events-none"></div>
        </div>
        <div className="flex justify-between text-[8px] font-mono text-slate-500 mt-2 uppercase tracking-widest">
          <span>T-40s Interval</span>
          <span>Buffer Active</span>
        </div>
      </div>
      
      {/* Efficiency Section */}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-between items-end mb-3">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase mb-1">Network Efficiency</span>
            <span className="text-xl font-bold text-white flex items-center gap-2">
              92.4% <Activity className="text-emerald-400" size={16} />
            </span>
          </div>
          <span className="text-emerald-400 font-mono text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 uppercase tracking-tighter">Optimal</span>
        </div>
        
        <div className="flex-1 flex items-end gap-1 border-b border-l border-white/10 p-2 relative min-h-[120px] bg-gradient-to-tr from-white/[0.02] to-transparent rounded-bl-lg">
          {data.map((d, i) => (
            <div 
              key={i} 
              className="flex-1 bg-gradient-to-t from-emerald-500/10 via-emerald-500/40 to-emerald-400 transition-all duration-500 ease-linear rounded-t-[1px]"
              style={{ height: `${100 - (d.riskValue * 0.6)}%` }}
            ></div>
          ))}
        </div>
        <div className="flex justify-between text-[8px] font-mono text-slate-500 mt-2 uppercase tracking-widest">
          <span>Global Latency</span>
          <span>14ms Avg</span>
        </div>
      </div>
    </div>
  );
};

export const IntelligenceFeed = ({ colorClass, onHoverVessel }) => {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState("");

  const fetchFeed = async () => {
    setLoading(true);
    try {
      const resp = await fetch('http://localhost:8000/api/intelligence');
      const data = await resp.json();
      setFeed(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error("News fetch failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
    const interval = setInterval(fetchFeed, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-4 relative">
      {/* Timeline Thread */}
      <div className="absolute left-[23px] top-12 bottom-0 w-px bg-gradient-to-b from-white/20 via-white/10 to-transparent"></div>

      <div className="flex justify-between items-center mb-1 px-1 bg-slate-900/40 p-2 rounded border border-white/5 backdrop-blur-sm">
        <div className="flex flex-col">
          <span className="text-[8px] text-slate-500 font-mono font-bold tracking-widest uppercase">Stream Integrity</span>
          <span className="text-[10px] text-white font-mono">{lastUpdated} SYNC</span>
        </div>
        <button 
          onClick={fetchFeed}
          disabled={loading}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all text-slate-300 hover:text-white"
        >
          {loading ? <Zap className="animate-spin text-cyan-400" size={14} /> : <BarChart3 size={14} />}
        </button>
      </div>

      <div className="flex flex-col gap-4">
        {feed.map((item, i) => (
          <a 
            key={item.id} 
            href={item.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="group relative pl-10 no-underline block"
          >
            {/* Timeline Dot */}
            <div className={`absolute left-[19px] top-4 w-2 h-2 rounded-full border-2 border-slate-900 z-10 transition-transform group-hover:scale-150 ${
              item.type === 'critical' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' : 
              item.type === 'warning' ? 'bg-amber-500' : 'bg-emerald-500'
            }`}></div>

            <div className="glass-card p-3 rounded-xl border border-white/5 relative overflow-hidden">
               <div className="flex items-center justify-between mb-2">
                <span className={`text-[9px] font-bold tracking-widest px-2 py-0.5 rounded-full border ${
                  item.type === 'critical' ? 'bg-red-500/10 border-red-500/30 text-red-400' : 
                  item.type === 'warning' ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                }`}>
                  {item.type?.toUpperCase() || 'INFO'}
                </span>
                <span className="text-[9px] text-slate-500 font-mono font-bold uppercase">{item.source}</span>
              </div>
              
              <h4 className="text-[11px] text-slate-200 leading-snug font-semibold group-hover:text-white transition-colors mb-2 line-clamp-3">
                {item.title}
              </h4>

              <div className="flex justify-between items-center pt-2 border-t border-white/5">
                <div className="flex items-center gap-3">
                  <div className="text-[8px] text-slate-500 font-mono font-bold">{item.time?.split(' ').slice(0,3).join(' ') || 'JUST NOW'}</div>
                  {item.affected_vessel && (
                    <div 
                      onMouseEnter={() => onHoverVessel(item.affected_vessel.id)}
                      onMouseLeave={() => onHoverVessel(null)}
                      className="relative group/icon"
                    >
                      <div className="p-1 rounded bg-white/5 border border-white/10 hover:bg-white/20 transition-all text-[10px]">
                        {item.affected_vessel.type === 'maritime' ? '🚢' : '✈️'}
                      </div>
                      
                      <div className="absolute bottom-full left-0 mb-2 w-40 p-2 bg-slate-900/95 border border-white/10 rounded-lg shadow-2xl opacity-0 group-hover/icon:opacity-100 pointer-events-none transition-all translate-y-1 group-hover/icon:translate-y-0 z-50 backdrop-blur-xl">
                        <p className="text-[9px] text-slate-200 leading-tight">
                          <span className="text-cyan-400 font-bold block mb-1">ASSET ALERT</span>
                          Your {item.affected_vessel.type === 'maritime' ? 'ship' : 'plane'} <span className="text-white font-bold">{item.affected_vessel.name}</span> is in the impact radius.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
                <div className="text-[9px] text-cyan-400 font-bold opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0">INTEL ↗</div>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};

export const CascadeAnalysis = ({ selectedVessel, colorClass }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (selectedVessel) {
      setData(null);
      fetch(`http://localhost:8000/api/cascade/${selectedVessel.id}`)
        .then(r => r.json())
        .then(setData);
    }
  }, [selectedVessel]);

  if (!selectedVessel) return <div className="p-10 text-center text-slate-600 text-[10px] font-mono uppercase tracking-[0.2em] animate-pulse">Scanning Grid for Selection...</div>;
  if (!data) return <div className="p-10 text-center text-slate-500 text-[10px] font-mono animate-pulse uppercase tracking-[0.2em]">Executing Nodal Cascade...</div>;

  return (
    <div className="p-4 flex flex-col gap-4">
      <div className="p-3 rounded-lg bg-white/5 border border-white/10">
        <div className="text-[9px] text-slate-500 font-mono tracking-widest uppercase mb-1">Target Analysis</div>
        <div className="text-sm font-bold text-white tracking-tight">{selectedVessel.name}</div>
        <div className="text-[10px] text-slate-400 font-mono mt-1 opacity-60">UUID: {selectedVessel.id}</div>
      </div>

      <div className="flex flex-col gap-4 relative pl-2">
        <div className="absolute left-[11px] top-2 bottom-2 w-px bg-white/10"></div>
        {data?.nodes.map((node, i) => (
          <div key={i} className="flex gap-4 items-start relative group">
            <div className={`w-2.5 h-2.5 rounded-full mt-1 border-2 border-slate-900 z-10 ${node.impact === 'High' ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`}></div>
            <div className="flex-1 p-2.5 rounded-lg border border-white/5 bg-white/[0.02] group-hover:bg-white/5 transition-colors">
              <div className="flex justify-between items-center mb-1">
                <div className="text-[11px] font-bold text-slate-100">{node.name}</div>
                <div className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${node.impact === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-slate-500/20 text-slate-400'}`}>
                  {node.impact.toUpperCase()}
                </div>
              </div>
              <div className="text-[9px] text-slate-500 font-mono">ESTIMATED DELAY: {node.delay}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const RouteOptimizer = ({ selectedVessel, colorClass }) => {
  const [routes, setRoutes] = useState(null);

  useEffect(() => {
    if (selectedVessel) {
      setRoutes(null);
      fetch(`http://localhost:8000/api/vessels/${selectedVessel.id}/reroute`)
        .then(r => r.json())
        .then(setRoutes);
    }
  }, [selectedVessel]);

  if (!selectedVessel) return <div className="p-10 text-center text-slate-600 text-[10px] font-mono uppercase tracking-[0.2em]">Awaiting Asset Lock...</div>;
  if (!routes) return <div className="p-10 text-center text-slate-500 text-[10px] font-mono animate-pulse uppercase tracking-[0.2em]">Calculating Trajectories...</div>;

  return (
    <div className="p-4 h-full flex flex-col overflow-hidden">
       <div className="text-[10px] text-slate-500 mb-4 font-mono font-bold tracking-widest px-1 shrink-0 flex items-center gap-2">
         <ShieldAlert size={12} className={colorClass} /> AI TRAJECTORY MODELS
       </div>
       <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-3 custom-scrollbar">
         {routes?.all_options.map((opt, i) => (
           <div key={i} className={`p-4 rounded-xl border transition-all ${i === 0 ? `bg-white/[0.04] ${colorClass.replace('text', 'border')}` : 'bg-white/5 border-white/10 opacity-50 grayscale hover:grayscale-0 hover:opacity-100'}`}>
              <div className="flex justify-between items-center mb-3">
                <span className="text-xs font-bold text-white">{opt.name.toUpperCase()}</span>
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white/10 ${colorClass}`}>MATCH: {opt.score}%</span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="flex flex-col gap-1">
                  <div className="text-[8px] text-slate-500 font-mono uppercase tracking-tighter">Safety</div>
                  <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-400" style={{ width: `${opt.safety}%` }}></div>
                  </div>
                </div>
                <div className="flex flex-col gap-1">
                  <div className="text-[8px] text-slate-500 font-mono uppercase tracking-tighter">Time</div>
                  <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-400" style={{ width: `${opt.time}%` }}></div>
                  </div>
                </div>
                <div className="flex flex-col gap-1">
                  <div className="text-[8px] text-slate-500 font-mono uppercase tracking-tighter">Cost</div>
                  <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-400" style={{ width: `${opt.cost}%` }}></div>
                  </div>
                </div>
              </div>
              {i === 0 && (
                <div className="mt-4 flex items-center gap-2 text-[10px] text-emerald-400 font-bold uppercase tracking-widest bg-emerald-500/10 p-2 rounded border border-emerald-500/20">
                  <CheckCircle size={14} /> AI Primary Recommendation
                </div>
              )}
           </div>
         ))}
       </div>
    </div>
  );
};

export const ActionTerminal = ({ colorClass }) => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/logs')
      .then(r => r.json())
      .then(setLogs);
  }, []);

  return (
    <div className="font-mono text-[11px] flex flex-col gap-1.5 relative overflow-hidden">
      <div className="scanline"></div>
      {logs.map((log, i) => (
        <div key={i} className="flex gap-4 opacity-80 hover:opacity-100 transition-opacity">
          <span className="text-slate-600 shrink-0 font-bold">[{log.time}]</span>
          <span className="text-slate-400 font-medium">
            <span className="text-slate-500 uppercase text-[9px] mr-2">Core_Process:</span> 
            <span className="text-slate-100">{log.msg}</span>
          </span>
        </div>
      ))}
      <div className="flex items-center gap-2 mt-2">
        <span className="w-1.5 h-3 bg-cyan-500 animate-pulse"></span>
        <span className="text-slate-500 text-[10px]">Awaiting system instructions...</span>
      </div>
    </div>
  );
};

export const RerouteProposals = ({ selectedVessel, colorClass }) => {
  const [proposals, setProposals] = useState([]);

  useEffect(() => {
    const fetchProposals = () => {
      fetch('http://localhost:8000/api/proposals')
        .then(r => r.json())
        .then(setProposals);
    };
    fetchProposals();
    const interval = setInterval(fetchProposals, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleExecute = async (proposal) => {
    try {
      const resp = await fetch('http://localhost:8000/api/execute-switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vessel_id: proposal.vessel_id })
      });
      if (resp.ok) {
        setProposals(prev => prev.filter(p => p.shipment_id !== proposal.shipment_id));
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (!selectedVessel) return <div className="p-10 text-center text-slate-600 text-[10px] font-mono uppercase tracking-[0.2em]">Scanning for Active Threats...</div>;
  
  const vesselProposals = proposals.filter(p => p.vessel_id === selectedVessel.id);

  if (vesselProposals.length === 0) return (
    <div className="p-10 text-center">
      <Shield className="w-10 h-10 text-slate-700 mx-auto mb-4 opacity-20" />
      <p className="text-slate-600 text-[10px] font-mono uppercase tracking-widest mb-4">No mitigations required for {selectedVessel.name}</p>
      {selectedVessel.status !== 'at_risk' && (
        <div className="bg-emerald-500/5 border border-emerald-500/10 p-3 rounded-lg text-[10px] text-emerald-500/70 uppercase font-bold tracking-widest flex items-center justify-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
          Node Integrity: Optimal
        </div>
      )}
    </div>
  );

  return (
    <div className="flex flex-col h-full p-4 overflow-hidden">
      <div className="text-[10px] text-slate-500 mb-4 font-mono uppercase tracking-[0.2em] px-1 shrink-0 flex justify-between items-center border-b border-white/5 pb-2">
        <span>Strategy Queue</span>
        <span className="text-red-500 font-bold animate-pulse">Critical Intervention</span>
      </div>
      <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-4 custom-scrollbar">
        {vesselProposals.map((p, i) => (
          <div key={i} className="glass-card p-4 rounded-xl border border-red-500/20 bg-red-500/[0.02] group">
            <div className="flex justify-between items-start mb-3">
              <span className="text-[10px] font-bold text-red-400 font-mono">MITIGATION_{p.shipment_id}</span>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></div>
                <span className="text-[9px] text-red-500 font-bold uppercase tracking-tighter">AI PRIORITY</span>
              </div>
            </div>
            
            <h4 className="text-sm font-bold text-white mb-2">{p.vessel}</h4>
            <p className="text-[11px] text-slate-400 mb-4 leading-relaxed line-clamp-2">{p.reason}</p>
            
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-2 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                <div className="text-[8px] text-emerald-500/60 font-mono uppercase">Resilience Gain</div>
                <div className="text-xs font-bold text-emerald-400">-{p.time_saved} ETA</div>
              </div>
              <div className="p-2 rounded-lg bg-amber-500/5 border border-amber-500/10">
                <div className="text-[8px] text-amber-500/60 font-mono uppercase">Cost Delta</div>
                <div className="text-xs font-bold text-amber-400">+${p.cost_delta.toLocaleString()}</div>
              </div>
            </div>

            <button 
              onClick={() => handleExecute(p)}
              className="w-full py-2.5 bg-red-500/10 border border-red-500/30 text-red-400 text-[10px] font-bold rounded-lg hover:bg-red-500/30 transition-all uppercase tracking-[0.2em] flex items-center justify-center gap-2 group-hover:border-red-500"
            >
              <ShieldAlert size={14} /> AUTHORIZE MODE SWITCH
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export const ContextualThreatSimulator = ({ selectedVessel, colorClass, onSimulate }) => {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedVessel) {
      setLoading(true);
      fetch(`http://localhost:8000/api/vessels/${selectedVessel.id}/threat-scenarios`)
        .then(r => r.json())
        .then(data => {
          setScenarios(data);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [selectedVessel]);

  if (!selectedVessel) return null;

  const handleSimulate = async (scenario) => {
    try {
      await fetch(`http://localhost:8000/api/simulate-risk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vessel_id: selectedVessel.id,
          scenario_id: scenario.id,
          scenario_name: scenario.name
        })
      });
      if (onSimulate) onSimulate();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="mt-4 p-4 border border-red-500/20 rounded-xl bg-red-500/[0.03] flex flex-col gap-4 relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-red-500/20 animate-pulse"></div>
      <div className="flex items-center gap-3">
        <div className="p-1.5 rounded-lg bg-red-500/20 border border-red-500/30">
          <AlertTriangle className="text-red-400" size={16} />
        </div>
        <div>
          <h3 className="text-[10px] text-red-400 font-mono uppercase tracking-[0.2em] font-bold leading-none">Simulation Core</h3>
          <span className="text-[9px] text-slate-500 font-mono">Injecting Disruption Vectors</span>
        </div>
      </div>
      
      {loading ? (
        <div className="p-4 text-center text-[10px] text-slate-600 font-mono uppercase animate-pulse">Calculating Regional Risks...</div>
      ) : (
        <div className="grid grid-cols-1 gap-2.5">
          {scenarios.map(scenario => (
            <button
              key={scenario.id}
              onClick={() => handleSimulate(scenario)}
              className="relative overflow-hidden p-3 text-left rounded-lg border transition-all bg-white/[0.02] hover:bg-white/[0.05] border-white/10 group/btn"
            >
              <div className="flex justify-between items-center">
                <span className="text-[11px] font-bold text-slate-300 group-hover/btn:text-white transition-colors">{scenario.name.toUpperCase()}</span>
                <div className={`w-1.5 h-1.5 rounded-full ${scenario.severity === 'critical' ? 'bg-red-500 animate-pulse' : 'bg-amber-500'}`}></div>
              </div>
              <div className="text-[8px] text-slate-500 font-mono mt-1 uppercase tracking-tighter">Severity: {scenario.severity} // Action: Trigger</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
