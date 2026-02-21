[![Tests](https://github.com/abrahamkolo/mw-omega-orchestrator/actions/workflows/test.yml/badge.svg)](https://github.com/abrahamkolo/mw-omega-orchestrator/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# MW-Omega Orchestrator

Deterministic orchestration engine for institutional governance stacks -- dependency graphs, Monte Carlo simulation, decision compression.

> **Start here:** `python3 demo/run_demo.py` -- runs in 2 seconds, no setup needed.

## What It Does

1. **Dependency Graph** -- maps 39-document constitutional stack with layer relationships
2. **Monte Carlo Simulation** -- 10,000-trial deployment risk analysis (deterministic seed)
3. **Decision Compression** -- prioritizes tasks by impact x urgency / effort

## Run It Now

**Demo mode** (no API keys needed):
```bash
git clone https://github.com/abrahamkolo/mw-omega-orchestrator.git
cd mw-omega-orchestrator
python3 demo/run_demo.py
```

**Run tests** (24 tests across 3 modules):
```bash
pip install pytest
pytest tests/ -v
```

**Test coverage:**

| Module | Tests | What's Verified |
|---|---|---|
| Dependency Graph | 8 | 39-doc structure, layer distribution, no self-deps, sequential IDs |
| Monte Carlo | 8 | Deterministic output, pass rates, verdict logic, edge cases |
| Decision Compressor | 8 | Priority scoring, sort order, effort penalty, empty input |

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
| `tests/` | 24 pytest tests (3 modules) |
| `.github/workflows/test.yml` | CI matrix: Python 3.9, 3.11, 3.12 |
| `pyproject.toml` | Package metadata and build config |
| `reports/` | Generated briefings and analyses |

## License

MIT. Part of the MW Infrastructure Stack.

