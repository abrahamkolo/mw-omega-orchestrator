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

## Proof (60-Second Demo)

Run the demo and see deterministic output in under 60 seconds:

```bash
python demo/run_demo.py
```

Sample output:

```
[1/3] Building 39-document dependency graph...
  Layer 0: 6 documents
  Layer 1: 3 documents
  Layer 2: 14 documents
  Layer 3: 16 documents
  Total: 39 documents -- all CANONICAL

[2/3] Running Monte Carlo deployment simulation...
  Trials: 10,000
  Deployment pass rate: 98.2%
  Average minimum score: 88.5
  Verdict: DEPLOY

[3/3] Compressing execution queue...
  1. [7.9] LLC formation
  2. [7.1] Ethereum attestation
  3. [6.9] Stripe integration
  4. [6.7] Arweave upload
  5. [5.7] Per-document DOIs
```

Full test suite (24 tests):

```bash
pytest tests/ -v
```

All 24 tests pass across 3 modules: dependency graph (8), Monte Carlo simulation (8), decision compression (8).

> [Full verification proof](assets/verification-proof.md)

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

