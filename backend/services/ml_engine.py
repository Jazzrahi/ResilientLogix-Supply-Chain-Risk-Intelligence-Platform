import numpy as np
import pandas as pd
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
import random

class MLEngine:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=10)
        self.graph = nx.DiGraph()
        self._mock_train()
        self._initialize_graph()

    def _mock_train(self):
        # Create mock features: [congestion_index, labor_strike_prob, weather_severity]
        X = np.array([
            [0.1, 0.05, 0.1], [0.8, 0.1, 0.2], [0.2, 0.9, 0.1], [0.9, 0.8, 0.9],
            [0.3, 0.2, 0.3], [0.7, 0.6, 0.7], [0.1, 0.1, 0.8], [0.5, 0.5, 0.5]
        ])
        # Labels: 1 for disruption, 0 for normal
        y = np.array([0, 1, 1, 1, 0, 1, 1, 0])
        self.model.fit(X, y)

    def _initialize_graph(self):
        # Supply Chain Graph: Nodes (Ports/Hubs) -> Edges (Routes)
        self.graph.add_edge("Shanghai", "Singapore", weight=5)
        self.graph.add_edge("Singapore", "Suez", weight=12)
        self.graph.add_edge("Suez", "Rotterdam", weight=8)
        self.graph.add_edge("Singapore", "CapeTown", weight=20)
        self.graph.add_edge("CapeTown", "Rotterdam", weight=15)

    def predict_disruption(self, congestion, strike_prob, weather):
        features = np.array([[congestion, strike_prob, weather]])
        prob = self.model.predict_proba(features)[0][1]
        return round(prob, 2)

    def find_shortest_path(self, start, end, avoided_node=None):
        temp_graph = self.graph.copy()
        if avoided_node in temp_graph:
            temp_graph.remove_node(avoided_node)
        
        try:
            path = nx.shortest_path(temp_graph, source=start, target=end, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

ml_engine = MLEngine()
