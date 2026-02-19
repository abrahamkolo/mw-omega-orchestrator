# Contributing to MW-Ω Orchestrator

## Branch Strategy
- `main` — production. Only merge via PR from `dev`.
- `dev` — development. All changes go here first.

## Workflow
1. Make changes on `dev` branch
2. Test locally: `python mw_orchestrator.py weekly`
3. Push to `dev`
4. Create PR from `dev` → `main`
5. Review diff, then merge

## Testing Commands
```bash
python mw_orchestrator.py weekly      # Quick test
python mw_orchestrator.py montecarlo  # Full simulation
python mw_orchestrator.py depgraph    # Dependency check
```

## Secrets Required
* `ANTHROPIC_API_KEY` — Anthropic API key for Claude calls
