#!/usr/bin/env python3
"""
MW-Omega Orchestrator Demo -- runs without API keys.
Demonstrates: dependency graph, Monte Carlo simulation, decision compression.
"""
import json
import random
import sys
from datetime import datetime


def build_dependency_graph():
    """Build sample 39-document dependency graph."""
    docs = {f"DOC-{i:03d}": {
        "layer": 0 if i <= 6 else 1 if i <= 9 else 2 if i <= 23 else 3,
        "depends_on": [f"DOC-{max(1,i-j):03d}" for j in range(1, min(4, i))],
        "status": "CANONICAL"
    } for i in range(1, 40)}
    return docs


def monte_carlo_simulation(n_trials=10000):
    """Simulate deployment risk across document stack."""
    random.seed(42)  # Deterministic for demo
    results = []
    for _ in range(n_trials):
        doc_scores = [random.gauss(95, 3) for _ in range(39)]
        min_score = min(doc_scores)
        all_pass = all(s >= 85 for s in doc_scores)
        results.append({"min_score": min_score, "all_pass": all_pass})

    pass_rate = sum(1 for r in results if r["all_pass"]) / n_trials
    avg_min = sum(r["min_score"] for r in results) / n_trials
    return {
        "trials": n_trials,
        "deployment_pass_rate": f"{pass_rate:.1%}",
        "average_minimum_score": f"{avg_min:.1f}",
        "verdict": "DEPLOY" if pass_rate > 0.95 else "HOLD"
    }


def decision_compress(tasks):
    """Compress task list into prioritized execution order."""
    scored = []
    for t in tasks:
        score = t["impact"] * 0.4 + t["urgency"] * 0.3 + (10 - t["effort"]) * 0.3
        scored.append({**t, "priority_score": round(score, 1)})
    return sorted(scored, key=lambda x: -x["priority_score"])


def main():
    print("=" * 60)
    print("MW-OMEGA ORCHESTRATOR -- DEMO MODE (no API keys required)")
    print("=" * 60)

    # 1. Dependency Graph
    print("\n[1/3] Building 39-document dependency graph...")
    graph = build_dependency_graph()
    layers = {}
    for doc_id, info in graph.items():
        layers.setdefault(info["layer"], []).append(doc_id)
    for layer, docs in sorted(layers.items()):
        print(f"  Layer {layer}: {len(docs)} documents")
    print(f"  Total: {len(graph)} documents -- all CANONICAL")

    # 2. Monte Carlo
    print("\n[2/3] Running Monte Carlo deployment simulation...")
    mc = monte_carlo_simulation()
    print(f"  Trials: {mc['trials']:,}")
    print(f"  Deployment pass rate: {mc['deployment_pass_rate']}")
    print(f"  Average minimum score: {mc['average_minimum_score']}")
    print(f"  Verdict: {mc['verdict']}")

    # 3. Decision Compression
    print("\n[3/3] Compressing execution queue...")
    tasks = [
        {"name": "Ethereum attestation", "impact": 8, "urgency": 6, "effort": 3},
        {"name": "Arweave upload", "impact": 7, "urgency": 5, "effort": 2},
        {"name": "Per-document DOIs", "impact": 9, "urgency": 4, "effort": 7},
        {"name": "LLC formation", "impact": 10, "urgency": 8, "effort": 5},
        {"name": "Stripe integration", "impact": 9, "urgency": 7, "effort": 6},
    ]
    prioritized = decision_compress(tasks)
    for i, t in enumerate(prioritized, 1):
        print(f"  {i}. [{t['priority_score']}] {t['name']}")

    print("\n" + "=" * 60)
    print(f"Demo complete -- {datetime.utcnow().isoformat()}Z")
    print("Full mode requires ANTHROPIC_API_KEY in environment.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
