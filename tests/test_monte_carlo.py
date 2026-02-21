"""Tests for Monte Carlo deployment simulation."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'demo'))
from run_demo import monte_carlo_simulation


class TestMonteCarlo:
    """Test suite for Monte Carlo deployment risk simulation."""

    def test_deterministic_output(self):
        """Same seed should produce identical results."""
        r1 = monte_carlo_simulation(n_trials=1000)
        r2 = monte_carlo_simulation(n_trials=1000)
        assert r1 == r2, "Monte Carlo with same seed should be deterministic"

    def test_default_trial_count(self):
        result = monte_carlo_simulation()
        assert result["trials"] == 10000

    def test_custom_trial_count(self):
        result = monte_carlo_simulation(n_trials=500)
        assert result["trials"] == 500

    def test_pass_rate_is_percentage(self):
        result = monte_carlo_simulation(n_trials=100)
        rate = result["deployment_pass_rate"]
        assert rate.endswith("%"), f"Pass rate should be percentage, got {rate}"

    def test_verdict_is_valid(self):
        result = monte_carlo_simulation()
        assert result["verdict"] in ("DEPLOY", "HOLD"), f"Invalid verdict: {result['verdict']}"

    def test_average_min_score_reasonable(self):
        result = monte_carlo_simulation()
        avg = float(result["average_minimum_score"])
        assert 70 < avg < 100, f"Average min score {avg} out of reasonable range"

    def test_high_pass_rate_with_good_params(self):
        """With mean=95, stdev=3, deployment should usually pass."""
        result = monte_carlo_simulation(n_trials=10000)
        rate = float(result["deployment_pass_rate"].rstrip("%")) / 100
        assert rate > 0.5, f"Pass rate {rate} unexpectedly low for mean=95, stdev=3"

    def test_single_trial(self):
        result = monte_carlo_simulation(n_trials=1)
        assert result["trials"] == 1
