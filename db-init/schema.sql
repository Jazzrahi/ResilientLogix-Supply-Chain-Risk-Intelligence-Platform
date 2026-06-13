-- Enable PostGIS extension for spatial capabilities
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Vessels Table
CREATE TABLE vessels (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- e.g., 'water', 'air', 'rail'
    location GEOGRAPHY(Point, 4326), -- PostGIS Spatial Column for lat/lng
    heading FLOAT,
    status VARCHAR(50) DEFAULT 'normal' -- 'normal', 'warning', 'critical', 'at_risk'
);

-- 2. Cargo Table
CREATE TABLE cargo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vessel_id VARCHAR(50) REFERENCES vessels(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL, -- e.g., 'Oil', 'Semiconductors', 'Vaccines'
    weight FLOAT NOT NULL, -- metric tons
    priority VARCHAR(50) DEFAULT 'standard' -- 'standard', 'high', 'critical'
);

-- 3. Routes Table
CREATE TABLE routes (
    vessel_id VARCHAR(50) PRIMARY KEY REFERENCES vessels(id) ON DELETE CASCADE,
    path GEOGRAPHY(LineString, 4326),
    alt_path GEOGRAPHY(LineString, 4326)
);

-- 4. Risk Events Table
CREATE TABLE risk_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_api VARCHAR(100),
    location GEOGRAPHY(Point, 4326),
    severity VARCHAR(50), -- 'low', 'medium', 'high', 'critical'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Support Assets Table (For Rescue Logic)
CREATE TABLE support_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    type VARCHAR(50), -- e.g., 'Rescue Tug', 'Cold Storage Hub'
    location GEOGRAPHY(Point, 4326)
);

-- 6. Spatial Trigger for 500km Radius Flagging
CREATE OR REPLACE FUNCTION flag_vessels_at_risk()
RETURNS TRIGGER AS $$
BEGIN
    -- Update status of vessels within 500km (500,000 meters) of the new risk event
    UPDATE vessels
    SET status = 'at_risk'
    WHERE ST_DWithin(location, NEW.location, 500000);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_flag_vessels
AFTER INSERT ON risk_events
FOR EACH ROW
EXECUTE FUNCTION flag_vessels_at_risk();
