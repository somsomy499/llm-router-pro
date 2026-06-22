"""Load balancer for distributing requests across providers."""
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import threading

@dataclass
class ProviderStats:
    name: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    total_latency_ms: float = 0
    total_cost: float = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    
    @property
    def avg_latency(self):
        return self.total_latency_ms / max(self.successful, 1)
    
    @property
    def success_rate(self):
        return self.successful / max(self.total_requests, 1)
    
    @property
    def avg_cost(self):
        return self.total_cost / max(self.successful, 1)
    
    def record_success(self, latency_ms, cost):
        with self._lock:
            self.total_requests += 1
            self.successful += 1
            self.total_latency_ms += latency_ms
            self.total_cost += cost
    
    def record_failure(self):
        with self._lock:
            self.total_requests += 1
            self.failed += 1

class LoadBalancer:
    """Weighted round-robin load balancer with health tracking."""
    
    def __init__(self, providers: List[str], strategy: str = "weighted"):
        self.providers = providers
        self.strategy = strategy
        self.stats = {p: ProviderStats(name=p) for p in providers}
        self._weights = {p: 1.0 for p in providers}
        self._current_idx = 0
        self._lock = threading.Lock()
        
    def select(self) -> str:
        with self._lock:
            if self.strategy == "round-robin":
                return self._round_robin()
            elif self.strategy == "weighted":
                return self._weighted_select()
            elif self.strategy == "least-latency":
                return self._least_latency()
            elif self.strategy == "random":
                return random.choice(self.providers)
            return self.providers[0]
    
    def _round_robin(self):
        provider = self.providers[self._current_idx % len(self.providers)]
        self._current_idx += 1
        return provider
    
    def _weighted_select(self):
        healthy = [p for p in self.providers if self._is_healthy(p)]
        if not healthy:
            return self.providers[0]
        weights = [self._weights[p] for p in healthy]
        total = sum(weights)
        r = random.uniform(0, total)
        cumulative = 0
        for p, w in zip(healthy, weights):
            cumulative += w
            if r <= cumulative:
                return p
        return healthy[-1]
    
    def _least_latency(self):
        healthy = [p for p in self.providers if self._is_healthy(p)]
        if not healthy:
            return self.providers[0]
        return min(healthy, key=lambda p: self.stats[p].avg_latency)
    
    def _is_healthy(self, provider):
        s = self.stats[provider]
        if s.total_requests < 5:
            return True
        return s.success_rate > 0.5
    
    def record(self, provider, success, latency_ms=0, cost=0):
        if success:
            self.stats[provider].record_success(latency_ms, cost)
            self._update_weight(provider)
        else:
            self.stats[provider].record_failure()
    
    def _update_weight(self, provider):
        s = self.stats[provider]
        if s.total_requests > 10:
            score = s.success_rate * 0.6 + (1 - min(s.avg_latency / 2000, 1)) * 0.4
            self._weights[provider] = max(0.1, score)
    
    def get_report(self) -> Dict:
        return {p: {
            "requests": s.total_requests,
            "success_rate": f"{s.success_rate:.1%}",
            "avg_latency_ms": f"{s.avg_latency:.0f}",
            "avg_cost": f"${s.avg_cost:.4f}",
            "weight": f"{self._weights[p]:.2f}",
        } for p, s in self.stats.items()}
