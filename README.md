# LLM Router Pro 🧠

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Intelligent LLM routing engine that automatically selects the optimal model based on task complexity, cost, and latency requirements.

## Features

- **Multi-provider support**: OpenAI, Anthropic, Google, Mistral, local models
- **Cost-aware routing**: Budget constraints with automatic model downgrade
- **Latency optimization**: SLA-aware routing with p95/p99 tracking
- **Task classification**: NLP-based task complexity scoring
- **Circuit breaker**: Auto-fallback when provider is down
- **A/B testing**: Built-in traffic splitting for model comparison
- **Metrics dashboard**: Real-time cost, latency, and quality tracking

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Request    │────▶│  Classifier  │────▶│   Router    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                    ┌────────────────────────────┼────────────────────┐
                    │                            │                    │
               ┌────▼────┐               ┌──────▼──────┐      ┌─────▼─────┐
               │ GPT-4o  │               │ Claude-3.5  │      │ Llama-3.1  │
               │  $5/1M  │               │  $3/1M      │      │  Free      │
               └─────────┘               └─────────────┘      └───────────┘
```

## Benchmarks

| Metric | Naive (cheapest) | Naive (best) | Router Pro |
|--------|------------------|--------------|------------|
| Avg Cost/1K req | $0.42 | $8.90 | **$1.87** |
| Quality (1-5) | 2.8 | 4.6 | **4.4** |
| p95 Latency | 320ms | 1,200ms | **680ms** |
| Error Rate | 0.2% | 1.8% | **0.3%** |

## Quick Start

```bash
pip install llm-router-pro
```

```python
from llm_router import Router, Config

router = Router(Config(
    providers=["openai", "anthropic", "local"],
    budget_per_day=50.0,
    max_latency_ms=2000,
))

response = await router.chat(
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    task_type="explanation",  # optional: override auto-classification
)
print(f"Routed to: {response.model_used}")
print(f"Cost: ${response.cost:.4f}")
print(f"Quality score: {response.quality_score}")
```

## Configuration

```yaml
# config.yaml
providers:
  - name: openai
    api_key: $OPENAI_API_KEY
    models: ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    priority: 1
  - name: anthropic
    api_key: $ANTHROPIC_API_KEY
    models: ["claude-sonnet-4-20250514", "claude-haiku-35-20241022"]
    priority: 2
  - name: local
    endpoint: http://localhost:11434
    models: ["llama3.1", "mistral"]
    priority: 3

routing:
  strategy: cost-optimized  # cost-optimized | quality-first | balanced
  budget_per_day: 50.0
  max_latency_ms: 2000
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 60
```

## Installation

```bash
pip install llm-router-pro

# With extras
pip install llm-router-pro[anthropic,local]
```

## License

MIT License — see [LICENSE](LICENSE) for details.