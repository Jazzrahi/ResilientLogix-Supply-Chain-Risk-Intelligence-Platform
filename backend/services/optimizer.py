import json
import random

class ResilienceOptimizer:
    def __init__(self):
        # Weights for the decision matrix
        self.weights = {
            "risk": 0.40,
            "cost": 0.25,
            "time": 0.25,
            "carbon": 0.10
        }

    def calculate_resilience_strategy(self, current_route_risk, alt_mode, cargo_priority, carbon_impact):
        """
        Decision Matrix for mode-switching recommendations.
        """
        # Base scores (0-100, higher is better)
        # For cost/time, we use 100 - (value/max) or similar normalization
        
        scores = {}
        
        # Risk Score: Higher risk = lower score
        scores["risk"] = (1.0 - current_route_risk) * 100
        
        # Priority Multiplier
        priority_factor = 1.5 if cargo_priority == "high" else 1.0
        
        # Decision: Stay Sea vs Switch to Air
        recommendation = "SEA"
        estimated_cost_delta = 0
        time_saved = 0
        
        if current_route_risk > 0.6 and cargo_priority == "high":
            recommendation = "AIR"
            # Calculate dynamic metrics based on vessel context
            # (In a real app, these would come from distance/weight/logistics models)
            seed = sum(ord(c) for c in str(current_route_risk))
            random.seed(seed)
            estimated_cost_delta = random.randint(12000, 45000)
            time_saved = random.randint(36, 120)
            random.seed(None)
            
        return {
            "recommended_path": recommendation,
            "estimated_cost_delta": estimated_cost_delta,
            "time_saved": time_saved,
            "confidence_score": round(scores["risk"] * priority_factor, 2)
        }

optimizer = ResilienceOptimizer()
