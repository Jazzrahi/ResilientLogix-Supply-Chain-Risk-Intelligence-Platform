import pandas as pd
import random
import uuid

def generate_mock_kaggle_data(num_records=100):
    ship_names = ["Maersk Triple-E", "MSC Oscar", "CMA CGM Marco Polo", "Ever Given", "OOCL Hong Kong"]
    origins = ["Shanghai", "Singapore", "Jebel Ali", "Busan", "Port Klang"]
    destinations = ["Rotterdam", "Hamburg", "Antwerp", "Felixstowe", "Valencia"]
    
    data = []
    for _ in range(num_records):
        sector = random.choice(["Energy", "Health", "Industrial", "Consumer", "Humanitarian"])
        # Logic: 10% assigned to Critical (Health/Energy)
        priority = "high" if sector in ["Health", "Energy"] else "normal"
        
        record = {
            "shipment_id": str(uuid.uuid4())[:8],
            "vessel_name": random.choice(ship_names),
            "weight_kg": random.randint(5000, 200000),
            "origin": random.choice(origins),
            "destination": random.choice(destinations),
            "sector": sector,
            "priority": priority,
            "current_mode": "Sea",
            "budget": random.randint(10000, 50000)
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    # Save to a local CSV to simulate the Kaggle file
    df.to_csv("scripts/mock_supply_chain_data.csv", index=False)
    print(f"Seeded {num_records} shipments. 10% assigned to Critical sectors.")

if __name__ == "__main__":
    generate_mock_kaggle_data()
