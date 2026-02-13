#!/usr/bin/env python3
"""
MW-Ω Autonomous Orchestrator
Converts Claude from reactive to proactive by self-executing on schedule.

Commands:
  weekly     - Monday morning briefing: stop rules, queue, energy check
  monthly    - 1st of month: metrics snapshot, concentration check
  quarterly  - Competitive scan, regulatory monitor, vendor health
  absence    - Founder absence simulation test
  decision   - Tier-1 Red/Blue team analysis (requires context arg)

Usage:
  python mw_orchestrator.py weekly
  python mw_orchestrator.py decision "Should I invest $15K in workforce multifamily?"
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

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
}


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
        "decision": ("Tier-1 Red/Blue analysis", None),  # handled separately
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
    else:
        _, func = commands[cmd]
        func()


if __name__ == "__main__":
    main()
