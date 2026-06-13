import os
import asyncio
import httpx
import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://resilient_user:resilient_password@localhost:5432/resilientlogix")

async def fetch_gdacs_events():
    """
    Fetches real-time disaster alerts from the Global Disaster Alert and Coordination System (GDACS).
    Parses the RSS feed and inserts critical events into the PostGIS risk_events table.
    """
    url = "https://www.gdacs.org/xml/rss.xml"
    print(f"Fetching real-time disaster data from GDACS: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code != 200:
                print("Failed to fetch GDACS data.")
                return []
            
            root = ET.fromstring(response.content)
            events = []
            
            # GDACS RSS has items inside channel
            for item in root.findall('./channel/item'):
                title = item.find('title').text if item.find('title') is not None else 'Unknown Event'
                desc = item.find('description').text if item.find('description') is not None else ''
                
                # GDACS uses georss:point for coordinates "lat lng"
                geo_point = item.find('{http://www.georss.org/georss}point')
                if geo_point is not None and geo_point.text:
                    lat_str, lng_str = geo_point.text.split()
                    lat, lng = float(lat_str), float(lng_str)
                    
                    # Determine severity based on title or GDACS alert level
                    severity = 'medium'
                    if 'Red' in title or 'Orange' in title:
                        severity = 'critical'
                    elif 'Earthquake' in title or 'Cyclone' in title:
                        severity = 'high'
                        
                    events.append({
                        "source": "GDACS API",
                        "title": title,
                        "description": desc,
                        "lat": lat,
                        "lng": lng,
                        "severity": severity
                    })
            return events[:5] # Return top 5 recent events
    except Exception as e:
        print(f"Error fetching GDACS: {e}")
        return []

def update_database_risks(events):
    """
    Inserts fetched risk events into the database.
    This will automatically trigger the PostGIS spatial trigger `flag_vessels_at_risk()`.
    """
    if not events:
        print("No new events to process.")
        return
        
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        for event in events:
            # Check if we already inserted a similar event recently to avoid spam
            check_sql = text("SELECT COUNT(*) FROM risk_events WHERE description = :desc")
            count = conn.execute(check_sql, {"desc": event["description"]}).scalar()
            
            if count == 0:
                print(f"Inserting New Risk Event: {event['title']} at ({event['lat']}, {event['lng']})")
                insert_sql = text("""
                    INSERT INTO risk_events (source_api, location, severity, description)
                    VALUES (:source, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :severity, :desc)
                """)
                conn.execute(insert_sql, {
                    "source": event["source"],
                    "lng": event["lng"],
                    "lat": event["lat"],
                    "severity": event["severity"],
                    "desc": event["title"]
                })
        
        # Now count how many vessels were flagged by the PostGIS trigger
        count_sql = text("SELECT COUNT(*) FROM vessels WHERE status = 'at_risk'")
        at_risk_count = conn.execute(count_sql).scalar()
        print(f"PostGIS Spatial Trigger executed. Total vessels currently 'at_risk': {at_risk_count}")

async def run_live_feed():
    print("--- Starting Live Data Feeder ---")
    events = await fetch_gdacs_events()
    update_database_risks(events)
    print("--- Feeder Cycle Complete ---")

if __name__ == "__main__":
    asyncio.run(run_live_feed())
