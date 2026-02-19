#!/usr/bin/env python3
"""
MW-Ω Notion Sync
Reads the latest report from reports/ and syncs key metrics to the
MW-Ω Command Center dashboard in Notion.

Requires environment variables:
  NOTION_API_KEY       - Notion integration token
  NOTION_DASHBOARD_ID  - Page ID of the Dashboard section
"""

import os
import re
import json
import requests
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_DASHBOARD_ID = os.environ.get("NOTION_DASHBOARD_ID", "")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def get_latest_report():
    """Get the most recent .md report file."""
    reports = [f for f in REPORTS_DIR.glob("*.md") if f.name != "README.md" and "FAILURE" not in f.name]
    if not reports:
        return None
    return sorted(reports, key=lambda f: f.stat().st_mtime, reverse=True)[0]


def extract_key_metrics(content):
    """Extract key metrics from report content for Notion blocks."""
    metrics = {
        "report_type": "unknown",
        "generated": "",
        "highlights": [],
    }

    # Detect report type from title
    title_match = re.search(r"# MW-Ω (\w+) Report", content)
    if title_match:
        metrics["report_type"] = title_match.group(1)

    # Extract generation timestamp
    gen_match = re.search(r"\*\*Generated:\*\*\s*(.+)", content)
    if gen_match:
        metrics["generated"] = gen_match.group(1)

    # Extract key lines (bullet points, table rows with data)
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        # Capture stop rule mentions
        if any(kw in line.lower() for kw in ["liquidity", "concentration", "irrelevance", "spof", "survival rate"]):
            if line.startswith("|") or line.startswith("-") or line.startswith("*"):
                cleaned = line.strip("|-* ")
                if cleaned and len(cleaned) > 5:
                    metrics["highlights"].append(cleaned[:200])

    return metrics


def build_notion_blocks(report_name, content, metrics):
    """Build Notion block children from report content."""
    blocks = []

    # Header
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": f"Latest: {metrics['report_type']} Report"}}]
        }
    })

    # Metadata
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": f"Source: {report_name}\nGenerated: {metrics['generated']}\nSynced: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"}}
            ]
        }
    })

    # Divider
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # Key highlights
    if metrics["highlights"]:
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"type": "text", "text": {"content": "Key Metrics"}}]
            }
        })
        for highlight in metrics["highlights"][:10]:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": highlight}}]
                }
            })

    # Full report as toggle
    # Notion has a 2000 char limit per rich_text content, so chunk it
    chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
    toggle_children = []
    for chunk in chunks[:20]:  # Max 20 chunks to stay within API limits
        toggle_children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            }
        })

    blocks.append({
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": "Full Report"}}],
            "children": toggle_children[:5],  # Notion limits nested children
        }
    })

    return blocks


def clear_page_content(page_id, headers):
    """Remove existing children blocks from a page to replace with fresh content."""
    # Get existing blocks
    response = requests.get(
        f"{NOTION_API_URL}/blocks/{page_id}/children?page_size=100",
        headers=headers
    )
    if response.status_code != 200:
        print(f"Warning: Could not fetch existing blocks: {response.status_code}")
        return

    data = response.json()
    for block in data.get("results", []):
        block_id = block["id"]
        requests.delete(f"{NOTION_API_URL}/blocks/{block_id}", headers=headers)


def sync_to_notion(report_path):
    """Sync a report to the Notion dashboard page."""
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    content = report_path.read_text(encoding="utf-8", errors="replace")
    metrics = extract_key_metrics(content)
    blocks = build_notion_blocks(report_path.name, content, metrics)

    # Clear existing content and replace
    clear_page_content(NOTION_DASHBOARD_ID, headers)

    # Append new blocks
    response = requests.patch(
        f"{NOTION_API_URL}/blocks/{NOTION_DASHBOARD_ID}/children",
        headers=headers,
        json={"children": blocks}
    )

    if response.status_code == 200:
        print(f"Notion sync successful: {report_path.name} → Dashboard")
    else:
        print(f"Notion sync failed ({response.status_code}): {response.text[:200]}")
        raise SystemExit(1)


def main():
    if not NOTION_API_KEY:
        print("NOTION_API_KEY not set — skipping Notion sync.")
        return
    if not NOTION_DASHBOARD_ID:
        print("NOTION_DASHBOARD_ID not set — skipping Notion sync.")
        return

    report = get_latest_report()
    if not report:
        print("No reports found to sync.")
        return

    print(f"MW-Ω Notion Sync: {report.name}")
    sync_to_notion(report)


if __name__ == "__main__":
    main()
