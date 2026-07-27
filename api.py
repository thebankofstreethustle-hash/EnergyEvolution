"""
Waste Heat OS - FastAPI Wrapper
Run with: uvicorn api:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import random
from waste_heat_optimizer import WasteHeatOptimizer, ReactorState, HeatClient

app = FastAPI(title="Waste Heat OS API", version="0.1")

# In-memory clients (replace with DB later)
CLIENTS_DB = [
    HeatClient("farm1", "Chicken Farm - Mareetsane", 70, 15, 650, 3.2),
    HeatClient("green1", "Greenhouse Cluster - Jouberton", 55, 25, 480, 5.1),
    HeatClient("mine1", "Gold Mine Processing", 90, 120, 900, 8.5),
    HeatClient("heat1", "District Heating - Klerksdorp", 65, 40, 550, 12.0),
    HeatClient("desal1", "Desalination Pilot", 80, 30, 1100, 2.0),
]

class OptimizeRequest(BaseModel):
    thermal_mw: float = 3000
    electricity_price: float = 850  # R/MWh

@app.get("/")
def health():
    return {"status": "Waste Heat OS online", "reactor_thermal_mw": 3000}

@app.get("/clients")
def list_clients():
    return CLIENTS_DB

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # Simulate live electricity price if not provided
    elec_price = req.electricity_price if req.electricity_price else random.uniform(600, 1800)
    
    reactor = ReactorState(
        thermal_mw=req.thermal_mw,
        electricity_price_r_per_mwh=elec_price
    )
    optimizer = WasteHeatOptimizer(reactor, CLIENTS_DB)
    plan = optimizer.optimize()
    return plan

@app.post("/what-if/hydrogen")
def hydrogen_scenario():
    """
    What if we add a 100MW electrolyzer using waste heat?
    """
    # 100MW thermal at 80C can pre-heat water for electrolysis, saving ~10% electricity
    thermal_for_h2 = 100
    h2_saved_mw = thermal_for_h2 * 0.10
    h2_kg_per_hour = h2_saved_mw * 18  # ~18kg per MWh
    return {
        "scenario": "100MW waste heat to High-Temp Electrolysis",
        "thermal_used_mw": thermal_for_h2,
        "electricity_saved_mw": h2_saved_mw,
        "hydrogen_produced_kg_h": round(h2_kg_per_hour, 1),
        "value_r_per_h": round(h2_kg_per_hour * 75, 2)  # R75/kg green H2
    }

# For your React Native app, call /optimize every 30 seconds
# and animate the dispatch.
