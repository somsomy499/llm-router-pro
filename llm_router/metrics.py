"""Metrics tracking for routing decisions."""
import time
from collections import defaultdict

class MetricsTracker:
    def __init__(self):
        self.records = []
        self.by_model = defaultdict(lambda: {"count": 0, "total_cost": 0, "total_latency": 0})
        
    def record(self, result):
        entry = {
            "model": result.model_used,
            "cost": result.cost,
            "latency_ms": result.latency_ms,
            "quality": result.quality_score,
            "timestamp": time.time(),
        }
        self.records.append(entry)
        m = self.by_model[result.model_used]
        m["count"] += 1
        m["total_cost"] += result.cost
        m["total_latency"] += result.latency_ms
        
    def summary(self):
        return {model: {
            "requests": d["count"],
            "avg_cost": d["total_cost"] / max(d["count"], 1),
            "avg_latency_ms": d["total_latency"] / max(d["count"], 1),
        } for model, d in self.by_model.items()}
