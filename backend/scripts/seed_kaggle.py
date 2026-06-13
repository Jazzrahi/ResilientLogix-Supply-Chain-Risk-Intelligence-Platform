import os
import pandas as pd
import random
from sqlalchemy import create_engine, text

# Use localhost if running locally, or db if running inside docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://resilient_user:resilient_password@localhost:5432/resilientlogix")

def seed_database():
    print(f"Connecting to database at {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    csv_path = os.path.join(os.path.dirname(__file__), "mock_supply_chain_data.csv")
    print(f"Reading Kaggle dataset from {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("CSV file not found. Make sure mock_supply_chain_data.csv exists.")
        return
        
    # Get unique vessels from dataset
    unique_vessels = df['vessel_name'].unique()
    
    # Hub coordinates to assign random starting locations
    HUBS = {
        "Rotterdam": (51.92, 4.48),
        "Shanghai": (31.23, 121.47),
        "Jebel Ali": (25.0, 55.0),
        "Singapore": (1.35, 103.81),
        "Busan": (35.10, 129.04),
        "Felixstowe": (51.96, 1.35),
        "Hamburg": (53.55, 9.99),
        "Valencia": (39.47, -0.38),
        "Antwerp": (51.22, 4.40),
        "Port Klang": (3.00, 101.40)
    }
    
    with engine.begin() as conn:
        print("Clearing existing data...")
        conn.execute(text("TRUNCATE TABLE cargo CASCADE;"))
        conn.execute(text("TRUNCATE TABLE vessels CASCADE;"))
        conn.execute(text("TRUNCATE TABLE risk_events CASCADE;"))
        
        print("Inserting Vessels...")
        vessel_mapping = {}
        for idx, v_name in enumerate(unique_vessels):
            v_id = f"V-MAR-{1000 + idx}"
            vessel_mapping[v_name] = v_id
            
            # Pick a random hub as starting point
            hub_name = random.choice(list(HUBS.keys()))
            lat, lng = HUBS[hub_name]
            # Add slight jitter to location
            lat += random.uniform(-0.5, 0.5)
            lng += random.uniform(-0.5, 0.5)
            
            heading = random.uniform(0, 360)
            v_type = "water"
            
            insert_vessel_sql = text("""
                INSERT INTO vessels (id, name, type, location, heading, status) 
                VALUES (:id, :name, :type, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :heading, 'normal')
            """)
            conn.execute(insert_vessel_sql, {
                "id": v_id, 
                "name": v_name, 
                "type": v_type, 
                "lng": lng, 
                "lat": lat, 
                "heading": heading
            })
            
        print("Inserting Cargo...")
        for _, row in df.iterrows():
            v_id = vessel_mapping[row['vessel_name']]
            c_type = f"{row['sector']} - {row['origin']} to {row['destination']}"
            weight = float(row['weight_kg']) / 1000.0 # Convert to metric tons
            priority = row['priority'] # standard, high, critical
            if priority == "normal": priority = "standard"
            
            insert_cargo_sql = text("""
                INSERT INTO cargo (vessel_id, type, weight, priority)
                VALUES (:v_id, :type, :weight, :priority)
            """)
            conn.execute(insert_cargo_sql, {
                "v_id": v_id,
                "type": c_type,
                "weight": weight,
                "priority": priority
            })
            
        # Add a couple of Aviation vessels representing OpenSky/Cargo flights
        print("Inserting sample Aviation Vessels...")
        for i in range(3):
            v_id = f"V-AIR-{5000 + i}"
            hub_name = random.choice(["Shanghai", "Rotterdam", "Jebel Ali"])
            lat, lng = HUBS[hub_name]
            
            conn.execute(text("""
                INSERT INTO vessels (id, name, type, location, heading, status) 
                VALUES (:id, :name, 'air', ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :heading, 'normal')
            """), {
                "id": v_id,
                "name": f"AeroLogistics Flight {random.randint(100,999)}",
                "lng": lng,
                "lat": lat,
                "heading": random.uniform(0, 360)
            })
            
            conn.execute(text("""
                INSERT INTO cargo (vessel_id, type, weight, priority)
                VALUES (:v_id, 'Medical Supplies (COVID-19 Relief)', 45.5, 'critical')
            """), {"v_id": v_id})
            
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
