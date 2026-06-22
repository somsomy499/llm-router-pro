# Architecture

## Overview

LLM Router Pro uses a pipeline architecture:

```
Input → Classifier → Router → Provider → Response → Cache
                                      ↓
                                   Metrics
```

## Components

### Task Classifier
NLP-based classifier that determines task complexity (simple/moderate/complex/advanced).
Uses regex patterns and keyword matching for speed.

### Router
Selects optimal model based on:
- Task complexity score
- Provider health status
- Cost constraints
- Latency SLA
- Circuit breaker state

### Load Balancer
Distributes requests across providers using:
- Round-robin
- Weighted (based on success rate + latency)
- Least-latency
- Random

### Cache
LRU cache with configurable TTL to avoid redundant API calls.
Key is hash of (messages, model, params).

### Circuit Breaker
Per-provider circuit breaker:
- Opens after N consecutive failures
- Half-opens after recovery timeout
- Closes on successful request

### Metrics
Tracks per-provider: request count, latency, cost, success rate.
Used for adaptive weight adjustment in load balancer.
