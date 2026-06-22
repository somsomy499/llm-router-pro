"""Tests for LLM Router."""
import pytest
from llm_router import Router, Config

def test_config_defaults():
    config = Config()
    assert config.routing.strategy == "cost-optimized"
    assert config.routing.budget_per_day == 50.0

def test_classifier():
    from llm_router.classifier import TaskClassifier
    c = TaskClassifier()
    assert c.classify([{"role": "user", "content": "hi"}]) == "simple"
    assert c.classify([{"role": "user", "content": "implement a distributed cache"}]) == "complex"
