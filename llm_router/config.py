"""Configuration management for LLM Router."""
from dataclasses import dataclass, field
from typing import List, Dict, Any
import yaml
import os

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60

@dataclass
class RoutingConfig:
    strategy: str = "cost-optimized"
    budget_per_day: float = 50.0
    max_latency_ms: int = 2000
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)

@dataclass
class Config:
    providers: List[Dict[str, Any]] = field(default_factory=list)
    routing: RoutingConfig = field(default_factory=RoutingConfig)
    
    @classmethod
    def from_yaml(cls, path):
        with open(path) as f:
            data = yaml.safe_load(f)
        providers = data.get("providers", [])
        routing_data = data.get("routing", {})
        cb = CircuitBreakerConfig(**routing_data.pop("circuit_breaker", {}))
        routing = RoutingConfig(**routing_data, circuit_breaker=cb)
        return cls(providers=providers, routing=routing)
