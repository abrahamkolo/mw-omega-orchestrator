# Demo Mode

Run the orchestrator demo without API keys:

```bash
python3 demo/run_demo.py
```

This demonstrates:
* 39-document dependency graph construction
* Monte Carlo deployment risk simulation (10K trials)
* Decision compression algorithm

For full mode with AI-powered orchestration, set `ANTHROPIC_API_KEY` in your environment.
