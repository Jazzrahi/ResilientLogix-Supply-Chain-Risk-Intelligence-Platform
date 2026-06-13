import sys
import os
import httpx
import asyncio
import json

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ml_engine import ml_engine
from services.optimizer import optimizer

async def simulate_red_sea_crisis():
    print("--- STARTING RED SEA CRISIS SIMULATION ---")
    
    # 1. Update risk status in simulation (Mock API call)
    print("[1] Triggering High-Severity Zone: Red Sea (15.0, 41.0)")
    
    # We'll simulate fetching shipments from our mock "Kaggle" data
    try:
        import pandas as pd
        df = pd.read_csv("scripts/mock_supply_chain_data.csv")
    except FileNotFoundError:
        print("Error: Mock Kaggle data not found. Run seed_data.py first.")
        return

    # 2. Trigger ML Engine to find all shipments with priority == 'high'
    high_priority = df[df['priority'] == 'high']
    print(f"[2] Identified {len(high_priority)} High-Priority Shipments (Energy/Health)")

    proposals = []
    
    # 3. Generate Reroute Proposals
    for _, row in high_priority.iterrows():
        # Predict disruption prob (simulated high for Red Sea)
        prob = 0.85 
        
        # Calculate strategy
        rec = optimizer.calculate_resilience_strategy(
            current_route_risk=prob,
            alt_mode="AIR",
            cargo_priority="high",
            carbon_impact=0.2
        )
        
        if rec["recommended_path"] == "AIR":
            proposal = {
                "shipment_id": row["shipment_id"],
                "vessel": row["vessel_name"],
                "suggestion": "SWITCH MODE TO AIR",
                "reason": "Red Sea Blockade High Risk",
                "cost_delta": rec["estimated_cost_delta"],
                "time_saved": f"{rec['time_saved']}h"
            }
            proposals.append(proposal)
            print(f"   [PROPOSAL] {row['shipment_id']}: {proposal['suggestion']} (Save {proposal['time_saved']})")

    # 4. Save results to a 'Reroute Proposal' table (Mocked as JSON)
    with open("scripts/reroute_proposals.json", "w") as f:
        json.dump(proposals, f, indent=4)
    
    print(f"--- SIMULATION COMPLETE. {len(proposals)} Reroute Proposals Generated. ---")

if __name__ == "__main__":
    asyncio.run(simulate_red_sea_crisis())
