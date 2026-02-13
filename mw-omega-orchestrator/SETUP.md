# MW-Ω Autonomous Orchestrator — Setup Guide

## What This Does

Makes Claude run automatically on a schedule — without you opening a browser.
- **Every Monday 9am**: Weekly briefing (stop rules, queue, energy)
- **1st of every month**: Metrics snapshot (concentration, liquidity, assets)
- **Quarterly (Mar/Jun/Sep/Dec)**: Competitive scan with live web search
- **On-demand**: Tier-1 decision analysis anytime you trigger it

Reports save as markdown files in the `reports/` folder of your GitHub repo.

---

## Setup (15 minutes)

### Step 1: Get Your Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)
5. Save it somewhere safe — you'll need it in Step 4

### Step 2: Create the GitHub Repo

Open **PowerShell** and paste these one at a time:

```powershell
cd ~
cd mw-omega-orchestrator
git add .
git commit -m "MW-Ω Orchestrator: initial deploy"
git branch -M main
git remote add origin git@github.com:abrahamkolo/mw-omega-orchestrator.git
git push -u origin main
```

**If the repo doesn't exist yet on GitHub:**
1. Go to https://github.com/new
2. Name: `mw-omega-orchestrator`
3. Set to **Private**
4. Do NOT add README or .gitignore
5. Click **Create repository**
6. Then run the commands above

### Step 3: Add Your API Key as a Secret

1. Go to your repo on GitHub: `github.com/abrahamkolo/mw-omega-orchestrator`
2. Click **Settings** (tab at the top)
3. Left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `ANTHROPIC_API_KEY`
6. Value: paste your `sk-ant-...` key
7. Click **Add secret**

### Step 4: Test It

1. Go to your repo on GitHub
2. Click **Actions** tab
3. Click **MW-Ω Orchestrator** in the left sidebar
4. Click **Run workflow** button (top right)
5. Select **weekly** from the dropdown
6. Click **Run workflow**
7. Wait 1-2 minutes — check the `reports/` folder for output

---

## How It Works

GitHub Actions runs the Python script on a cron schedule for free.
The script calls the Anthropic API with the MW-Ω system prompt baked in.
Claude generates the briefing/report.
The report saves as a markdown file and auto-commits to the repo.

**Cost**: ~$0.15 per weekly/monthly run (Sonnet). ~$1.50 for Tier-1 decisions (Opus).
Roughly $8-10/month for full automation.

---

## Manual Runs

From your computer (after `pip install anthropic python-dotenv`):

```bash
# Set your key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Run commands
python mw_orchestrator.py weekly
python mw_orchestrator.py monthly
python mw_orchestrator.py quarterly
python mw_orchestrator.py absence
python mw_orchestrator.py decision "Should I invest $15K in workforce multifamily?"
```

---

## Troubleshooting

**"Error: ANTHROPIC_API_KEY not set"**
→ Make sure you added the secret in Step 3.

**GitHub Actions not running**
→ Check Actions tab. Make sure workflows are enabled (Settings → Actions → General → Allow all actions).

**Reports not appearing**
→ Check the Actions run log for errors. Most common: API key issue or rate limit.
