# ResilientLogix: Global Supply Chain Risk Intelligence Platform

ResilientLogix is an enterprise-grade, real-time supply chain risk mitigation platform. It integrates a **PostgreSQL/PostGIS spatial database**, a **FastAPI backend with a prescriptive AI/ML optimization engine**, and a **sleek, glassmorphic React/Tailwind dashboard** to visualize global fleet positions, track live hazards, and calculate multi-modal alternative routes (Sea-to-Air switches) to safeguard critical shipments.

---

## 🖥️ Visual Preview

![ResilientLogix Dashboard Preview](docs/dashboard_preview.png)

---

## 🚀 Key Features

### 1. **AI Prescriptive & Optimization Engine**
* **Dynamic Multi-Modal Rerouting**: Resolves route interruptions by recommending alternative transport modes (e.g., Sea to Air) utilizing cargo priority, carbon footprint data, and safety-to-cost indexes.
* **ML Disruption Severity Predictor**: Runs real-time machine learning predictions on disruption probabilities using key variables like local port congestion, strikes, and weather patterns.

### 2. **Advanced Spatial Database (PostGIS)**
* **Real-time Spatial Triggers**: Utilizes PL/pgSQL database triggers to automatically scan and flag cargo vessels inside a **500km radius** (`ST_DWithin` on SRID 4326) of any newly registered natural disaster or geopolitical threat.
* **Geographical Models**: Structured tables for `vessels`, `cargo`, `routes`, `risk_events`, and `support_assets` featuring PostGIS spatial geography geometry.

### 3. **Live Telemetry & Geopolitical Ingestion**
* **GDACS Ingestor**: Connects directly to the Global Disaster Alert and Coordination System API to feed live earthquakes, cyclones, and floods into the spatial risk engine.
* **OpenSky Network Integration**: Pulls live aviation callsigns, headings, and coordinates to track airborne flights in real-time.
* **Great-Circle Maritime Physics**: Custom-engineered simulation engine calculates spherical bearings and simulates vessel coordinates dynamically.

### 4. **Modern Glassmorphic Frontend Dashboard**
* **Sleek Dark Mode UI**: Custom-themed interactive dashboards that shift colors dynamically based on the active sector (Energy, Health, Industrial, Humanitarian).
* **Interactive Global Map**: Full geographic overlay map rendering active vessels, danger zones, simulated storm radii, and real-time routes.
* **Downstream Cascade Impact Visualizer**: Shows direct downstream nodes (depots, refineries, and assembly plants) affected by a late shipment.
* **Aggregated Command Log**: Simulates an automated operations terminal logging system actions.

---

## 🛠️ Technology Stack

| Component | Technologies Used |
| :--- | :--- |
| **Frontend** | React, Vite, Tailwind CSS, Leaflet Maps, Lucide Icons |
| **Backend** | FastAPI (Python), Pandas, Pydantic, SQLAlchemy, Geopy, Feedparser |
| **Database** | PostgreSQL + PostGIS (Spatial Database Extension) |
| **Infrastructure** | Docker, Docker Compose |

---

## ⚙️ Project Architecture

```mermaid
graph TD
    A[GDACS & OpenSky APIs] -->|Live Ingestion| B(FastAPI Backend)
    B -->|SQLAlchemy ORM| C[(PostgreSQL + PostGIS)]
    C -->|PL/pgSQL Trigger: 500km Risk Check| C
    B -->|Machine Learning Engine| B
    B -->|WebSocket Telemetry: 1s ticks| D[React Frontend]
    D -->|Simulate Danger Zone/Reroute| B
```

---

## 📋 Installation & Running Guide

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Recommended)
* [Node.js](https://nodejs.org/) (v16+ for local frontend development)

---

### Option A: Complete Docker Compose Run (Recommended)
This runs the PostGIS database and the FastAPI Backend in containers automatically.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Jazzrahi/ResilientLogix-Supply-Chain-Risk-Intelligence-Platform.git
   cd ResilientLogix-Supply-Chain-Risk-Intelligence-Platform
   ```

2. **Start the containers**:
   ```bash
   docker-compose up --build
   ```

3. **Database Initialization**:
   The database container automatically loads `db-init/schema.sql` on startup to prepare tables, spatial geography columns, and trigger functions.

4. **Run the Frontend locally**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open your browser and navigate to `http://localhost:5173`.

---

### Option B: Local Development Run (Manual Setup)

#### 1. Setup Database
1. Spin up a Postgres database and run the `CREATE EXTENSION postgis;` command.
2. Initialize tables by executing the SQL script:
   ```bash
   psql -U your_user -d your_db -f db-init/schema.sql
   ```

#### 2. Run the Python Backend
1. Navigate to the backend directory and set up a virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Database Environment variable:
   ```bash
   export DATABASE_URL="postgresql://your_user:your_password@localhost:5432/your_db"
   ```
4. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The backend will be running at `http://localhost:8000`.

#### 3. Run the React Frontend
1. Open a new terminal window, navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Open `http://localhost:5173` to see the live system.

---

## 📂 Codebase Directory Structure

```text
├── backend/
│   ├── main.py                # Core FastAPI app with endpoints, WebSockets, & event loop
│   ├── Dockerfile             # Container configuration for Python backend
│   ├── requirements.txt       # Backend dependencies
│   ├── services/
│   │   ├── ml_engine.py       # Disruption and risk probability ML model logic
│   │   ├── optimizer.py       # Multi-modal routing cost/time optimization formulas
│   │   └── live_feed.py       # Google News, OpenSky, and GDACS ingestion service
│   └── scripts/
│       └── seed_data.py       # Initial mock data and SQL views simulator
├── db-init/
│   └── schema.sql             # SQL Schema containing PostGIS tables and spatial triggers
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main dashboard manager and tab states
│   │   ├── components/
│   │   │   ├── MapComponent.jsx       # Interactive Leaflet visual world theater
│   │   │   └── DashboardComponents.jsx # Glassmorphic UI panels and controls
│   │   └── index.css          # Tailwind CSS global design system and panels
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
└── docker-compose.yml         # Dev environment container orchestrator
```

---

## 🛡️ License
This project is licensed under the MIT License.
