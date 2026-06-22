"""Basic usage examples for LLM Router Pro."""
import asyncio
from llm_router import Router, Config

async def example_cost_optimized():
    """Route to cheapest model that meets quality bar."""
    router = Router(Config(
        providers=[
            {"name": "openai", "models": ["gpt-4o", "gpt-4o-mini"]},
            {"name": "anthropic", "models": ["claude-sonnet-4-20250514"]},
            {"name": "local", "models": ["llama3.1"]},
        ],
        routing={"strategy": "cost-optimized", "budget_per_day": 10.0},
    ))
    
    result = await router.chat(
        messages=[{"role": "user", "content": "Summarize quantum computing in 3 sentences"}],
    )
    print(f"Model: {result.model_used}")
    print(f"Cost: ${result.cost:.4f}")
    print(f"Latency: {result.latency_ms:.0f}ms")
    print(f"Answer: {result.response[:100]}...")

async def example_batch():
    """Process multiple requests efficiently."""
    router = Router(Config(providers=[{"name": "openai", "models": ["gpt-4o-mini"]}]))
    
    questions = [
        "What is machine learning?",
        "Explain neural networks",
        "What is gradient descent?",
        "Compare supervised vs unsupervised learning",
        "What is overfitting?",
    ]
    
    results = []
    for q in questions:
        result = await router.chat(messages=[{"role": "user", "content": q}])
        results.append(result)
    
    total_cost = sum(r.cost for r in results)
    avg_latency = sum(r.latency_ms for r in results) / len(results)
    print(f"Processed {len(results)} requests")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Avg latency: {avg_latency:.0f}ms")

if __name__ == "__main__":
    asyncio.run(example_cost_optimized())
