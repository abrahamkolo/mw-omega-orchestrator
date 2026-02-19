# MW-Ω Revenue Data Directory

Place CSV exports here. The orchestrator will auto-parse on next `ingest` run.

## Expected Files

### kdp_royalties.csv (Amazon KDP)
```
Date,Title,Marketplace,Royalty
2026-01-15,Formation Series Vol 1,Amazon.com,12.50
2026-01-15,Formation Series Vol 2,Amazon.co.uk,3.20
```

### substack_earnings.csv
```
Date,Subscribers,Revenue
2026-01-01,150,0.00
2026-02-01,175,25.00
```

### suno_revenue.csv
```
Date,Source,Amount
2026-01-15,Suno Royalties,15.00
```

### spotify_royalties.csv
```
Date,Source,Amount
2026-01-15,Spotify Streams,8.50
```

### spring_sales.csv
```
Date,Source,Amount
2026-01-15,Spring Merch,22.00
```

### Generic CSV (any platform)
```
Date,Source,Amount
2026-01-15,Platform Name,100.00
```

## Output

After running `python mw_orchestrator.py ingest`, a `revenue_summary.json` file will be generated in this directory with consolidated totals.
