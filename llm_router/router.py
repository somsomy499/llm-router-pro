"""Core routing logic with cost-aware model selection."""
import time
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class RouteResult:
    model_used: str
    provider: str
    response: str
    cost: float
    latency_ms: float
    quality_score: float
    tokens_used: int = 0

@dataclass
class ProviderHealth:
    failures: int = 0
    last_failure: float = 0
    is_circuit_open: bool = False

class Router:
    def __init__(self, config):
        self.config = config
        self.health: Dict[str, ProviderHealth] = {}
        self.classifier = TaskClassifier()
        self.metrics = MetricsTracker()
        
    async def chat(self, messages, task_type=None, **kwargs):
        task = task_type or self.classifier.classify(messages)
        model, provider = self._select_model(task)
        
        start = time.monotonic()
        response = await self._call_provider(provider, model, messages, **kwargs)
        latency = (time.monotonic() - start) * 1000
        
        result = RouteResult(
            model_used=model,
            provider=provider,
            response=response["content"],
            cost=response["cost"],
            latency_ms=latency,
            quality_score=response.get("quality", 0.9),
            tokens_used=response.get("tokens", 0),
        )
        self.metrics.record(result)
        return result
        
    def _select_model(self, task):
        for provider in self._available_providers():
            if self._circuit_is_open(provider):
                continue
            for model in self._provider_models(provider):
                score = self._score_model(model, provider, task)
                if score > 0.7:
                    return model, provider["name"]
        fallback = self._cheapest_available()
        return fallback["model"], fallback["provider"]
        
    def _available_providers(self):
        return [p for p in self.config.providers if not self._circuit_is_open(p["name"])]
    
    def _circuit_is_open(self, provider_name):
        h = self.health.get(provider_name)
        if not h:
            return False
        if h.failures >= self.config.circuit_breaker.failure_threshold:
            if time.time() - h.last_failure < self.config.circuit_breaker.recovery_timeout:
                return True
            h.failures = 0
            h.is_circuit_open = False
        return False
