#!/usr/bin/env python3
"""
MW-Ω Dashboard Updater
Reads the most recent report from reports/ and generates an updated docs/index.html.
"""

import os
import re
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")
DOCS_DIR = Path("docs")

# Dark theme template matching the dashboard design
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MW-Ω Operational Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.6; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 2rem 1rem; }}
  h1 {{ color: #ff6b35; font-size: 1.8rem; margin-bottom: 0.5rem; }}
  h2 {{ color: #ff6b35; font-size: 1.3rem; margin: 2rem 0 1rem; border-bottom: 1px solid #333; padding-bottom: 0.5rem; }}
  .subtitle {{ color: #888; font-size: 0.9rem; margin-bottom: 2rem; }}
  .card {{ background: #16213e; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; border-left: 3px solid #ff6b35; }}
  .card h3 {{ color: #ff6b35; margin-bottom: 0.5rem; font-size: 1.1rem; }}
  .status-green {{ color: #4caf50; }}
  .status-yellow {{ color: #ffc107; }}
  .status-red {{ color: #f44336; }}
  table {{ width: 100%; border-collapse: collapse; margin: 0.5rem 0; }}
  th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #2a2a4a; }}
  th {{ color: #ff6b35; font-size: 0.85rem; text-transform: uppercase; }}
  td {{ font-size: 0.9rem; }}
  a {{ color: #ff6b35; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .report-list {{ list-style: none; }}
  .report-list li {{ padding: 0.4rem 0; border-bottom: 1px solid #2a2a4a; }}
  .report-list li:last-child {{ border-bottom: none; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.75rem; font-weight: bold; }}
  .badge-green {{ background: #1b5e20; color: #4caf50; }}
  .badge-yellow {{ background: #4a3800; color: #ffc107; }}
  .badge-red {{ background: #4a0000; color: #f44336; }}
  pre {{ background: #0d1117; padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; margin: 0.5rem 0; white-space: pre-wrap; }}
  footer {{ text-align: center; color: #555; font-size: 0.8rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #2a2a4a; }}
</style>
</head>
<body>
<div class="container">
  <h1>MW-Ω Operational Dashboard</h1>
  <p class="subtitle">Autonomous Orchestrator Status | Last updated: {last_updated}</p>

  <h2>Stop Rules Status</h2>
  <div class="card">
    {stop_rules_html}
  </div>

  <h2>Execution Queue</h2>
  <div class="card">
    {queue_html}
  </div>

  <h2>Last Monte Carlo Summary</h2>
  <div class="card">
    <h3>Survival Simulation</h3>
    {montecarlo_html}
  </div>

  <h2>Latest Reports</h2>
  <div class="card">
    <ul class="report-list">
      {reports_html}
    </ul>
  </div>

  <footer>MW-Ω Autonomous Orchestrator | Updated by GitHub Actions</footer>
</div>
</body>
</html>"""


def get_sorted_reports():
    """Get all .md report files sorted by modification time (newest first)."""
    if not REPORTS_DIR.exists():
        return []
    reports = [f for f in REPORTS_DIR.glob("*.md") if f.name != "README.md"]
    return sorted(reports, key=lambda f: f.stat().st_mtime, reverse=True)


def extract_section(content, section_name):
    """Extract content under a markdown heading."""
    pattern = rf"#+\s*{re.escape(section_name)}.*?\n(.*?)(?=\n#+\s|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def parse_stop_rules(content):
    """Extract stop rules status from report content."""
    lines = content.split("\n")
    rules = []
    for line in lines:
        line_lower = line.lower()
        if "liquidity" in line_lower and ("floor" in line_lower or "$50k" in line_lower):
            rules.append(("Liquidity Floor ($50K)", "BREACHED", line.strip("- *")))
        elif "concentration" in line_lower and ("cap" in line_lower or "25%" in line_lower):
            rules.append(("Concentration Cap (25%)", "VIOLATED", line.strip("- *")))
        elif "founder" in line_lower and "irrelevance" in line_lower:
            rules.append(("Founder Irrelevance (60+)", "CRITICAL", line.strip("- *")))
        elif "spof" in line_lower and "centrality" in line_lower:
            rules.append(("SPOF Centrality (<15%)", "WARNING", line.strip("- *")))

    if not rules:
        return "<p>No stop rule data found in latest report.</p>"

    html = "<table><tr><th>Rule</th><th>Status</th><th>Detail</th></tr>"
    for name, status, detail in rules:
        badge_class = "badge-red" if status in ("BREACHED", "VIOLATED", "CRITICAL") else "badge-yellow"
        html += f'<tr><td>{name}</td><td><span class="badge {badge_class}">{status}</span></td><td>{detail[:80]}</td></tr>'
    html += "</table>"
    return html


def parse_queue(content):
    """Extract execution queue from report content."""
    queue_section = extract_section(content, "QUEUE")
    if not queue_section:
        queue_section = extract_section(content, "Top 5")
    if not queue_section:
        queue_section = extract_section(content, "EXECUTION")

    if not queue_section:
        return "<p>No queue data found in latest report.</p>"

    items = re.findall(r"\d+\.\s*(.+)", queue_section)
    if not items:
        return f"<pre>{queue_section[:500]}</pre>"

    html = "<ol style='padding-left: 1.2rem;'>"
    for item in items[:7]:
        html += f"<li>{item.strip()}</li>"
    html += "</ol>"
    return html


def parse_montecarlo(reports):
    """Find and extract Monte Carlo summary from reports."""
    for report in reports:
        if "montecarlo" in report.name.lower():
            content = report.read_text(encoding="utf-8", errors="replace")
            survival_match = re.search(r"12-Month Survival Rate\*?\*?\s*\|\s*\*?\*?(\d+\.?\d*%)", content)
            median_match = re.search(r"P50 \(median\)\*?\*?\s*\|\s*\*?\*?\$?([\-\d,]+)", content)

            summary = f"<p><strong>Report:</strong> {report.name}</p>"
            if survival_match:
                summary += f"<p><strong>12-Month Survival Rate:</strong> {survival_match.group(1)}</p>"
            if median_match:
                summary += f"<p><strong>Median Cash Position (P50):</strong> ${median_match.group(1)}</p>"

            verdict_section = extract_section(content, "RECOMMENDATION")
            if not verdict_section:
                verdict_section = extract_section(content, "VERDICT")
            if verdict_section:
                summary += f"<pre>{verdict_section[:400]}</pre>"

            return summary

    return "<p>No Monte Carlo report found yet. Trigger via GitHub Actions → montecarlo.</p>"


def build_reports_list(reports):
    """Build HTML list of recent reports."""
    if not reports:
        return "<li>No reports found.</li>"

    html = ""
    for report in reports[:15]:
        name = report.name
        # Determine report type from filename
        if "weekly" in name:
            badge = '<span class="badge badge-green">WEEKLY</span>'
        elif "monthly" in name:
            badge = '<span class="badge badge-yellow">MONTHLY</span>'
        elif "quarterly" in name:
            badge = '<span class="badge badge-red">QUARTERLY</span>'
        elif "montecarlo" in name:
            badge = '<span class="badge badge-yellow">MONTE CARLO</span>'
        elif "depgraph" in name:
            badge = '<span class="badge badge-green">DEPGRAPH</span>'
        elif "healthcheck" in name:
            badge = '<span class="badge badge-green">HEALTH</span>'
        elif "FAILURE" in name:
            badge = '<span class="badge badge-red">FAILURE</span>'
        else:
            badge = '<span class="badge badge-green">REPORT</span>'

        html += f"<li>{badge} {name}</li>\n"

    return html


def main():
    reports = get_sorted_reports()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Parse the latest weekly/monthly report for stop rules and queue
    stop_rules_html = "<p>Awaiting first report with stop rule data.</p>"
    queue_html = "<p>Awaiting first report with queue data.</p>"

    for report in reports:
        if any(t in report.name for t in ["weekly", "monthly"]):
            content = report.read_text(encoding="utf-8", errors="replace")
            parsed_rules = parse_stop_rules(content)
            if "No stop rule" not in parsed_rules:
                stop_rules_html = parsed_rules
            parsed_queue = parse_queue(content)
            if "No queue" not in parsed_queue:
                queue_html = parsed_queue
            break

    montecarlo_html = parse_montecarlo(reports)
    reports_html = build_reports_list(reports)

    # Generate final HTML
    html = HTML_TEMPLATE.format(
        last_updated=now,
        stop_rules_html=stop_rules_html,
        queue_html=queue_html,
        montecarlo_html=montecarlo_html,
        reports_html=reports_html,
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DOCS_DIR / "index.html"
    output_path.write_text(html)
    print(f"Dashboard updated: {output_path}")


if __name__ == "__main__":
    main()
