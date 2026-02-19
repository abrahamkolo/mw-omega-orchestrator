#!/usr/bin/env python3
"""
MW-Ω Revenue Data Parser
Scans data/ for CSV files, parses platform-specific formats,
and outputs a consolidated revenue summary JSON.
"""

import csv
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "revenue_summary.json"

# Known platform CSV patterns
PLATFORM_PARSERS = {
    "kdp_royalties.csv": "kdp",
    "substack_earnings.csv": "substack",
    "suno_revenue.csv": "generic",
    "spotify_royalties.csv": "generic",
    "spring_sales.csv": "generic",
}


def parse_kdp(filepath):
    """Parse Amazon KDP royalties CSV: Date, Title, Marketplace, Royalty"""
    revenues = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row.get("Royalty", row.get("royalty", 0)))
                revenues.append({
                    "date": row.get("Date", row.get("date", "")),
                    "source": "kdp_books",
                    "detail": row.get("Title", row.get("title", "")),
                    "amount": amount,
                })
            except (ValueError, KeyError):
                continue
    return revenues


def parse_substack(filepath):
    """Parse Substack earnings CSV: Date, Subscribers, Revenue"""
    revenues = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row.get("Revenue", row.get("revenue", 0)))
                revenues.append({
                    "date": row.get("Date", row.get("date", "")),
                    "source": "substack_newsletter",
                    "detail": f"Subscribers: {row.get('Subscribers', row.get('subscribers', 'N/A'))}",
                    "amount": amount,
                })
            except (ValueError, KeyError):
                continue
    return revenues


def parse_generic(filepath):
    """Parse generic CSV: Date, Source, Amount"""
    revenues = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row.get("Amount", row.get("amount", 0)))
                source = row.get("Source", row.get("source", filepath.stem))
                revenues.append({
                    "date": row.get("Date", row.get("date", "")),
                    "source": source.lower().replace(" ", "_"),
                    "detail": "",
                    "amount": amount,
                })
            except (ValueError, KeyError):
                continue
    return revenues


def scan_and_parse():
    """Scan data/ directory and parse all recognized CSV files."""
    all_revenues = []
    parsed_files = []
    missing_files = []

    for filename, parser_type in PLATFORM_PARSERS.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            if parser_type == "kdp":
                records = parse_kdp(filepath)
            elif parser_type == "substack":
                records = parse_substack(filepath)
            else:
                records = parse_generic(filepath)
            all_revenues.extend(records)
            parsed_files.append(filename)
            print(f"  Parsed {filename}: {len(records)} records")
        else:
            missing_files.append(filename)

    # Also parse any other CSV files not in the known list
    for csvfile in DATA_DIR.glob("*.csv"):
        if csvfile.name not in PLATFORM_PARSERS:
            records = parse_generic(csvfile)
            all_revenues.extend(records)
            parsed_files.append(csvfile.name)
            print(f"  Parsed {csvfile.name} (generic): {len(records)} records")

    return all_revenues, parsed_files, missing_files


def build_summary(revenues):
    """Build consolidated summary from parsed revenue records."""
    total_revenue = sum(r["amount"] for r in revenues)

    # Group by source
    by_stream = {}
    for r in revenues:
        source = r["source"]
        by_stream[source] = by_stream.get(source, 0) + r["amount"]

    # Calculate concentration
    concentration = {}
    if total_revenue > 0:
        for source, amount in by_stream.items():
            concentration[source] = round(amount / total_revenue, 4)

    # Estimate liquidity (simple: total revenue as proxy)
    liquidity_estimate = total_revenue

    return {
        "total_revenue": round(total_revenue, 2),
        "by_stream": {k: round(v, 2) for k, v in sorted(by_stream.items(), key=lambda x: x[1], reverse=True)},
        "concentration": {k: v for k, v in sorted(concentration.items(), key=lambda x: x[1], reverse=True)},
        "liquidity_estimate": round(liquidity_estimate, 2),
    }


def main():
    print("MW-Omega Revenue Data Ingestion")
    print("=" * 40)

    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)
        print("Created data/ directory.")

    revenues, parsed_files, missing_files = scan_and_parse()

    if missing_files:
        print(f"\n  Missing (no data yet): {', '.join(missing_files)}")

    if not revenues:
        print("\nNo revenue data found. Place CSV files in data/ directory.")
        print("See data/README.md for expected formats.")
        # Still write an empty summary so the system knows data was checked
        summary = {
            "total_revenue": 0,
            "by_stream": {},
            "concentration": {},
            "liquidity_estimate": 0,
            "data_source": "no_data",
            "parsed_at": datetime.utcnow().isoformat() + "Z",
            "files_parsed": [],
            "files_missing": missing_files,
        }
    else:
        summary = build_summary(revenues)
        summary["data_source"] = "live"
        summary["parsed_at"] = datetime.utcnow().isoformat() + "Z"
        summary["files_parsed"] = parsed_files
        summary["files_missing"] = missing_files
        summary["record_count"] = len(revenues)

    OUTPUT_FILE.write_text(json.dumps(summary, indent=2))
    print(f"\nSummary written to {OUTPUT_FILE}")
    print(f"Total revenue: ${summary['total_revenue']:,.2f}")
    print(f"Data source: {summary['data_source']}")


if __name__ == "__main__":
    main()
