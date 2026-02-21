"""Tests for decision compression algorithm."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'demo'))
from run_demo import decision_compress


class TestDecisionCompressor:
    """Test suite for task prioritization algorithm."""

    def test_returns_sorted_by_priority(self):
        tasks = [
            {"name": "low", "impact": 1, "urgency": 1, "effort": 9},
            {"name": "high", "impact": 10, "urgency": 10, "effort": 1},
        ]
        result = decision_compress(tasks)
        assert result[0]["name"] == "high"
        assert result[1]["name"] == "low"

    def test_preserves_all_tasks(self):
        tasks = [
            {"name": f"task-{i}", "impact": i, "urgency": i, "effort": i}
            for i in range(1, 6)
        ]
        result = decision_compress(tasks)
        assert len(result) == 5

    def test_adds_priority_score(self):
        tasks = [{"name": "test", "impact": 5, "urgency": 5, "effort": 5}]
        result = decision_compress(tasks)
        assert "priority_score" in result[0]

    def test_priority_score_formula(self):
        """Score = impact * 0.4 + urgency * 0.3 + (10 - effort) * 0.3"""
        tasks = [{"name": "test", "impact": 10, "urgency": 8, "effort": 2}]
        result = decision_compress(tasks)
        expected = 10 * 0.4 + 8 * 0.3 + (10 - 2) * 0.3  # 4 + 2.4 + 2.4 = 8.8
        assert result[0]["priority_score"] == round(expected, 1)

    def test_empty_input(self):
        result = decision_compress([])
        assert result == []

    def test_single_task(self):
        tasks = [{"name": "only", "impact": 7, "urgency": 3, "effort": 5}]
        result = decision_compress(tasks)
        assert len(result) == 1
        assert result[0]["name"] == "only"

    def test_high_effort_penalized(self):
        """High effort (10) should produce lower score than low effort (1), all else equal."""
        tasks = [
            {"name": "easy", "impact": 5, "urgency": 5, "effort": 1},
            {"name": "hard", "impact": 5, "urgency": 5, "effort": 10},
        ]
        result = decision_compress(tasks)
        assert result[0]["name"] == "easy"

    def test_original_task_data_preserved(self):
        tasks = [{"name": "test", "impact": 3, "urgency": 7, "effort": 4}]
        result = decision_compress(tasks)
        assert result[0]["impact"] == 3
        assert result[0]["urgency"] == 7
        assert result[0]["effort"] == 4
