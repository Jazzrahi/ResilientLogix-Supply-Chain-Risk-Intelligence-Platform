import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { AlertTriangle } from 'lucide-react';

const createVehicleIcon = (type, heading, color, status, isHighlighted) => {
  const isAtRisk = status === 'at_risk';
  const highlightGlow = isHighlighted ? 'filter: drop-shadow(0 0 12px #fff) drop-shadow(0 0 15px rgba(255,255,255,0.8)); transform: scale(1.4);' : '';
  const transition = 'transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);';
  
  const iconHtml = type === 'maritime' 
    ? `<div class="relative flex items-center justify-center" style="${highlightGlow} ${transition}">
        ${isAtRisk ? '<div class="absolute w-12 h-12 bg-red-500 rounded-full animate-ping opacity-30"></div>' : ''}
        <div style="transform: rotate(${heading}deg); color: ${isAtRisk ? '#FF3131' : color}; font-size: 1.4rem; filter: ${isAtRisk ? 'drop-shadow(0 0 10px #FF3131)' : 'drop-shadow(0 0 4px rgba(0,0,0,0.5))'}">🚢</div>
       </div>`
    : `<div class="relative flex items-center justify-center" style="${highlightGlow} ${transition}">
        ${isAtRisk ? '<div class="absolute w-12 h-12 bg-red-500 rounded-full animate-ping opacity-30"></div>' : ''}
        <div style="transform: rotate(${heading}deg); color: ${isAtRisk ? '#FF3131' : color}; font-size: 1.9rem; filter: ${isAtRisk ? 'drop-shadow(0 0 10px #FF3131)' : 'drop-shadow(0 0 4px rgba(0,0,0,0.5))'}">✈️</div>
       </div>`;

  return L.divIcon({
    html: iconHtml,
    className: 'custom-vehicle-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });
};

export default function MapComponent({ activeSector, onSelectVessel, hoveredVesselId }) {
  const [vehicles, setVehicles] = useState([]);
  const [lastAlert, setLastAlert] = useState(null);
  const [selectedVessel, setSelectedVessel] = useState(null);
  const [dangerZones, setDangerZones] = useState([]);

  const fetchVessels = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/vessels');
      const data = await response.json();
      setVehicles(data);
      if (selectedVessel) {
        const updated = data.find(v => v.id === selectedVessel.id);
        if (updated) setSelectedVessel(updated);
      }
    } catch (err) {
      console.error("Failed to fetch vessels:", err);
    }
  };

  useEffect(() => {
    fetchVessels();
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'VESSEL_UPDATE') {
        setVehicles(data.data);
        if (selectedVessel) {
          const updated = data.data.find(v => v.id === selectedVessel.id);
          if (updated) setSelectedVessel(updated);
        }
      } else if (data.type === 'NEW_RISK_EVENT') {
        setLastAlert(data.scenario ? `Simulated Danger: ${data.scenario}` : data.message);
        if (data.lat && data.lng) {
          setDangerZones(prev => [...prev, { lat: data.lat, lng: data.lng, name: data.scenario }]);
        }
      }
    };
    return () => ws.close();
  }, [selectedVessel?.id]);

  const filteredVehicles = vehicles.filter(v => v.sector === activeSector.id);
  const themeHex = activeSector.colorClass.includes('amber') ? '#FFB800' : 
                   activeSector.colorClass.includes('emerald') ? '#10B981' : 
                   activeSector.colorClass.includes('cyan') ? '#06B6D4' : '#F43F5E';

  return (
    <div className="w-full h-full relative transition-all duration-700 overflow-hidden">
      {/* Tactical Grid Overlay */}
      <div className="absolute inset-0 pointer-events-none z-[1000] opacity-[0.03]" 
           style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>
      
      {/* HUD Scanline */}
      <div className="absolute inset-0 pointer-events-none z-[1001] opacity-[0.05] bg-gradient-to-b from-transparent via-white/10 to-transparent h-12 w-full animate-[scan_8s_linear_infinite]"
           style={{ top: '-10%' }}>
      </div>

      <style>{`
        @keyframes scan {
          0% { top: -10%; }
          100% { top: 110%; }
        }
      `}</style>

      <MapContainer 
        center={[20, 30]} 
        zoom={3} 
        style={{ height: '100%', width: '100%', background: '#020408' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          className="map-tile-layer"
        />
        
        <style>{`
          .leaflet-container { background: #050810 !important; }
          .map-tile-layer { 
            filter: brightness(0.9) saturate(0.8) contrast(1.1) !important;
          }
          .leaflet-marker-icon { transition: all 0.5s linear !important; }
          .glass-popup .leaflet-popup-content-wrapper {
             background: rgba(10, 15, 30, 0.95);
             backdrop-filter: blur(12px);
             border: 1px solid rgba(255, 255, 255, 0.1);
             border-radius: 12px;
             padding: 4px;
             box-shadow: 0 10px 40px rgba(0,0,0,0.6);
          }
          .glass-popup .leaflet-popup-content { margin: 12px; }
        `}</style>

        {selectedVessel && selectedVessel.route && (
          <Polyline 
            positions={[[selectedVessel.lat, selectedVessel.lng], ...selectedVessel.route]}
            pathOptions={{ 
              color: themeHex, 
              weight: 3, 
              dashArray: '1, 10', 
              opacity: 0.8,
              lineCap: 'round'
            }}
          />
        )}
        
        {filteredVehicles.map(v => (
          <Marker 
            key={v.id} 
            position={[v.lat, v.lng]}
            icon={createVehicleIcon(v.type, v.heading, themeHex, v.status, v.id === hoveredVesselId)}
            eventHandlers={{
              click: () => {
                setSelectedVessel(v);
                onSelectVessel(v);
              }
            }}
          >
            <Popup className="glass-popup">
              <div className="flex flex-col gap-1 min-w-[140px]">
                <div className="flex items-center justify-between mb-1">
                  <strong className="text-sm font-bold tracking-tight" style={{ color: v.status === 'at_risk' ? '#FF3131' : themeHex }}>{v.name}</strong>
                  <span className="text-[9px] font-mono opacity-50 uppercase">{v.type}</span>
                </div>
                <div className="h-px bg-white/10 my-1"></div>
                <div className="text-[10px] text-slate-300 font-mono">
                   <span className="opacity-50 uppercase text-[8px] mr-1">Cargo:</span> {v.cargo}
                </div>
                <div className="text-[10px] font-mono mt-1 flex items-center gap-2">
                   <span className="opacity-50 uppercase text-[8px]">Status:</span> 
                   <span className={`px-1.5 py-0.5 rounded-full text-[9px] font-bold ${v.status === 'at_risk' ? 'bg-red-500/20 text-red-400 animate-pulse' : 'bg-white/5 text-slate-400'}`}>
                     {v.status.toUpperCase()}
                   </span>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {dangerZones.map((zone, i) => (
          <Circle 
            key={i}
            center={[zone.lat, zone.lng]}
            radius={300000}
            pathOptions={{ color: '#FF3131', fillColor: '#FF3131', fillOpacity: 0.15, weight: 1, dashArray: '5, 10' }}
          >
            <Popup className="glass-popup">
              <div className="p-1">
                <strong className="text-red-500 flex items-center gap-2 uppercase tracking-widest text-[10px]">
                  <AlertTriangle size={12} /> {zone.name}
                </strong>
                <p className="text-[9px] text-slate-400 font-mono mt-1">SIMULATED DISRUPTION RADIUS</p>
              </div>
            </Popup>
          </Circle>
        ))}
      </MapContainer>
      
      {/* Dynamic Map HUD */}
      <div className="absolute bottom-6 left-6 z-[400] pointer-events-none flex flex-col gap-2">
        <div className="bg-slate-900/60 backdrop-blur-md border border-white/10 p-3 rounded-xl flex flex-col gap-1 shadow-2xl">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10B981]"></div>
            <span className="text-[10px] font-mono text-white font-bold uppercase tracking-[0.2em]">Live Telemetry</span>
          </div>
          <div className="h-px bg-white/10 my-1 w-24"></div>
          <span className="text-[9px] text-slate-400 font-mono uppercase">Nodes Tracked: <span className="text-white font-bold">{filteredVehicles.length}</span></span>
          <span className="text-[9px] text-slate-400 font-mono uppercase">Global Integrity: <span className="text-emerald-400 font-bold">98.2%</span></span>
        </div>
      </div>

      {lastAlert && (
        <div className="absolute top-6 right-6 z-[400] bg-red-600/90 backdrop-blur-xl border border-red-400/50 text-white px-6 py-3 rounded-xl shadow-[0_0_30px_rgba(239,68,68,0.4)] flex items-center gap-3 animate-bounce">
           <AlertTriangle size={20} className="animate-pulse" />
           <div className="flex flex-col">
             <span className="text-[10px] font-bold uppercase tracking-widest opacity-80">Crisis Protocol Initiated</span>
             <span className="text-sm font-bold tracking-tight">{lastAlert}</span>
           </div>
        </div>
      )}
    </div>
  );
}
