"""Pytest configuration and fixtures for cfabric_benchmarks tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from cfabric_benchmarks.models.config import BenchmarkConfig, CorpusConfig


@pytest.fixture
def sample_config(tmp_path: Path) -> BenchmarkConfig:
    """Create a sample benchmark configuration."""
    return BenchmarkConfig(
        num_runs=2,
        warmup_runs=1,
        corpora_dir=tmp_path / "corpora",
        output_dir=tmp_path / "output",
        num_patterns=10,
        latency_iterations=3,
        num_workers=2,
    )


@pytest.fixture
def sample_corpus_config(tmp_path: Path) -> CorpusConfig:
    """Create a sample corpus configuration."""
    tf_path = tmp_path / "test_corpus"
    tf_path.mkdir(parents=True)
    return CorpusConfig(
        name="test_corpus",
        tf_path=tf_path,
    )


@pytest.fixture
def sample_latencies() -> list[float]:
    """Sample latency measurements for testing."""
    return [1.2, 1.5, 1.3, 1.8, 1.1, 2.0, 1.4, 1.6, 1.7, 1.9]


@pytest.fixture
def sample_memory_values() -> list[float]:
    """Sample memory measurements in MB for testing."""
    return [100.0, 102.5, 101.2, 103.0, 99.8, 104.5, 100.8, 102.0, 101.5, 103.2]
