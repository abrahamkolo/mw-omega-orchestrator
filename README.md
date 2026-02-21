[![Tests](https://github.com/abrahamkolo/mw-omega-orchestrator/actions/workflows/test.yml/badge.svg)](https://github.com/abrahamkolo/mw-omega-orchestrator/actions/workflows/test.yml)

# MW-Omega Orchestrator

Deterministic orchestration engine for institutional governance stacks. Dependency graphs, Monte Carlo simulation, and decision compression.

## Quick Start (No API Keys)

```bash
git clone https://github.com/abrahamkolo/mw-omega-orchestrator.git
cd mw-omega-orchestrator
python3 demo/run_demo.py
```

## What It Does

- **Dependency Graph Construction** — Maps the 39-document constitutional stack with layer-aware traversal
- **Monte Carlo Deployment Simulation** — 10K-trial risk analysis with deterministic seeding
- **Decision Compression** — Weighted priority scoring for execution queue optimization
- **Scheduled Orchestration** — Automated briefings via GitHub Actions + Anthropic API

## Full Mode

Requires `ANTHROPIC_API_KEY` for AI-powered orchestration:

```bash
pip install anthropic python-dotenv
export ANTHROPIC_API_KEY="sk-ant-..."
python mw_orchestrator.py weekly
```

See [SETUP.md](SETUP.md) for complete setup instructions including GitHub Actions scheduling and Notion sync.

## Architecture

| Component | Purpose |
|---|---|
| `mw_orchestrator.py` | Core orchestration engine |
| `demo/run_demo.py` | Zero-dependency demo mode |
| `.github/workflows/` | Scheduled automation |
| `reports/` | Generated briefings and analyses |
| `data/` | Revenue and operational data |

## License

Proprietary. Part of the MW Infrastructure Stack.
