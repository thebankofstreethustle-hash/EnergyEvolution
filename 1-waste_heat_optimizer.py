"""
Waste Heat OS - Core Optimization Engine
Solves: Maximize revenue from Thermal Power = Electricity + Heat products
"""

from dataclasses import dataclass
from typing import List, Dict
import random
from datetime import datetime

@dataclass
class HeatClient:
    id: str
    name: str
    temp_required_c: float  # Client needs this temp
    mw_demand: float        # How much heat they want
    price_per_mwh: float    # What they pay (R/MWh)
    distance_km: float
    co2_factor: float = 0.2  # tons CO2 saved per MWh vs LPG/diesel

@dataclass
class ReactorState:
    thermal_mw: float = 3000.0
    max_electric_mw: float = 1020.0
    electricity_price_r_per_mwh: float = 850.0  # Eskom price
    condenser_temp_c: float = 35.0

class WasteHeatOptimizer:
    def __init__(self, reactor: ReactorState, clients: List[HeatClient]):
        self.reactor = reactor
        self.clients = clients
        # Heat loss over distance: ~1.5% per km for insulated pipe
        self.loss_per_km = 0.015

    def optimize(self) -> Dict:
        """
        Greedy optimizer: Prioritize highest value use per MW thermal.
        In production, replace with pulp / ortools for true LP.
        Returns dispatch plan.
        """
        available_thermal = self.reactor.thermal_mw
        plan = {
            "timestamp": datetime.now().isoformat(),
            "electric_mw": 0,
            "heat_dispatch": [],
            "waste_dumped_mw": 0,
            "total_revenue_r_per_h": 0,
            "total_co2_saved_t_per_h": 0,
            "efficiency_total_pct": 0
        }

        # Sort clients by effective price after distance loss
        def effective_price(c: HeatClient):
            loss = c.distance_km * self.loss_per_km
            return c.price_per_mwh * (1 - loss)

        sorted_clients = sorted(self.clients, key=effective_price, reverse=True)

        # Decision: Is it more valuable to make electricity or heat?
        # Value of 1 MW thermal as electricity = elec_price * 0.33 (conversion eff)
        elec_value_per_thermal = self.reactor.electricity_price_r_per_mwh * 0.33

        remaining_thermal = available_thermal

        for client in sorted_clients:
            # Can we serve this client?
            loss_factor = 1 - (client.distance_km * self.loss_per_km)
            if loss_factor < 0.7:
                continue  # Too far, too much loss

            client_eff_price = client.price_per_mwh * loss_factor
            
            # Only divert to heat if heat pays more than electricity
            if client_eff_price < elec_value_per_thermal:
                continue

            allocatable = min(client.mw_demand / loss_factor, remaining_thermal * 0.8)  # Leave 20% for elec
            if allocatable < 1:
                continue

            delivered_mw = allocatable * loss_factor
            revenue = delivered_mw * client.price_per_mwh
            co2_saved = delivered_mw * client.co2_factor

            plan["heat_dispatch"].append({
                "client_id": client.id,
                "client_name": client.name,
                "thermal_allocated_mw": round(allocatable, 2),
                "heat_delivered_mw": round(delivered_mw, 2),
                "temp_c": client.temp_required_c,
                "revenue_r_h": round(revenue, 2),
                "co2_saved_t_h": round(co2_saved, 2),
                "distance_km": client.distance_km
            })
            remaining_thermal -= allocatable
            plan["total_revenue_r_per_h"] += revenue
            plan["total_co2_saved_t_per_h"] += co2_saved

        # Remaining thermal goes to electricity (33% eff) + waste
        electric_mw = min(remaining_thermal * 0.33, self.reactor.max_electric_mw)
        plan["electric_mw"] = round(electric_mw, 2)
        plan["total_revenue_r_per_h"] += electric_mw * self.reactor.electricity_price_r_per_mwh
        
        thermal_used_for_elec = electric_mw / 0.33
        plan["waste_dumped_mw"] = round(remaining_thermal - thermal_used_for_elec, 2)
        plan["efficiency_total_pct"] = round(((electric_mw + sum(d["heat_delivered_mw"] for d in plan["heat_dispatch"])) / self.reactor.thermal_mw) * 100, 1)
        
        return plan

# --- DEMO / TEST ---
if __name__ == "__main__":
    clients = [
        HeatClient("farm1", "Chicken Farm - Mareetsane", 70, 15, 650, 3.2),
        HeatClient("green1", "Greenhouse Cluster - Jouberton", 55, 25, 480, 5.1),
        HeatClient("mine1", "Gold Mine Processing", 90, 120, 900, 8.5),
        HeatClient("heat1", "District Heating - Klerksdorp", 65, 40, 550, 12.0),
        HeatClient("desal1", "Desalination Pilot", 80, 30, 1100, 2.0),
    ]

    reactor = ReactorState(electricity_price_r_per_mwh=850)
    opt = WasteHeatOptimizer(reactor, clients)
    result = opt.optimize()
    
    import json
    print(json.dumps(result, indent=2))
    print(f"\n> System efficiency jumped from 33% to {result['efficiency_total_pct']}%")
    print(f"> Extra revenue from waste: R{result['total_revenue_r_per_h'] - result['electric_mw']*850:,.0f}/hour")
