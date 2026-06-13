import os
import math
import asyncio
from fastapi import FastAPI, BackgroundTasks, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.ml_engine import ml_engine
from services.optimizer import optimizer
import pandas as pd
import json
import httpx
from geopy.distance import geodesic
import random
import math

import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Physical DBMS Mirror (For Viva/Demo) ---
SQLITE_DB = "logistics.db"

def init_sqlite_db():
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS live_fleet 
                 (id TEXT PRIMARY KEY, name TEXT, type TEXT, status TEXT, lat REAL, lng REAL, destination TEXT)''')
    conn.commit()
    conn.close()

def sync_to_db():
    """Dumps the in-memory state to a physical SQL file for the examiner to see."""
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    for v in db_vessels.values():
        c.execute('''INSERT OR REPLACE INTO live_fleet (id, name, type, status, lat, lng, destination) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                  (v["id"], v["name"], v["type"], v["status"], v["lat"], v["lng"], v["destination"]))
    conn.commit()
    conn.close()

init_sqlite_db()

Base = declarative_base()

class Shipment(Base):
    __tablename__ = 'shipments'
    id = Column(String, primary_key=True)
    vessel_id = Column(String)
    priority = Column(String)
    cargo_value = Column(Float)

class Vessel(Base):
    __tablename__ = 'vessels'
    id = Column(String, primary_key=True)
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String)

# SQL View simulation logic (Python side for this demo)
def get_v_impact_analysis():
    """
    Simulates the SQL View: 
    SELECT s.*, v.lat, v.lng, v.status 
    FROM shipments s JOIN vessels v ON s.vessel_id = v.id
    """
    return "JOIN vessels v ON s.vessel_id = v.id WHERE v.status = 'at_risk'"

app = FastAPI(title="ResilientLogix API - Prescriptive Engine")

# Allow React frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
connected_clients = set()

import random

# --- Fleet & Shipment Data Integration ---
try:
    kaggle_df = pd.read_csv("scripts/mock_supply_chain_data.csv")
except Exception:
    kaggle_df = pd.DataFrame()

db_vessels = {}

# Global Logistics Hubs
HUBS = {
    "Rotterdam": (51.92, 4.48),
    "Shanghai": (31.23, 121.47),
    "Houston": (29.76, -95.36),
    "Singapore": (1.35, 103.81),
    "Jebel Ali": (25.0, 55.0),
    "Los Angeles": (34.05, -118.24),
    "New York": (40.71, -74.00),
    "Tokyo": (35.67, 139.65),
    "London": (51.50, -0.12),
    "Mumbai": (19.07, 72.87),
    "Sydney": (-33.86, 151.20),
    "Cape Town": (-33.92, 18.42)
}

def generate_fleet(count=50):
    sectors = ["energy", "health", "industrial", "humanitarian"]
    
    for i in range(count):
        v_id = f"V-{1000 + i}"
        
        # Pull realistic data from our Kaggle Seeder if available
        if not kaggle_df.empty and i < len(kaggle_df):
            row = kaggle_df.iloc[i]
            v_name = row["vessel_name"]
            cargo = row["sector"] + " " + random.choice(["Shipment", "Supply", "Payload"])
            sector = row["sector"].lower()
            priority = row["priority"]
        else:
            sector = random.choice(sectors)
            v_name = f"Node-{random.randint(100, 999)}"
            cargo = f"Strategic {sector.capitalize()} Payload"
            priority = "normal"

        # Explicitly assign types: 40% aviation, 60% maritime
        v_type = "aviation" if random.random() > 0.6 else "maritime"
        if v_type == "aviation" and "SEA" in v_name: v_name = v_name.replace("SEA", "AERO")
        
        hub_names = list(HUBS.keys())
        origin = random.choice(hub_names)
        dest = random.choice([h for h in hub_names if h != origin])
        
        # Start near the origin
        o_lat, o_lng = HUBS[origin]
        lat = o_lat + random.uniform(-2, 2)
        lng = o_lng + random.uniform(-2, 2)
        
        db_vessels[v_id] = {
            "id": v_id,
            "name": v_name,
            "type": v_type,
            "sector": sector,
            "cargo": cargo,
            "priority": priority,
            "lat": lat,
            "lng": lng,
            "heading": 0, # Will be calculated
            "status": "normal",
            "origin": origin,
            "destination": dest,
            "route": [] # Will be populated live
        }

generate_fleet(50)

async def broadcast_vessel_state():
    """Broadcasts the entire active fleet state to all connected UI clients."""
    if not connected_clients: return
    state_json = json.dumps({"type": "VESSEL_UPDATE", "data": list(db_vessels.values())})
    disconnected = set()
    for client in connected_clients:
        try:
            await client.send_text(state_json)
        except:
            disconnected.add(client)
    for client in disconnected:
        connected_clients.remove(client)

async def fetch_live_aviation_data():
    """Pulls live, real-world aircraft coordinates from OpenSky Network."""
    while True:
        try:
            async with httpx.AsyncClient() as client:
                # Fetch live flights
                resp = await client.get("https://opensky-network.org/api/states/all", timeout=15.0)
                if resp.status_code == 200:
                    data = resp.json()
                    states = data.get("states", [])
                    if states:
                        valid_flights = [s for s in states if s[5] is not None and s[6] is not None and s[10] is not None]
                        random.shuffle(valid_flights)
                        
                        aviation_nodes = [v_id for v_id, v in db_vessels.items() if v["type"] == "aviation"]
                        
                        for i, v_id in enumerate(aviation_nodes):
                            if i < len(valid_flights):
                                flight = valid_flights[i]
                                # s[6] = lat, s[5] = lng, s[10] = heading, s[1] = callsign
                                db_vessels[v_id]["lat"] = flight[6]
                                db_vessels[v_id]["lng"] = flight[5]
                                db_vessels[v_id]["heading"] = flight[10]
                                callsign = flight[1].strip()
                                if callsign:
                                    db_vessels[v_id]["name"] = f"FLIGHT {callsign}"
        except Exception as e:
            print(f"OpenSky API Warning: {e}. Relying on internal physics engine.")
            
        await asyncio.sleep(15) # Poll OpenSky every 15s to avoid rate limits

def calculate_initial_compass_bearing(pointA, pointB):
    """Calculates the bearing between two points in degrees."""
    lat1, lon1 = map(math.radians, pointA)
    lat2, lon2 = map(math.radians, pointB)
    dLon = lon2 - lon1
    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dLon))
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    return (initial_bearing + 360) % 360

# --- Background Movement Simulator ---
async def simulate_movement():
    """Continuously update maritime positions using great-circle spherical physics."""
    while True:
        for v in db_vessels.values():
            if not v.get("destination"): continue
            
            dest_lat, dest_lng = HUBS[v["destination"]]
            
            # Distance to destination
            dist_to_dest = haversine_distance(v["lat"], v["lng"], dest_lat, dest_lng)
            
            if dist_to_dest < 100:
                # Arrived! Pick a new random destination
                hub_names = list(HUBS.keys())
                v["origin"] = v["destination"]
                v["destination"] = random.choice([h for h in hub_names if h != v["origin"]])
                dest_lat, dest_lng = HUBS[v["destination"]]
            
            # Calculate heading towards destination
            v["heading"] = calculate_initial_compass_bearing((v["lat"], v["lng"]), (dest_lat, dest_lng))
            
            # Draw the route polyline to destination
            v["route"] = [[dest_lat, dest_lng]]
            
            if v["type"] == "maritime":
                try:
                    # Move 50km per tick along the great circle path
                    current_point = (v["lat"], v["lng"])
                    dest = geodesic(kilometers=50).destination(current_point, v["heading"])
                    v["lat"], v["lng"] = dest.latitude, dest.longitude
                except Exception:
                    pass
            else:
                # Aviation is handled mostly by OpenSky, but we interpolate if OpenSky fails
                try:
                    current_point = (v["lat"], v["lng"])
                    dest = geodesic(kilometers=150).destination(current_point, v["heading"])
                    v["lat"], v["lng"] = dest.latitude, dest.longitude
                except Exception:
                    pass
                
        sync_to_db() # Sync to physical SQL file for Viva demo
        await broadcast_vessel_state()
        await asyncio.sleep(1) # Broadcast state to UI every 1 second (Live WebSockets)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_movement())
    asyncio.create_task(fetch_live_aviation_data())

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lng coordinates in km."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)

async def notify_clients(message: str):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            pass

# --- API Endpoints ---

@app.get("/api/vessels")
def get_vessels():
    """Returns all active vessels globally."""
    return list(db_vessels.values())

@app.get("/api/vessels/{vessel_id}/reroute")
def get_optimal_reroute(vessel_id: str):
    """Calculates optimal reroute using the AI Prescriptive Engine."""
    if vessel_id not in db_vessels:
        raise HTTPException(status_code=404, detail="Vessel not found")
    
    v = db_vessels[vessel_id]
    
    # Run ML prediction for current status
    risk_prob = 0.85 if v["status"] == "at_risk" else 0.15
    
    # Get Recommendation from Prescriptive Engine
    rec = optimizer.calculate_resilience_strategy(
        current_route_risk=risk_prob,
        alt_mode="AIR" if v["type"] == "maritime" else "SEA",
        cargo_priority=v["priority"],
        carbon_impact=0.12
    )
    
    potential_routes = [
        {"mode": rec["recommended_path"].lower(), "safety": 95, "time": 90, "cost": 40, "name": f"AI Optimized {rec['recommended_path']} Link"},
        {"mode": "sea" if rec["recommended_path"] == "AIR" else "air", "safety": 60, "time": 40, "cost": 80, "name": "Standard Alternate"}
    ]
        
    for route in potential_routes:
        route["score"] = round((0.4 * route["safety"]) + (0.3 * route["time"]) + (0.3 * route["cost"]), 2)
        
    potential_routes.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "vessel_id": vessel_id,
        "recommended_route": potential_routes[0],
        "all_options": potential_routes,
        "ai_analysis": rec
    }

# --- Intelligence Ingestion Service ---

async def fetch_and_process_news():
    """Simulates background geopolitics engine flagging vessels near risk zones."""
    await asyncio.sleep(2) # Simulate API fetch delay
    
    # Risk Event: Red Sea Blockade
    event_lat, event_lng = 15.0, 41.0
    
    flagged_count = 0
    # Simulate PostGIS 500km spatial trigger
    for v_id, v in db_vessels.items():
        dist = haversine_distance(event_lat, event_lng, v["lat"], v["lng"])
        if dist <= 500:
            db_vessels[v_id]["status"] = "at_risk"
            flagged_count += 1
            
    await notify_clients(f'{{"type": "NEW_RISK_EVENT", "message": "Red Sea maritime blockade detected! {flagged_count} vessels flagged AT_RISK."}}')

@app.post("/api/trigger-scenario")
async def trigger_scenario(background_tasks: BackgroundTasks):
    """Endpoint to manually trigger the scenario for the demo."""
    background_tasks.add_task(fetch_and_process_news)
    
    # Run the prescriptive simulation to generate proposals
    import subprocess
    def run_simulation():
        subprocess.run(["python3", "scripts/simulate_crisis.py"])
    
    background_tasks.add_task(run_simulation)
    return {"status": "Scenario triggered, processing in background..."}

class DisruptionReportRequest(BaseModel):
    lat: float
    lng: float
    radius: float

@app.post("/api/analyze-disruption")
def analyze_disruption(req: DisruptionReportRequest):
    """Returns a detailed Economic Impact Report for a specific zone."""
    vessels_at_risk = []
    total_value = 0
    
    for v_id, v in db_vessels.items():
        dist = haversine_distance(req.lat, req.lng, v["lat"], v["lng"])
        if dist <= req.radius:
            # Predict disruption probability
            prob = ml_engine.predict_disruption(
                congestion=random.uniform(0.5, 0.9),
                strike_prob=random.uniform(0.1, 0.4),
                weather=random.uniform(0.2, 0.6)
            )
            
            # Get recommendation
            rec = optimizer.calculate_resilience_strategy(
                current_route_risk=prob,
                alt_mode="AIR",
                cargo_priority="high" if v["sector"] in ["health", "energy"] else "normal",
                carbon_impact=0.15
            )
            
            v_data = {
                "id": v_id,
                "name": v["name"],
                "disruption_prob": prob,
                "recommendation": rec
            }
            vessels_at_risk.append(v_data)
            total_value += random.randint(1, 5) # Mock M$ values
            
    return {
        "zone": {"lat": req.lat, "lng": req.lng, "radius": req.radius},
        "vessels_at_risk_count": len(vessels_at_risk),
        "economic_impact_m_usd": total_value,
        "vessels": vessels_at_risk,
        "mitigation_strategy": "Switch critical high-priority shipments to AIR mode to avoid maritime delays."
    }

# --- New API Endpoints for Full Dashboard ---

@app.get("/api/intelligence")
def get_intelligence():
    """Returns a rich, multi-item stream of geopolitical risk events."""
    # Pick a few random vessels to "affect" with news
    vessel_ids = list(db_vessels.keys())
    affected_1 = db_vessels[vessel_ids[0]] if len(vessel_ids) > 0 else None
    affected_2 = db_vessels[vessel_ids[1]] if len(vessel_ids) > 1 else None
    
    return [
        {
            "id": 1, "type": "critical", "source": "GLOBAL INTEL", 
            "title": "Suez Canal Congestion: Geopolitical Tension increases in Red Sea sector.",
            "time": "APR 30 11:15", "affected_vessel": affected_1
        },
        {
            "id": 2, "type": "warning", "source": "LOGISTICS DAILY", 
            "title": "Semiconductor shortage predicted to impact Singapore hub in Q3.",
            "time": "APR 30 11:10", "affected_vessel": None
        },
        {
            "id": 3, "type": "info", "source": "SYSTEM MESH", 
            "title": "Global satellite network status: OPTIMAL. Latency: 14ms.",
            "time": "APR 30 11:05", "affected_vessel": None
        },
        {
            "id": 4, "type": "critical", "source": "MARITIME SEC", 
            "title": "Piracy Warning: High-speed craft sighted near Gulf of Aden.",
            "time": "APR 30 10:55", "affected_vessel": affected_2
        },
        {
            "id": 5, "type": "warning", "source": "REUTERS", 
            "title": "Fuel price volatility expected following OPEC+ production meeting.",
            "time": "APR 30 10:40", "affected_vessel": None
        },
        {
            "id": 6, "type": "info", "source": "PORT AUTHORITY", 
            "title": "Port of Rotterdam implementing AI-driven automated berth scheduling.",
            "time": "APR 30 10:25", "affected_vessel": None
        },
        {
            "id": 7, "type": "warning", "source": "METEO GLOBAL", 
            "title": "Approaching Typhoon: Vessels in North Pacific advised to adjust heading.",
            "time": "APR 30 10:15", "affected_vessel": None
        },
        {
            "id": 8, "type": "info", "source": "BLOOMBERG", 
            "title": "Global trade volume up 4.2% YoY; demand for aviation cargo surges.",
            "time": "APR 30 09:50", "affected_vessel": None
        },
        {
            "id": 9, "type": "critical", "source": "CYBER WATCH", 
            "title": "Cyber Alert: Ransomware attack reported on major freight forwarder.",
            "time": "APR 30 09:30", "affected_vessel": None
        },
        {
            "id": 10, "type": "info", "source": "RESILLIENT LOGIX", 
            "title": "System Update: Prescriptive Optimization Engine v4.2 deployed.",
            "time": "APR 30 09:00", "affected_vessel": None
        }
    ]

@app.get("/api/cascade/{vessel_id}")
def get_cascade_analysis(vessel_id: str):
    """Simulates the downstream impact based on the vessel's specific cargo and sector."""
    if vessel_id not in db_vessels:
        return {"vessel_id": vessel_id, "nodes": []}
    
    v = db_vessels[vessel_id]
    sector = v["sector"]
    cargo = v["cargo"]
    
    impact_map = {
        "energy": [
            {"name": f"Refinery Hub: {random.choice(['Rotterdam', 'Singapore', 'Houston'])}", "impact": random.choice(["Critical", "High"]), "delay": f"{random.randint(24, 72)}h"},
            {"name": "Industrial Grid Feed", "impact": "High", "delay": f"{random.randint(48, 96)}h"},
            {"name": "Consumer Heating Reserve", "impact": "Medium", "delay": "120h"}
        ],
        "health": [
            {"name": f"Regional Vaccine Depot: {random.choice(['Berlin', 'Mumbai', 'NYC'])}", "impact": "Life-Critical", "delay": f"{random.randint(12, 24)}h"},
            {"name": "Hospital Logistics Chain", "impact": random.choice(["High", "Critical"]), "delay": f"{random.randint(24, 48)}h"},
            {"name": "Pharmacy Stock replenishment", "impact": "Medium", "delay": "48h"}
        ],
        "industrial": [
            {"name": f"Assembly Plant: {random.choice(['Shenzhen', 'Detroit', 'Tokyo'])}", "impact": "High", "delay": f"{random.randint(72, 120)}h"},
            {"name": "Silicon Tier 2 Supplier", "impact": "Medium", "delay": f"{random.randint(96, 144)}h"},
            {"name": "Electronics Retail Inventory", "impact": "Low", "delay": "1 week"}
        ],
        "humanitarian": [
            {"name": f"Crisis Zone: {random.choice(['Sudan', 'Yemen', 'Ukraine'])}", "impact": "High", "delay": "24h"},
            {"name": "NGO Distribution Center", "impact": "Medium", "delay": "48h"},
            {"name": "Field Hospital Supplies", "impact": "High", "delay": f"{random.randint(36, 60)}h"}
        ]
    }
    
    return {
        "vessel_id": vessel_id,
        "cargo": cargo,
        "nodes": impact_map.get(sector, [
            {"name": "Global Distribution Hub", "impact": "Medium", "delay": "48h"}
        ])
    }

@app.get("/api/logs")
def get_system_logs():
    return [
        {"time": "00:00:01", "msg": "System Boot Sequence Complete"},
        {"time": "00:00:15", "msg": "Global Satellite Sync: 24/24 Online"},
        {"time": "00:01:42", "msg": "Heuristic Engine: Optimized for Safety"}
    ]

@app.get("/api/proposals")
def get_reroute_proposals():
    """Returns the list of generated reroute proposals from the latest simulation."""
    try:
        with open("scripts/reroute_proposals.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.get("/api/vessels/{vessel_id}/threat-scenarios")
def get_threat_scenarios(vessel_id: str):
    """Returns contextual threat scenarios for the selected vessel."""
    return [
        {"id": "piracy", "name": "Piracy Escalation", "severity": "critical", "description": "High-speed skiff activity detected in theater."},
        {"id": "storm", "name": "Regional Cyclone", "severity": "high", "description": "Severe weather conditions impacting shipping lanes."},
        {"id": "strike", "name": "Labor Strike", "severity": "medium", "description": "Port workers union announced industrial action."}
    ]

@app.post("/api/simulate-risk")
async def simulate_risk(data: dict):
    """Triggers a simulated risk event and generates mitigation proposals."""
    vessel_id = data.get("vessel_id")
    if vessel_id in db_vessels:
        db_vessels[vessel_id]["status"] = "at_risk"
        db_vessels[vessel_id]["last_risk"] = data.get("scenario_name", "Piracy Escalation")
        recalculate_proposals()
        await notify_clients(f"CRITICAL: {vessel_id} marked as AT_RISK due to {db_vessels[vessel_id]['last_risk']}")
    return {"status": "success", "message": f"Simulation active for {vessel_id}"}

@app.post("/api/execute-switch")
async def execute_switch(data: dict):
    """Authorizes an AI-proposed mode switch (e.g., Maritime to Aviation)."""
    v_id = data.get("vessel_id")
    if v_id in db_vessels:
        v = db_vessels[v_id]
        old_mode = v["type"]
        new_mode = "aviation" if old_mode == "maritime" else "maritime"
        
        # Apply the tactical switch
        v["type"] = new_mode
        v["status"] = "normal" # Threat mitigated
        
        # Update the route to a direct line to destination for the new mode
        dest_lat, dest_lng = HUBS[v["destination"]]
        mid_lat = (v["lat"] + dest_lat) / 2 + random.uniform(-5, 5)
        mid_lng = (v["lng"] + dest_lng) / 2 + random.uniform(-5, 5)
        v["route"] = [[mid_lat, mid_lng], [dest_lat, dest_lng]]
        
        recalculate_proposals() # Clear this vessel from the queue
        await notify_clients(f"ACTION: {v_id} authorized for {new_mode.upper()} transit.")
        
        try:
            with open("scripts/action_audit.log", "a") as f:
                f.write(f"{v_id}: Switched {old_mode} -> {new_mode} at {v['lat']},{v['lng']}\n")
        except Exception:
            pass
            
    return {"status": "success", "new_mode": new_mode, "message": f"Successfully switched {v_id} to {new_mode}"}

def recalculate_proposals():
    """Scans for at_risk vessels and generates JSON proposals with correct vessel_id linking."""
    new_proposals = []
    for v_id, v in db_vessels.items():
        if v["status"] == "at_risk":
            new_proposals.append({
                "shipment_id": f"{random.randint(1000, 9999)}",
                "vessel_id": v_id,
                "vessel": v["name"],
                "suggestion": "AUTHORIZE MODE SWITCH",
                "reason": v.get("last_risk", "AI-Predicted Structural Risk"),
                "cost_delta": random.randint(12000, 25000),
                "time_saved": f"{random.randint(48, 96)}h"
            })
    
    with open("scripts/reroute_proposals.json", "w") as f:
        json.dump(new_proposals, f, indent=4)

@app.get("/")
def read_root():
    return {"message": "ResilientLogix Full Simulation API is running"}
