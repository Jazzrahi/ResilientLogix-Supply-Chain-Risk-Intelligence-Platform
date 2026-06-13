import os
import math
import asyncio
import feedparser
from datetime import datetime
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

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

# --- Vast Global Fleet Data Library ---
MARITIME_NAMES = [
    "MSC Oscar", "Maersk Mc-Kinney Moller", "CMA CGM Marco Polo", "COSCO Shipping Universe", "Ever Given",
    "HMM Algeciras", "OOCL Hong Kong", "MOL Triumph", "Madrid Maersk", "MSC Gulsun", "Triton Maersk",
    "MSC Anna", "CMA CGM Antoine de Saint Exupery", "ONE Trust", "Ever Ace", "HMM Oslo", "MSC Amelia",
    "Maersk Essen", "CSCL Globe", "Barzan", "Al Zubara", "CMA CGM Jean Mermoz", "Ever Goods", "MSC Jade",
    "Cosco Shipping Leo", "MOL Truth", "Munich Maersk", "MSC Mirjam", "Ever Golden", "Maersk Edirne"
]

AVIATION_NAMES = [
    "Emirates Cargo EK902", "Qatar Airways QR8155", "Lufthansa Cargo LH8401", "FedEx Express FX32",
    "UPS Airlines 5X61", "DHL Air UK D0701", "Cathay Pacific CX2043", "Singapore Airlines Cargo SQ73",
    "Cargolux CV842", "Atlas Air 5Y401", "Korean Air Cargo KE274", "Asiana Cargo OZ987",
    "Turkish Cargo TK632", "Nippon Cargo KZ121", "China Airlines CI588", "Polar Air Cargo PO711"
]

CARGO_TYPES = {
    "energy": ["Crude Oil (Grade A)", "Liquefied Natural Gas", "Refined Petroleum", "Solar Panel Arrays", "Wind Turbine Blades"],
    "health": ["COVID-19 Vaccines", "Insulin Refrigerated Units", "Surgical Robots", "Diagnostic Lab Supplies", "Blood Plasma"],
    "industrial": ["Microchips (3nm)", "Automotive Engine Blocks", "Industrial Steel Coils", "Heavy Machinery Parts", "Lithium-Ion Batteries"],
    "humanitarian": ["Emergency Rations", "Portable Water Purifiers", "Field Hospital Tents", "Cold-Weather Blankets", "Medical Aid Kits"]
}

def generate_fleet(count=150):
    sectors = ["energy", "health", "industrial", "humanitarian"]
    
    for i in range(count):
        # Explicitly assign types: 40% aviation, 60% maritime
        v_type = "aviation" if random.random() > 0.6 else "maritime"
        prefix = "A" if v_type == "aviation" else "M"
        v_id = f"{prefix}-{1000 + i}"
        sector = random.choice(sectors)
        
        if v_type == "maritime":
            v_name = f"{random.choice(MARITIME_NAMES)} ({random.randint(100, 999)})"
        else:
            v_name = f"{random.choice(AVIATION_NAMES)} - {random.choice(['Alpha', 'Bravo', 'Echo'])}"
            
        cargo = random.choice(CARGO_TYPES[sector])
        priority = random.choice(["standard", "high", "critical"])
        
        hub_names = list(HUBS.keys())
        origin = random.choice(hub_names)
        dest = random.choice([h for h in hub_names if h != origin])
        
        # Start near the origin
        o_lat, o_lng = HUBS[origin]
        lat = o_lat + random.uniform(-4, 4)
        lng = o_lng + random.uniform(-4, 4)
        
        db_vessels[v_id] = {
            "id": v_id,
            "name": v_name,
            "type": v_type,
            "sector": sector,
            "cargo": cargo,
            "priority": priority,
            "lat": lat,
            "lng": lng,
            "heading": random.randint(0, 360),
            "status": "normal",
            "origin": origin,
            "destination": dest,
            "route": []
        }

generate_fleet(150)

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
            
            if dist_to_dest < 50:
                # Arrived! Pick a new random destination
                hub_names = list(HUBS.keys())
                v["origin"] = v["destination"]
                v["destination"] = random.choice([h for h in hub_names if h != v["origin"]])
                dest_lat, dest_lng = HUBS[v["destination"]]
                v["route"] = None # Clear old route for new destination
            
            # Calculate heading towards destination
            v["heading"] = calculate_initial_compass_bearing((v["lat"], v["lng"]), (dest_lat, dest_lng))
            
            # Only set default route if no custom route exists
            if not v.get("route"):
                v["route"] = [[dest_lat, dest_lng]]
            
            if v["type"] == "maritime":
                try:
                    # Move 10km per tick (Visibly fast at global scale)
                    current_point = (v["lat"], v["lng"])
                    dest = geodesic(kilometers=10.0).destination(current_point, v["heading"])
                    v["lat"], v["lng"] = dest.latitude, dest.longitude
                except Exception:
                    pass
            else:
                # Aviation move 40km per tick (Visibly fast at global scale)
                try:
                    current_point = (v["lat"], v["lng"])
                    dest = geodesic(kilometers=40.0).destination(current_point, v["heading"])
                    v["lat"], v["lng"] = dest.latitude, dest.longitude
                except Exception:
                    pass
                
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
    
    # Generate dynamic scores based on vessel properties
    # This simulates a real calculation instead of returning hardcoded 95, 90, 40
    
    # Air vs Sea base profiles
    is_maritime = v["type"] == "maritime"
    
    # Option 1: AI Optimized Path
    # If recommended is AIR: high safety, high time, low cost (relatively)
    # If recommended is SEA: medium safety, low time, high cost (relatively)
    
    seed = sum(ord(c) for c in vessel_id) # Consistent jitter per vessel
    random.seed(seed)
    
    potential_routes = []
    
    # Primary AI Recommendation
    rec_mode = rec["recommended_path"].lower()
    if rec_mode == "air":
        safety = random.randint(88, 98)
        time = random.randint(85, 95)
        cost = random.randint(30, 50)
    else:
        safety = random.randint(70, 85)
        time = random.randint(40, 60)
        cost = random.randint(80, 95)
        
    potential_routes.append({
        "mode": rec_mode, 
        "safety": safety, 
        "time": time, 
        "cost": cost, 
        "name": f"AI Optimized {rec['recommended_path']} Link"
    })
    
    # Alternate Option
    alt_mode = "sea" if rec_mode == "air" else "air"
    if alt_mode == "air":
        safety = random.randint(85, 95)
        time = random.randint(80, 90)
        cost = random.randint(20, 45)
    else:
        safety = random.randint(50, 75)
        time = random.randint(30, 55)
        cost = random.randint(70, 90)
        
    potential_routes.append({
        "mode": alt_mode, 
        "safety": safety, 
        "time": time, 
        "cost": cost, 
        "name": "Standard Alternate"
    })
        
    for route in potential_routes:
        route["score"] = round((0.4 * route["safety"]) + (0.3 * route["time"]) + (0.3 * route["cost"]), 2)
        
    potential_routes.sort(key=lambda x: x["score"], reverse=True)
    
    # Reset random seed for other parts of the app
    random.seed(None)
    
    return {
        "vessel_id": vessel_id,
        "recommended_route": potential_routes[0],
        "all_options": potential_routes,
        "ai_analysis": rec
    }

# --- Intelligence Ingestion Service ---

@app.get("/api/vessels/{vessel_id}/threat-scenarios")
def get_threat_scenarios(vessel_id: str):
    if vessel_id not in db_vessels:
        raise HTTPException(status_code=404, detail="Vessel not found")
    
    v = db_vessels[vessel_id]
    lat, lng = v["lat"], v["lng"]
    
    # Contextual logic based on region
    scenarios = []
    
    # Geographic region detection
    is_arctic = lat > 65
    is_middle_east = lat > 10 and lat < 35 and lng > 35 and lng < 65
    is_se_asia = lat > -10 and lat < 25 and lng > 95 and lng < 130
    is_africa = lat > -35 and lat < 35 and lng > -20 and lng < 55
    is_americas = lng < -30
    
    if v["type"] == "aviation":
        scenarios = [
            {"id": "cyclone", "name": "Severe Cyclonic Storm Detection", "severity": "critical"},
            {"id": "volcano", "name": "Volcanic Ash Cloud Eruption", "severity": "high"},
            {"id": "geopolitics", "name": "No-Fly Zone Enforcement", "severity": "critical"},
            {"id": "gps", "name": "Satellite GNSS Jamming Event", "severity": "high"},
            {"id": "fuel", "name": "Regional Aviation Fuel Shortage", "severity": "medium"}
        ]
    else:
        if is_arctic:
            scenarios = [
                {"id": "ice", "name": "Rapid Arctic Ice Sheet Encroachment", "severity": "critical"},
                {"id": "fog", "name": "Zero-Visibility Ice Fog Front", "severity": "high"},
                {"id": "radar", "name": "Magnetospheric Interference (Radar Fail)", "severity": "medium"}
            ]
        elif is_middle_east:
            scenarios = [
                {"id": "piracy", "name": "High-Risk Piracy Activity (Gulf of Aden)", "severity": "critical"},
                {"id": "naval", "name": "Naval Military Exercise Zone", "severity": "medium"},
                {"id": "blockade", "name": "Strategic Strait Blockade", "severity": "critical"}
            ]
        elif is_se_asia:
            scenarios = [
                {"id": "typhoon", "name": "Super Typhoon Category 5 Warning", "severity": "critical"},
                {"id": "dispute", "name": "Territorial Waters Sovereign Dispute", "severity": "high"},
                {"id": "congestion", "name": "Malacca Strait Super-Congestion", "severity": "medium"}
            ]
        elif is_africa:
            scenarios = [
                {"id": "port", "name": "Critical Infrastructure Grid Failure", "severity": "high"},
                {"id": "strike", "name": "Pan-African Logistics Labor Strike", "severity": "medium"},
                {"id": "ebola", "name": "Quarantine-Induced Port Closure", "severity": "critical"}
            ]
        elif is_americas:
            scenarios = [
                {"id": "hurricane", "name": "Atlantic Hurricane Path Intersection", "severity": "critical"},
                {"id": "canal", "name": "Panama Canal Drought Draft Restriction", "severity": "high"},
                {"id": "customs", "name": "Automated Customs System Outage", "severity": "medium"}
            ]
        else:
            scenarios = [
                {"id": "storm", "name": "Deep Ocean Severe Weather Front", "severity": "high"},
                {"id": "spill", "name": "Major Container Spill & Containment", "severity": "critical"},
                {"id": "whale", "name": "Marine Sanctuary Speed Restriction", "severity": "low"}
            ]
    return scenarios

class RiskSimulationRequest(BaseModel):
    vessel_id: str
    scenario_id: str
    scenario_name: str

@app.post("/api/execute-switch")
async def execute_switch(req: dict):
    v_id = req.get("vessel_id")
    if not v_id or v_id not in db_vessels:
        raise HTTPException(status_code=404, detail="Vessel not found")
    
    v = db_vessels[v_id]
    new_mode = "maritime" if v["type"] == "aviation" else "aviation"
    v["type"] = new_mode
    v["status"] = "normal"
    
    # Generate a more "calculated" route with intermediate waypoints
    dest_lat, dest_lng = HUBS[v["destination"]]
    mid_lat = (v["lat"] + dest_lat) / 2 + random.uniform(-5, 5)
    mid_lng = (v["lng"] + dest_lng) / 2 + random.uniform(-5, 5)
    
    v["route"] = [[mid_lat, mid_lng], [dest_lat, dest_lng]]
    
    # Log the action
    new_log = {
        "time": pd.Timestamp.now().strftime("%H:%M:%S"),
        "msg": f"OPTIMIZER: {v_id} switched to {new_mode.upper()} mode. Rerouting via waypoint grid."
    }
    
    # We can append to system logs if we had a persistent list, but here we just return success
    await notify_clients(f'{{"type": "ACTION_LOG", "message": "{new_log["msg"]}"}}')
    
    # Remove from proposals file so it doesn't reappear on refresh
    try:
        with open("scripts/reroute_proposals.json", "r") as f:
            proposals = json.load(f)
        proposals = [p for p in proposals if p.get("vessel_id") != v_id]
        with open("scripts/reroute_proposals.json", "w") as f:
            json.dump(proposals, f)
    except Exception:
        pass
    
    # Force immediate broadcast to UI for instant feedback
    await broadcast_vessel_state()
    
    return {"status": "success", "new_mode": new_mode, "message": f"Successfully switched {v_id} to {new_mode}"}

def recalculate_proposals():
    """Scans all 'at_risk' nodes and generates unique AI proposals for each."""
    proposals = []
    for v_id, v in db_vessels.items():
        if v["status"] == "at_risk":
            # Use ML engine to predict disruption severity
            risk_prob = ml_engine.predict_disruption(
                congestion=random.uniform(0.6, 0.9),
                strike_prob=0.5,
                weather=0.6
            )
            
            # Use Optimizer to get strategy
            rec = optimizer.calculate_resilience_strategy(
                current_route_risk=0.8, # High risk if flagged
                alt_mode="AIR" if v["type"] == "maritime" else "SEA",
                cargo_priority=v["priority"],
                carbon_impact=0.15
            )
            
            proposals.append({
                "shipment_id": f"SHP-{v_id}",
                "vessel_id": v_id,
                "vessel": v["name"],
                "reason": v.get("last_risk", "AI-Predicted Structural Risk"),
                "time_saved": f"{rec['time_saved']}h",
                "cost_delta": rec["estimated_cost_delta"],
                "confidence": rec["confidence_score"]
            })
            
    os.makedirs("scripts", exist_ok=True)
    with open("scripts/reroute_proposals.json", "w") as f:
        json.dump(proposals, f)

@app.post("/api/simulate-risk")
async def simulate_risk(req: RiskSimulationRequest):
    if req.vessel_id not in db_vessels:
        raise HTTPException(status_code=404, detail="Vessel not found")
        
    v = db_vessels[req.vessel_id]
    
    # Calculate a point slightly ahead of the vessel (e.g. 50km in its current heading)
    try:
        current_point = (v["lat"], v["lng"])
        dest = geodesic(kilometers=50).destination(current_point, v["heading"] if v.get("heading") else 0)
        risk_lat, risk_lng = dest.latitude, dest.longitude
    except Exception:
        risk_lat, risk_lng = v["lat"] + 0.5, v["lng"] + 0.5 # fallback
    
    v["status"] = "at_risk"
    v["last_risk"] = req.scenario_name
    
    # Notify clients to draw the danger zone
    await notify_clients(f'{{"type": "NEW_RISK_EVENT", "scenario": "{req.scenario_name}", "lat": {risk_lat}, "lng": {risk_lng}, "vessel_id": "{req.vessel_id}"}}')
    
    # Run the global node-wise scan
    recalculate_proposals()
        
    return {"status": "success", "message": f"Simulated {req.scenario_name} for {v['name']}. Node-wise proposals generated."}

@app.get("/api/live-news")
async def get_live_news():
    """Fetches real-time supply chain news from Google News RSS."""
    # Using 'when:1d' to force latest 24 hours news for a 'live' feel
    url = "https://news.google.com/rss/search?q=supply+chain+logistics+global+trade+when:1d&hl=en-US&gl=US&ceid=US:en"
    
    # We use a thread to avoid blocking the async loop for network I/O
    loop = asyncio.get_event_loop()
    feed = await loop.run_in_executor(None, feedparser.parse, url)
    
    news_items = []
    for entry in feed.entries[:10]: # Top 10 items
        title_lower = entry.title.lower()
        news_type = "normal"
        if any(w in title_lower for w in ["crisis", "shortage", "blockade", "strike", "critical", "danger", "conflict", "disruption"]):
            news_type = "critical"
        elif any(w in title_lower for w in ["warning", "delay", "congestion", "risk", "impact", "threat"]):
            news_type = "warning"
            
        # Parse time
        try:
            time_str = entry.published
        except:
            time_str = "Live"

        # Link to a vessel if possible for the demo
        affected_vessel = None
        
        # Expanded keywords for better matching
        sector_keywords = {
            "energy": ["energy", "oil", "gas", "fuel", "power", "petroleum", "electricity"],
            "health": ["health", "medical", "vaccine", "pharma", "hospital", "clinic", "medicine"],
            "industrial": ["industrial", "factory", "manufacturing", "steel", "automotive", "microchip", "tech"],
            "humanitarian": ["humanitarian", "aid", "relief", "food", "famine", "disaster", "refugee"]
        }
        
        for v_id, v in db_vessels.items():
            # Check vessel name
            if v["name"].lower() in title_lower:
                affected_vessel = {"id": v_id, "name": v["name"], "type": v["type"]}
                break
            
            # Check expanded sector keywords
            keywords = sector_keywords.get(v["sector"].lower(), [])
            if any(kw in title_lower for kw in keywords):
                affected_vessel = {"id": v_id, "name": v["name"], "type": v["type"]}
                break

        news_items.append({
            "id": entry.get("id", random.randint(1000, 9999)),
            "source": entry.get("source", {"title": "GLOBAL TRADE"}).get("title", "GLOBAL TRADE"),
            "time": time_str,
            "title": entry.title,
            "type": news_type,
            "url": entry.link,
            "affected_vessel": affected_vessel
        })
    return news_items

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
            db_vessels[v_id]["last_risk"] = "Red Sea Maritime Blockade"
            flagged_count += 1
    
    recalculate_proposals()
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
    """Returns the latest geopolitical risk events."""
    return [
        {"id": 1, "level": "CRITICAL", "source": "REUTERS", "msg": "Suez Canal congestion increasing due to Red Sea security protocol."},
        {"id": 2, "level": "WARNING", "source": "BLOOMBERG", "msg": "Semiconductor shortage predicted for Q3 in automotive sector."},
        {"id": 3, "level": "NORMAL", "source": "LLOYDS", "msg": "New arctic route trial successful for non-hazardous cargo."}
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

@app.get("/")
def read_root():
    return {"message": "ResilientLogix Full Simulation API is running"}
