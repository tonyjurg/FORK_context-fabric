"""Tests for statistical analysis functions."""

from __future__ import annotations

import math

import pytest

from cfabric_benchmarks.analysis.statistics import (
    aggregate_runs,
    compare_implementations,
    compute_confidence_interval,
    compute_percentiles,
    compute_summary,
    linear_regression,
    welch_t_test,
)


class TestComputeSummary:
    """Tests for compute_summary function."""

    def test_basic_summary(self, sample_latencies: list[float]) -> None:
        """Test basic statistical summary computation."""
        summary = compute_summary(sample_latencies, "latency", "ms")

        assert summary.metric_name == "latency"
        assert summary.unit == "ms"
        assert summary.n == len(sample_latencies)
        assert summary.min == min(sample_latencies)
        assert summary.max == max(sample_latencies)

    def test_mean_calculation(self) -> None:
        """Test mean calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        summary = compute_summary(values, "test", "unit")
        assert summary.mean == 3.0

    def test_median_calculation(self) -> None:
        """Test median calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        summary = compute_summary(values, "test", "unit")
        assert summary.median == 3.0

    def test_std_calculation(self) -> None:
        """Test standard deviation calculation."""
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        summary = compute_summary(values, "test", "unit")
        # Expected sample std is approximately 2.14
        assert abs(summary.std - 2.14) < 0.2

    def test_empty_values(self) -> None:
        """Test summary with empty values."""
        summary = compute_summary([], "test", "unit")
        assert summary.n == 0
        assert summary.mean == 0.0

    def test_single_value(self) -> None:
        """Test summary with single value."""
        summary = compute_summary([5.0], "test", "unit")
        assert summary.n == 1
        assert summary.mean == 5.0
        assert summary.std == 0.0


class TestComputePercentiles:
    """Tests for compute_percentiles function."""

    def test_basic_percentiles(self) -> None:
        """Test basic percentile calculation."""
        values = list(range(1, 101))  # 1 to 100
        percentiles = compute_percentiles(values, [50, 95, 99])

        assert percentiles[50] == pytest.approx(50.5, rel=0.05)
        assert percentiles[95] == pytest.approx(95.05, rel=0.05)
        assert percentiles[99] == pytest.approx(99.01, rel=0.05)

    def test_empty_values(self) -> None:
        """Test percentiles with empty values."""
        percentiles = compute_percentiles([], [50, 95, 99])
        assert percentiles[50] == 0.0
        assert percentiles[95] == 0.0
        assert percentiles[99] == 0.0

    def test_single_value(self) -> None:
        """Test percentiles with single value."""
        percentiles = compute_percentiles([42.0], [50, 95, 99])
        assert percentiles[50] == 42.0
        assert percentiles[95] == 42.0
        assert percentiles[99] == 42.0


class TestComputeConfidenceInterval:
    """Tests for compute_confidence_interval function."""

    def test_basic_ci(self) -> None:
        """Test basic confidence interval calculation."""
        values = [10.0, 12.0, 11.0, 13.0, 9.0, 11.0, 12.0, 10.0]
        ci_lower, ci_upper = compute_confidence_interval(values)

        mean = sum(values) / len(values)
        assert ci_lower < mean < ci_upper

    def test_symmetric_ci(self) -> None:
        """Test that CI is roughly symmetric around mean."""
        values = [10.0] * 100  # All same values
        ci_lower, ci_upper = compute_confidence_interval(values)

        # With no variance, CI should be very tight
        assert ci_lower == pytest.approx(10.0, rel=0.01)
        assert ci_upper == pytest.approx(10.0, rel=0.01)

    def test_empty_values(self) -> None:
        """Test CI with empty values."""
        ci_lower, ci_upper = compute_confidence_interval([])
        assert ci_lower == 0.0
        assert ci_upper == 0.0

    def test_single_value(self) -> None:
        """Test CI with single value."""
        ci_lower, ci_upper = compute_confidence_interval([5.0])
        assert ci_lower == 5.0
        assert ci_upper == 5.0


class TestWelchTTest:
    """Tests for welch_t_test function."""

    def test_same_populations(self) -> None:
        """Test t-test on identical populations."""
        a = [10.0, 11.0, 12.0, 10.0, 11.0]
        b = [10.0, 11.0, 12.0, 10.0, 11.0]
        t_stat, p_value = welch_t_test(a, b)

        # Same populations should have high p-value
        assert p_value > 0.05

    def test_different_populations(self) -> None:
        """Test t-test on clearly different populations."""
        a = [10.0, 11.0, 12.0, 10.0, 11.0] * 10
        b = [100.0, 101.0, 102.0, 100.0, 101.0] * 10
        t_stat, p_value = welch_t_test(a, b)

        # Very different populations should have very low p-value
        assert p_value < 0.001

    def test_empty_inputs(self) -> None:
        """Test t-test with empty inputs."""
        t_stat, p_value = welch_t_test([], [1.0, 2.0])
        assert t_stat == 0.0
        assert p_value == 1.0


class TestCompareImplementations:
    """Tests for compare_implementations function."""

    def test_basic_comparison(self) -> None:
        """Test basic implementation comparison."""
        tf_values = [100.0, 102.0, 98.0, 101.0, 99.0]
        cf_values = [50.0, 52.0, 48.0, 51.0, 49.0]

        result = compare_implementations(
            tf_values, cf_values, "memory", "MB", metric_type="memory"
        )

        assert result.metric_name == "memory"
        assert result.tf_stats.mean > result.cf_stats.mean
        # CF uses less memory, so reduction should be positive
        assert result.reduction_percent is not None
        assert result.reduction_percent > 0

    def test_speedup_factor(self) -> None:
        """Test speedup factor calculation."""
        tf_values = [100.0, 101.0, 102.0, 99.0, 98.0] * 2
        cf_values = [50.0, 51.0, 52.0, 49.0, 48.0] * 2

        result = compare_implementations(
            tf_values, cf_values, "latency", "ms", metric_type="time"
        )

        assert result.speedup_factor == pytest.approx(2.0, rel=0.1)


class TestLinearRegression:
    """Tests for linear_regression function."""

    def test_perfect_fit(self) -> None:
        """Test linear regression with perfect linear data."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]  # y = 2x

        slope, intercept, r_squared = linear_regression(x, y)

        assert slope == pytest.approx(2.0, rel=0.01)
        assert intercept == pytest.approx(0.0, abs=0.01)
        assert r_squared == pytest.approx(1.0, rel=0.01)

    def test_with_intercept(self) -> None:
        """Test linear regression with non-zero intercept."""
        x = [1, 2, 3, 4, 5]
        y = [12, 14, 16, 18, 20]  # y = 2x + 10

        slope, intercept, r_squared = linear_regression(x, y)

        assert slope == pytest.approx(2.0, rel=0.01)
        assert intercept == pytest.approx(10.0, rel=0.01)
        assert r_squared == pytest.approx(1.0, rel=0.01)

    def test_noisy_data(self) -> None:
        """Test linear regression with noisy data."""
        x = [1, 2, 3, 4, 5]
        y = [2.1, 3.9, 6.2, 7.8, 10.1]  # Approximately y = 2x

        slope, intercept, r_squared = linear_regression(x, y)

        # Should still be close to 2
        assert abs(slope - 2.0) < 0.3
        assert r_squared > 0.95

    def test_insufficient_data(self) -> None:
        """Test linear regression with insufficient data."""
        slope, intercept, r_squared = linear_regression([1], [2])

        assert slope == 0.0
        assert intercept == 0.0
        assert r_squared == 0.0


class TestAggregateRuns:
    """Tests for aggregate_runs function."""

    def test_basic_aggregation(self) -> None:
        """Test basic run aggregation."""
        runs = [
            [10.0, 20.0, 30.0],
            [11.0, 21.0, 31.0],
            [9.0, 19.0, 29.0],
        ]

        means, stds = aggregate_runs(runs)

        assert len(means) == 3
        assert len(stds) == 3
        assert means[0] == pytest.approx(10.0, rel=0.1)
        assert means[1] == pytest.approx(20.0, rel=0.1)
        assert means[2] == pytest.approx(30.0, rel=0.1)

    def test_empty_runs(self) -> None:
        """Test aggregation with empty runs."""
        means, stds = aggregate_runs([])
        assert means == []
        assert stds == []

    def test_single_run(self) -> None:
        """Test aggregation with single run."""
        runs = [[10.0, 20.0, 30.0]]
        means, stds = aggregate_runs(runs)

        assert means == [10.0, 20.0, 30.0]
        assert stds == [0.0, 0.0, 0.0]
