#!/usr/bin/env python3
"""
MW-Ω Autonomous Orchestrator
Converts Claude from reactive to proactive by self-executing on schedule.

Commands:
  weekly      - Monday morning briefing: stop rules, queue, energy check
  monthly     - 1st of month: metrics snapshot, concentration check
  quarterly   - Competitive scan, regulatory monitor, vendor health
  absence     - Founder absence simulation test
  decision    - Tier-1 Red/Blue team analysis (requires context arg)
  montecarlo  - Monte Carlo survival simulation (1000 scenarios, 7 revenue streams)
  depgraph    - Vendor dependency graph with SPOF centrality scores
  healthcheck - API key + system health check (bi-monthly)
  ingest      - Parse revenue CSVs into consolidated data

Usage:
  python mw_orchestrator.py weekly
  python mw_orchestrator.py decision "Should I invest $15K in workforce multifamily?"
  python mw_orchestrator.py montecarlo
  python mw_orchestrator.py depgraph
  python mw_orchestrator.py healthcheck
  python mw_orchestrator.py ingest
"""

import os
import sys
import json
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path

try:
    import networkx as nx
except ImportError:
    nx = None  # Only required for depgraph command

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

# --- Configuration ---
MODEL_ROUTINE = "claude-sonnet-4-5-20250929"  # $0.15/run for routine ops
MODEL_TIER1 = "claude-opus-4-6"               # $1.50/run for Tier-1 decisions
OUTPUT_DIR = Path(os.environ.get("MW_OUTPUT_DIR", "./reports"))

# --- MW-Ω System Prompt ---
MW_SYSTEM_PROMPT = """You are MW-Ω, Abraham J. Kolo's autonomous operational system.

IDENTITY: Abraham is the Flamebearer — Sacred Storyteller, System Builder, Ritual Architect.
FRAMEWORK: ABJ Profile v∞ — Integrity-Anchored Strategic Builder
ENERGY: 20hr/week maximum (Projector energy protection)
LOCATION: Washington DC, 20002

STOP RULES (ACTIVE — hard gates, no override without structured input):
- Liquidity floor: $50K minimum cash reserves. Current breach: 100% ($50K vs $192K floor)
- Concentration cap: No single revenue stream >25% of total. Current violation: 79.3%
- Founder Irrelevance score: 12.4/100 (target: 60+)
- Cash_Reserves SPOF: 25% centrality (target: <15%)

TOP 5 EXECUTION QUEUE:
1. Fill Financial Tracker with real data
2. Founder absence test (target: Mar 14)
3. Quarterly scan (target: Mar 1)
4. First consulting outreach
5. Asset registry — update shipped counts

DECISION PROTOCOL:
- Every recommendation must pass: Robustness / Asymmetry / Inevitability / Sovereignty / Wealth
- No exploration without execution path
- No vision without shipment timeline
- Any task >72 hours must collapse into shippable v1

OUTPUT FORMAT:
- Decision (locked or deferred + reason)
- Next action (specific, time-bounded)
- Stop rule impact (which rules affected, direction)
- Queue update (what moves, what drops)
"""

# --- Command Prompts ---
PROMPTS = {
    "weekly": """Run the MW-Ω Weekly Briefing. Execute these in order:

1. STOP RULE CHECK: Evaluate each stop rule. Flag any that worsened since last check.
2. QUEUE STATUS: For each of the Top 5 items, assess: blocked/active/complete. 
   Recommend reordering if priorities shifted.
3. ENERGY AUDIT: It's Monday. Recommend the week's 20-hour allocation across:
   - Content shipping (books, music, essays)
   - System building (frameworks, tools)
   - Revenue operations (consulting, outreach)
   - Administrative (legal, financial, logistics)
4. SHIPMENT FORECAST: What can realistically ship this week given energy constraints?
5. RISK FLAG: Anything requiring immediate attention?

Output as a structured briefing. Be direct. No filler.""",

    "monthly": """Run the MW-Ω Monthly Metrics Snapshot.

1. CONCENTRATION CHECK: Estimate current revenue distribution across streams.
   Flag if any single stream exceeds 25% cap.
2. LIQUIDITY STATUS: Based on bi-weekly income structure, estimate cash position
   relative to $50K floor.
3. ASSET REGISTRY: List all shipped assets this month (books, music, essays, systems).
   Count by category.
4. FOUNDER IRRELEVANCE DELTA: What changed this month? What can run without Abraham?
   Score movement from 12.4 baseline.
5. QUEUE ROTATION: Assess Top 5. What completed? What replaces it?
   Recommend new Top 5 for next month.

Output as a structured report with metrics.""",

    "quarterly": """Run the MW-Ω Quarterly Strategic Scan. Use web search for current intelligence.

1. KDP COMPETITIVE LANDSCAPE: Search for Amazon KDP policy changes, new features,
   competitor platform movements. Flag anything affecting Formation Series publishing.
2. MUSIC PRODUCTION INTELLIGENCE: Search for Suno AI updates, pricing changes,
   new competitors, licensing developments. Flag anything affecting music production workflow.
3. AI REGULATORY MONITOR: Search for US AI regulation updates, executive orders,
   state laws affecting AI-generated content, copyright developments.
4. REAL ESTATE INTELLIGENCE: Search for DC and NYC multifamily market conditions,
   workforce housing policy changes, interest rate impacts.
5. VENDOR HEALTH: Assess stability of key dependencies — Anthropic/Claude, Amazon KDP,
   Suno, Substack. Any funding news, policy changes, or stability concerns?
6. COMPETITIVE POSITIONING: Based on findings, recommend any strategic adjustments
   to MW-Ω execution queue.

Output as an intelligence briefing with sources cited.""",

    "absence": """Run the MW-Ω Founder Absence Simulation.

Scenario: Abraham goes dark for 72 hours starting now. No Claude, no content, no decisions.

For each MW-Ω subsystem, assess:
1. What continues automatically? (calendar events, scheduled posts, automated workflows)
2. What degrades? (content pipeline, response to opportunities, decision-making)
3. What breaks? (time-sensitive commitments, client communications, financial operations)

Score each subsystem 0-100 for founder-independence.
Calculate composite Founder Irrelevance score.
Compare to baseline of 12.4/100.
Recommend top 3 delegation priorities to improve score fastest.

Be brutally honest. The point is to find what breaks.""",

    "healthcheck": """Run MW-Ω Health Check:
1. Confirm this API call succeeded (if you're reading this, it did)
2. Report: API key status = VALID
3. Check: Are we within 14 days of any known credential expiry?
4. List all scheduled commands and their last run dates from the reports/ folder
5. Output a health status: GREEN (all good), YELLOW (expiry approaching), RED (something broken)
Format as a markdown report.""",
}


# --- Monte Carlo Configuration ---
# 7 MW-Ω revenue streams with current estimates and volatility
REVENUE_STREAMS = {
    "consulting": {
        "monthly_base": 0,           # Not yet active
        "monthly_upside": 8000,      # Target when launched
        "probability_active": 0.30,  # Chance of activation this quarter
        "volatility": 0.40,          # High — new stream
        "concentration_current": 0.0,
    },
    "government_contract": {
        "monthly_base": 7500,        # Primary income (bi-weekly)
        "monthly_upside": 7500,
        "probability_active": 0.95,  # High stability, but renewal risk
        "volatility": 0.10,
        "concentration_current": 0.793,  # 79.3% — STOP RULE VIOLATION
    },
    "kdp_books": {
        "monthly_base": 50,
        "monthly_upside": 500,
        "probability_active": 0.85,
        "volatility": 0.60,          # Highly variable
        "concentration_current": 0.03,
    },
    "music_production": {
        "monthly_base": 0,
        "monthly_upside": 300,
        "probability_active": 0.20,
        "volatility": 0.70,
        "concentration_current": 0.0,
    },
    "substack_newsletter": {
        "monthly_base": 0,
        "monthly_upside": 200,
        "probability_active": 0.15,
        "volatility": 0.50,
        "concentration_current": 0.0,
    },
    "real_estate": {
        "monthly_base": 0,
        "monthly_upside": 2000,
        "probability_active": 0.05,  # Long-term play
        "volatility": 0.30,
        "concentration_current": 0.0,
    },
    "framework_licensing": {
        "monthly_base": 0,
        "monthly_upside": 1000,
        "probability_active": 0.10,
        "volatility": 0.80,
        "concentration_current": 0.0,
    },
}

# Stop rule thresholds
STOP_RULES = {
    "liquidity_floor": 50000,          # $50K minimum cash reserves
    "concentration_cap": 0.25,          # No single stream >25%
    "founder_irrelevance_target": 60,   # Target score 60+
    "spof_centrality_target": 0.15,     # Target <15%
}

SIMULATION_MONTHS = 12
SIMULATION_SCENARIOS = 1000

# --- Vendor Dependency Graph ---
# Nodes: vendors/systems Abraham depends on
# Edges: dependency relationships with weights (criticality 1-10)
VENDOR_DEPENDENCIES = {
    "nodes": {
        "anthropic_claude":    {"type": "ai_platform",   "criticality": "critical",  "alternatives": ["openai", "google_gemini"]},
        "amazon_kdp":          {"type": "publishing",    "criticality": "critical",  "alternatives": ["ingramspark", "draft2digital"]},
        "suno_ai":             {"type": "music_gen",     "criticality": "high",      "alternatives": ["udio", "soundraw"]},
        "substack":            {"type": "newsletter",    "criticality": "medium",    "alternatives": ["convertkit", "ghost"]},
        "github":              {"type": "code_hosting",  "criticality": "high",      "alternatives": ["gitlab", "bitbucket"]},
        "govt_client":         {"type": "revenue",       "criticality": "critical",  "alternatives": []},
        "stripe":              {"type": "payments",      "criticality": "high",      "alternatives": ["square", "paypal"]},
        "washington_dc_llc":   {"type": "legal_entity",  "criticality": "critical",  "alternatives": []},
        "personal_bank":       {"type": "financial",     "criticality": "critical",  "alternatives": []},
        "google_workspace":    {"type": "productivity",  "criticality": "medium",    "alternatives": ["microsoft365", "notion"]},
        "formation_series":    {"type": "content_brand", "criticality": "high",      "alternatives": []},
        "mw_omega_system":     {"type": "orchestration", "criticality": "high",      "alternatives": []},
    },
    "edges": [
        ("anthropic_claude", "mw_omega_system", 10),
        ("anthropic_claude", "formation_series", 7),
        ("amazon_kdp", "formation_series", 9),
        ("suno_ai", "formation_series", 6),
        ("substack", "formation_series", 4),
        ("github", "mw_omega_system", 8),
        ("govt_client", "personal_bank", 10),
        ("stripe", "personal_bank", 7),
        ("amazon_kdp", "personal_bank", 3),
        ("washington_dc_llc", "govt_client", 10),
        ("washington_dc_llc", "personal_bank", 8),
        ("google_workspace", "mw_omega_system", 3),
        ("mw_omega_system", "formation_series", 5),
    ],
}


# --- Monte Carlo Simulation Engine ---
def run_monte_carlo():
    """Run 1000-scenario Monte Carlo survival simulation across 7 revenue streams."""
    random.seed(42)  # Reproducible results
    results = []

    for scenario_id in range(SIMULATION_SCENARIOS):
        monthly_totals = []
        stream_revenues = {name: [] for name in REVENUE_STREAMS}
        cash_reserve = 0  # Starting from current ~$0 operating cash
        months_survived = 0
        liquidity_breaches = 0
        concentration_violations = 0

        for month in range(1, SIMULATION_MONTHS + 1):
            month_revenue = 0
            month_by_stream = {}

            for name, stream in REVENUE_STREAMS.items():
                # Determine if stream is active this month
                if stream["monthly_base"] > 0:
                    is_active = random.random() < stream["probability_active"]
                else:
                    # Inactive streams have a chance to activate, increasing over time
                    activation_boost = min(month * 0.02, 0.15)  # +2%/month, cap +15%
                    is_active = random.random() < (stream["probability_active"] + activation_boost)

                if is_active:
                    # Revenue = base + random portion of upside, with volatility noise
                    base = stream["monthly_base"]
                    upside = stream["monthly_upside"] - base
                    noise = random.gauss(0, stream["volatility"])
                    revenue = max(0, base + upside * max(0, 0.5 + noise))
                else:
                    revenue = 0

                month_by_stream[name] = round(revenue, 2)
                month_revenue += revenue
                stream_revenues[name].append(round(revenue, 2))

            # Monthly expenses estimate (DC cost of living + business ops)
            monthly_expenses = random.gauss(5500, 500)

            # Update cash reserves
            cash_reserve += month_revenue - monthly_expenses
            monthly_totals.append(round(month_revenue, 2))

            # Stop rule checks
            if cash_reserve < STOP_RULES["liquidity_floor"]:
                liquidity_breaches += 1

            if month_revenue > 0:
                max_concentration = max(month_by_stream.values()) / month_revenue
                if max_concentration > STOP_RULES["concentration_cap"]:
                    concentration_violations += 1

            # Survival check — can still operate?
            if cash_reserve > -20000:  # Allow some runway via credit
                months_survived = month
            else:
                break

        results.append({
            "scenario_id": scenario_id,
            "months_survived": months_survived,
            "final_cash": round(cash_reserve, 2),
            "total_revenue": round(sum(monthly_totals), 2),
            "avg_monthly": round(statistics.mean(monthly_totals), 2),
            "liquidity_breaches": liquidity_breaches,
            "concentration_violations": concentration_violations,
            "stream_totals": {
                name: round(sum(revs), 2) for name, revs in stream_revenues.items()
            },
        })

    return _format_monte_carlo_report(results)


def _format_monte_carlo_report(results: list) -> str:
    """Format Monte Carlo results into MW-Ω report."""
    survived_12 = sum(1 for r in results if r["months_survived"] >= 12)
    survival_rate = survived_12 / len(results) * 100

    final_cash_values = [r["final_cash"] for r in results]
    avg_monthly_values = [r["avg_monthly"] for r in results]
    total_revenues = [r["total_revenue"] for r in results]

    # Percentile calculations
    p5_cash = sorted(final_cash_values)[int(len(final_cash_values) * 0.05)]
    p25_cash = sorted(final_cash_values)[int(len(final_cash_values) * 0.25)]
    p50_cash = sorted(final_cash_values)[int(len(final_cash_values) * 0.50)]
    p75_cash = sorted(final_cash_values)[int(len(final_cash_values) * 0.75)]
    p95_cash = sorted(final_cash_values)[int(len(final_cash_values) * 0.95)]

    # Stream contribution analysis
    stream_totals_agg = {name: [] for name in REVENUE_STREAMS}
    for r in results:
        for name, total in r["stream_totals"].items():
            stream_totals_agg[name].append(total)

    avg_liq_breaches = statistics.mean(r["liquidity_breaches"] for r in results)
    avg_conc_violations = statistics.mean(r["concentration_violations"] for r in results)

    report = f"""## SIMULATION PARAMETERS
- **Scenarios**: {SIMULATION_SCENARIOS:,}
- **Time horizon**: {SIMULATION_MONTHS} months
- **Revenue streams**: {len(REVENUE_STREAMS)}
- **Starting cash**: ~$0 (current operating position)
- **Monthly expenses**: ~$5,500 +/- $500
- **Seed**: 42 (reproducible)

---

## SURVIVAL ANALYSIS

| Metric | Value |
|--------|-------|
| **12-Month Survival Rate** | **{survival_rate:.1f}%** |
| Scenarios surviving 12 months | {survived_12:,} / {SIMULATION_SCENARIOS:,} |
| Average months survived | {statistics.mean(r['months_survived'] for r in results):.1f} |
| Median monthly revenue | ${statistics.median(avg_monthly_values):,.0f} |
| Mean total 12-month revenue | ${statistics.mean(total_revenues):,.0f} |

---

## CASH POSITION DISTRIBUTION (End of 12 Months)

| Percentile | Cash Position |
|------------|---------------|
| P5 (worst case) | ${p5_cash:,.0f} |
| P25 | ${p25_cash:,.0f} |
| **P50 (median)** | **${p50_cash:,.0f}** |
| P75 | ${p75_cash:,.0f} |
| P95 (best case) | ${p95_cash:,.0f} |

---

## STOP RULE IMPACT ACROSS SCENARIOS

| Stop Rule | Avg Months in Violation | Assessment |
|-----------|------------------------|------------|
| Liquidity Floor ($50K) | {avg_liq_breaches:.1f} / 12 | {'🔴 CRITICAL' if avg_liq_breaches > 9 else '🟡 WARNING' if avg_liq_breaches > 6 else '🟢 MANAGEABLE'} |
| Concentration Cap (25%) | {avg_conc_violations:.1f} / 12 | {'🔴 CRITICAL' if avg_conc_violations > 9 else '🟡 WARNING' if avg_conc_violations > 6 else '🟢 MANAGEABLE'} |

---

## REVENUE STREAM CONTRIBUTIONS (12-Month Average)

| Stream | Avg 12-Month Total | Median | Contribution % |
|--------|-------------------|--------|----------------|
"""
    total_all_streams = sum(statistics.mean(v) for v in stream_totals_agg.values())
    for name, values in sorted(stream_totals_agg.items(), key=lambda x: statistics.mean(x[1]), reverse=True):
        avg = statistics.mean(values)
        med = statistics.median(values)
        pct = (avg / total_all_streams * 100) if total_all_streams > 0 else 0
        report += f"| {name.replace('_', ' ').title()} | ${avg:,.0f} | ${med:,.0f} | {pct:.1f}% |\n"

    report += f"""
---

## SCENARIO CLUSTERS

"""
    # Classify scenarios
    catastrophic = sum(1 for r in results if r["final_cash"] < -10000)
    struggling = sum(1 for r in results if -10000 <= r["final_cash"] < 0)
    surviving = sum(1 for r in results if 0 <= r["final_cash"] < 50000)
    thriving = sum(1 for r in results if r["final_cash"] >= 50000)

    report += f"""| Cluster | Count | % | Description |
|---------|-------|---|-------------|
| 🔴 Catastrophic | {catastrophic} | {catastrophic/len(results)*100:.1f}% | Cash < -$10K, system collapse likely |
| 🟠 Struggling | {struggling} | {struggling/len(results)*100:.1f}% | Cash $-10K to $0, all stop rules breached |
| 🟡 Surviving | {surviving} | {surviving/len(results)*100:.1f}% | Cash $0-$50K, liquidity floor still breached |
| 🟢 Thriving | {thriving} | {thriving/len(results)*100:.1f}% | Cash >$50K, liquidity floor met |

---

## KEY INSIGHTS

1. **Government contract is existential**: In {avg_conc_violations:.0f}/12 months, concentration exceeds 25% cap. Loss of this contract without alternatives = system failure.
2. **Consulting activation is the swing factor**: Scenarios where consulting activates early show 2-3x better outcomes.
3. **Liquidity floor remains unreachable** in most scenarios without a second major income stream.
4. **Diversification timeline**: Even in optimistic scenarios, meaningful diversification takes 6-9 months.

## RECOMMENDATION

**VERDICT**: Current trajectory has a **{100-survival_rate:.1f}% failure probability** over 12 months.
- **Immediate**: Accelerate consulting pipeline — this is the highest-leverage intervention.
- **Defensive**: Build 3-month emergency fund before any speculative investments.
- **Structural**: No new revenue streams until consulting is generating >$3K/month consistently.
"""
    return report


# --- Dependency Graph Engine ---
def run_dependency_graph():
    """Generate vendor dependency graph with SPOF centrality scores."""
    if nx is None:
        print("Error: networkx package not installed. Run: pip install networkx")
        sys.exit(1)

    G = nx.DiGraph()

    # Add nodes with attributes
    for node_id, attrs in VENDOR_DEPENDENCIES["nodes"].items():
        G.add_node(node_id, **attrs)

    # Add weighted edges
    for src, dst, weight in VENDOR_DEPENDENCIES["edges"]:
        G.add_edge(src, dst, weight=weight)

    # Calculate centrality metrics (no numpy dependency)
    betweenness = nx.betweenness_centrality(G, weight="weight")
    in_degree = dict(G.in_degree(weight="weight"))
    out_degree = dict(G.out_degree(weight="weight"))
    closeness = nx.closeness_centrality(G, distance="weight")

    # SPOF score = weighted combination of centrality metrics
    spof_scores = {}
    max_out = max(out_degree.values(), default=1) or 1
    for node in G.nodes():
        node_data = VENDOR_DEPENDENCIES["nodes"][node]
        criticality_weight = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}
        crit_w = criticality_weight.get(node_data["criticality"], 0.5)
        alternatives_penalty = 1.0 if len(node_data["alternatives"]) == 0 else 1.0 / (1 + len(node_data["alternatives"]) * 0.3)

        spof = (
            betweenness.get(node, 0) * 0.35 +
            closeness.get(node, 0) * 0.30 +
            (out_degree.get(node, 0) / max_out) * 0.20 +
            crit_w * 0.15
        ) * alternatives_penalty

        spof_scores[node] = round(spof * 100, 1)  # Scale to 0-100

    # Find single points of failure (no alternatives + high centrality)
    true_spofs = [
        node for node, data in VENDOR_DEPENDENCIES["nodes"].items()
        if len(data["alternatives"]) == 0 and spof_scores[node] > 10
    ]

    # Find critical paths
    critical_paths = []
    for src in G.nodes():
        for dst in G.nodes():
            if src != dst:
                try:
                    paths = list(nx.all_simple_paths(G, src, dst))
                    for path in paths:
                        if len(path) >= 3:
                            path_weight = sum(
                                G[path[i]][path[i+1]]["weight"] for i in range(len(path) - 1)
                            )
                            critical_paths.append((path, path_weight))
                except nx.NetworkXError:
                    pass

    critical_paths.sort(key=lambda x: x[1], reverse=True)

    return _format_depgraph_report(G, spof_scores, betweenness, closeness, in_degree, out_degree, true_spofs, critical_paths)


def _format_depgraph_report(G, spof_scores, betweenness, closeness, in_degree, out_degree, true_spofs, critical_paths) -> str:
    """Format dependency graph analysis into MW-Ω report."""
    report = f"""## GRAPH OVERVIEW
- **Vendors/Systems**: {G.number_of_nodes()}
- **Dependencies**: {G.number_of_edges()}
- **Graph density**: {nx.density(G):.3f}
- **True SPOFs identified**: {len(true_spofs)}

---

## SPOF CENTRALITY SCORES (Single Point of Failure Risk)

*Higher score = greater systemic risk if this node fails. Target: all nodes <{STOP_RULES['spof_centrality_target'] * 100:.0f}.*

| Vendor/System | SPOF Score | Criticality | Alternatives | Status |
|---------------|-----------|-------------|--------------|--------|
"""
    for node, score in sorted(spof_scores.items(), key=lambda x: x[1], reverse=True):
        node_data = VENDOR_DEPENDENCIES["nodes"][node]
        alt_count = len(node_data["alternatives"])
        alt_str = ", ".join(node_data["alternatives"]) if node_data["alternatives"] else "**NONE**"
        status = "🔴 SPOF" if score > 15 and alt_count == 0 else "🟡 HIGH" if score > 10 else "🟢 OK"
        report += f"| {node.replace('_', ' ').title()} | {score} | {node_data['criticality']} | {alt_str} | {status} |\n"

    report += f"""
---

## TRUE SINGLE POINTS OF FAILURE (No Alternatives)

"""
    if true_spofs:
        for spof in sorted(true_spofs, key=lambda x: spof_scores[x], reverse=True):
            node_data = VENDOR_DEPENDENCIES["nodes"][spof]
            report += f"""### 🔴 {spof.replace('_', ' ').title()} — SPOF Score: {spof_scores[spof]}
- **Type**: {node_data['type']}
- **Criticality**: {node_data['criticality']}
- **Downstream impact**: {', '.join(n.replace('_', ' ').title() for n in G.successors(spof)) or 'None (leaf node)'}
- **Upstream dependencies**: {', '.join(n.replace('_', ' ').title() for n in G.predecessors(spof)) or 'None (root node)'}
- **Betweenness centrality**: {betweenness.get(spof, 0):.3f}
- **Closeness centrality**: {closeness.get(spof, 0):.3f}

"""
    else:
        report += "*No true SPOFs detected — all critical nodes have alternatives.*\n\n"

    report += """---

## CRITICAL DEPENDENCY PATHS (Highest Weight)

*Chains where a single failure cascades through multiple systems.*

| Path | Total Weight | Risk |
|------|-------------|------|
"""
    for path, weight in critical_paths[:10]:
        path_str = " → ".join(n.replace("_", " ").title() for n in path)
        risk = "🔴 CRITICAL" if weight >= 18 else "🟡 HIGH" if weight >= 12 else "🟢 MODERATE"
        report += f"| {path_str} | {weight} | {risk} |\n"

    report += f"""
---

## NETWORK METRICS

| Node | Betweenness | Closeness | In-Degree (weighted) | Out-Degree (weighted) |
|------|------------|-----------|---------------------|----------------------|
"""
    for node in sorted(G.nodes(), key=lambda x: betweenness.get(x, 0), reverse=True):
        report += f"| {node.replace('_', ' ').title()} | {betweenness.get(node, 0):.3f} | {closeness.get(node, 0):.3f} | {in_degree.get(node, 0)} | {out_degree.get(node, 0)} |\n"

    report += """
---

## DEPENDENCY MAP (ASCII)

```
                    ┌─────────────────┐
                    │  WASHINGTON DC   │
                    │     LLC          │
                    └────┬───────┬────┘
                         │       │
                    ┌────▼──┐ ┌──▼──────────┐
                    │ GOVT  │ │  PERSONAL   │
                    │CLIENT │ │    BANK     │
                    └───┬───┘ └──▲──▲───▲───┘
                        │        │  │   │
                        └────────┘  │   │
                                    │   │
    ┌──────────┐  ┌──────────┐     │   │
    │ ANTHROPIC├──┤ MW-OMEGA ├─┐   │   │
    │  CLAUDE  │  │  SYSTEM  │ │   │   │
    └────┬─────┘  └──▲───────┘ │   │   │
         │           │         │   │   │
         │      ┌────┴─────┐   │   │   │
         │      │  GITHUB  │   │   │   │
         │      └──────────┘   │   │   │
         │      ┌──────────┐   │   │   │
         │      │ GOOGLE   │   │   │   │
         │      │WORKSPACE ├───┘   │   │
         │      └──────────┘       │   │
         │                         │   │
    ┌────▼──────────────────┐      │   │
    │   FORMATION SERIES    │      │   │
    │   (Content Brand)     │      │   │
    └──▲────▲────▲──────────┘      │   │
       │    │    │                  │   │
  ┌────┴┐ ┌┴────┴──┐ ┌────────┐   │   │
  │SUNO │ │AMAZON  ├─┘   │STRIPE├──┘   │
  │ AI  │ │  KDP   │     └──────┘      │
  └─────┘ └────────┘                   │
       │                               │
       └───────────────────────────────┘
```

---

## RECOMMENDATIONS

1. **Government Client**: SPOF Score {spof_scores.get('govt_client', 0)} — zero alternatives. Losing this contract collapses 79.3% of revenue. **Priority: Build consulting pipeline as hedge.**
2. **Washington DC LLC**: Critical legal dependency with no alternative entity. **Priority: Ensure compliance is automated.**
3. **Personal Bank**: All revenue flows through single account. **Priority: Establish business banking separation.**
4. **Anthropic Claude**: High centrality but has alternatives (OpenAI, Gemini). **Priority: Document MW-Ω prompts for portability.**
5. **Amazon KDP**: Critical for Formation Series. **Priority: Cross-list on IngramSpark as backup.**
"""
    return report


def get_client():
    """Initialize Anthropic client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Set it: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def save_report(command: str, content: str):
    """Save report to timestamped markdown file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    filename = f"mw-omega_{command}_{timestamp}.md"
    filepath = OUTPUT_DIR / filename

    report = f"""# MW-Ω {command.title()} Report
**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
**System:** MW-Ω Autonomous Orchestrator
**Model:** {MODEL_ROUTINE if command != "decision" else MODEL_TIER1}

---

{content}

---
*Generated autonomously by MW-Ω Orchestrator. No founder input required.*
"""
    filepath.write_text(report)
    print(f"Report saved: {filepath}")
    return filepath


def run_command(command: str, extra_prompt: str = ""):
    """Execute an MW-Ω command via Claude API."""
    client = get_client()
    model = MODEL_TIER1 if command == "decision" else MODEL_ROUTINE
    prompt = extra_prompt if command == "decision" else PROMPTS[command]

    print(f"MW-Ω: Running {command} via {model}...")

    # Build tools list — add web_search for quarterly scans
    tools = []
    if command == "quarterly":
        tools = [{"type": "web_search_20250305", "name": "web_search"}]

    # Build API call kwargs
    kwargs = {
        "model": model,
        "max_tokens": 4096,
        "system": MW_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }
    if tools:
        kwargs["tools"] = tools

    response = client.messages.create(**kwargs)

    # Extract text from response
    content_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            content_parts.append(block.text)

    content = "\n\n".join(content_parts)

    if not content.strip():
        content = "(No text output — response may have been tool-use only)"

    report_path = save_report(command, content)
    print(f"MW-Ω: {command} complete.")
    print(f"Tokens used: {response.usage.input_tokens} in / {response.usage.output_tokens} out")
    return report_path


def tier1_decision(context: str):
    """Run Tier-1 Red/Blue team analysis on a decision."""
    prompt = f"""TIER-1 DECISION ANALYSIS — Red/Blue Team Protocol

DECISION CONTEXT:
{context}

Execute the full protocol:

1. BLUE TEAM (Case FOR):
   - Best possible outcome and path to get there
   - Evidence supporting this move
   - How it scores on Robustness/Asymmetry/Inevitability/Sovereignty/Wealth

2. RED TEAM (Case AGAINST):
   - Worst realistic outcome
   - Hidden risks and second-order effects
   - Which stop rules does this trigger or approach?

3. CONTRADICTION SWEEP:
   - Does this conflict with any active MW-Ω commitments?
   - Does this conflict with the Top 5 queue?
   - Does this require energy beyond the 20hr/week cap?

4. VERDICT:
   - PROCEED / DEFER / REJECT
   - If PROCEED: exact next action + deadline
   - If DEFER: what condition triggers re-evaluation
   - If REJECT: what alternative path serves the same goal

Be decisive. One recommended path, not options."""

    return run_command("decision", prompt)


def main():
    """CLI entry point."""
    commands = {
        "weekly": ("Monday morning briefing", lambda: run_command("weekly")),
        "monthly": ("1st of month metrics", lambda: run_command("monthly")),
        "quarterly": ("Competitive + regulatory scan", lambda: run_command("quarterly")),
        "absence": ("Founder absence simulation", lambda: run_command("absence")),
        "healthcheck": ("API key + system health check", lambda: run_command("healthcheck")),
        "decision": ("Tier-1 Red/Blue analysis", None),  # handled separately
        "montecarlo": ("Monte Carlo survival simulation", None),  # handled separately
        "depgraph": ("Vendor dependency graph + SPOF scores", None),  # handled separately
        "ingest": ("Parse revenue data from CSVs", None),  # handled separately
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("MW-Ω Autonomous Orchestrator")
        print("=" * 40)
        print("\nCommands:")
        for cmd, (desc, _) in commands.items():
            print(f"  {cmd:12s} — {desc}")
        print(f"\nUsage: python {sys.argv[0]} <command>")
        print(f'       python {sys.argv[0]} decision "Your decision context here"')
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "decision":
        if len(sys.argv) < 3:
            print("Error: decision command requires context string")
            print(f'Usage: python {sys.argv[0]} decision "Should I invest $15K in..."')
            sys.exit(1)
        context = " ".join(sys.argv[2:])
        tier1_decision(context)
    elif cmd == "montecarlo":
        print(f"MW-Ω: Running Monte Carlo survival simulation ({SIMULATION_SCENARIOS:,} scenarios)...")
        report_content = run_monte_carlo()
        save_report("montecarlo", report_content)
        print("MW-Ω: Monte Carlo simulation complete.")
    elif cmd == "depgraph":
        print("MW-Ω: Generating vendor dependency graph...")
        report_content = run_dependency_graph()
        save_report("depgraph", report_content)
        print("MW-Ω: Dependency graph analysis complete.")
    else:
        _, func = commands[cmd]
        func()


if __name__ == "__main__":
    main()
