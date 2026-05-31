# Historical Investment Rankings Tracker

Track changes in investment rankings over time to identify consistent performers and trending stocks.

## Overview

The Historical Tracker automatically saves dated snapshots of master rankings and provides comparison tools to analyze how stocks move up or down over time.

## Features

- **Automatic Snapshots**: Save dated copies of master rankings
- **Trend Analysis**: Compare rankings between any two dates
- **Biggest Movers**: Identify stocks with largest rank improvements/declines
- **New Entries**: Track stocks entering top 100
- **Dropped Stocks**: Monitor stocks falling out of top 100
- **Comparison Reports**: Generate detailed Excel reports

## Usage

### Create Snapshot and Generate Report

```bash
cd historical-tracker
python historical_tracker.py
```

This will:
1. Create a dated snapshot in `historical-data/rankings_YYYY-MM-DD.xlsx`
2. Compare with previous snapshots (if available)
3. Generate a comparison report

### Manual Snapshot Creation

```python
from historical_tracker import create_historical_snapshot

snapshot_file = create_historical_snapshot()
```

### Compare Specific Dates

```python
from historical_tracker import compare_rankings

# Compare oldest vs newest
comparison, date1, date2 = compare_rankings()

# Compare specific dates
comparison, date1, date2 = compare_rankings('2024-01-15', '2024-02-15')
```

## Output Files

### Snapshots
- Location: `historical-data/rankings_YYYY-MM-DD.xlsx`
- Content: Complete copy of master rankings from that date
- Format: Same as master_investment_rankings.xlsx

### Comparison Reports
- Location: `historical-data/comparison_DATE1_vs_DATE2.xlsx`
- Content: Side-by-side comparison with rank changes
- Columns:
  - Ticker, Company
  - Composite_Score (both dates)
  - Investment_Grade (both dates)
  - Rank_Change (positive = improved)
  - Status (Stable/New Entry/Dropped Out)

## Interpretation

### Rank Change
- **Positive number**: Stock improved (moved to lower/better rank)
- **Negative number**: Stock declined (moved to higher/worse rank)
- **Example**: Change of +50 means stock improved by 50 positions

### Status
- **Stable**: Stock in top 100 on both dates
- **New Entry**: Stock entered top 100
- **Dropped Out**: Stock fell out of top 100

## Best Practices

1. **Regular Snapshots**: Run weekly or monthly for trend analysis
2. **Long-term Tracking**: Keep at least 6-12 months of history
3. **Consistent Performers**: Focus on stocks with stable high rankings
4. **Avoid Volatility**: Be cautious of stocks with large rank swings
5. **Combine with Research**: Use trends as one factor in decision-making

## Example Workflow

```bash
# Week 1: Initial snapshot
python historical_tracker.py

# Week 2: Create new snapshot and see changes
python historical_tracker.py

# Week 3: Continue tracking
python historical_tracker.py

# After several weeks: Review trends
# - Which stocks consistently rank in top 50?
# - Which stocks are improving over time?
# - Which stocks are declining?
```

## Use Cases

### Identify Consistent Winners
Stocks that maintain top rankings over multiple periods are likely high-quality opportunities.

### Catch Rising Stars
Stocks steadily improving in rankings may be undervalued opportunities being discovered.

### Avoid Falling Knives
Stocks with declining rankings may have deteriorating fundamentals.

### Validate Strategy
Track if your investment picks maintain their rankings over time.

## Integration with Other Tools

The Historical Tracker works with output from:
- Master Aggregator (primary input)
- All 8 investment analysis tools (indirectly)

## Limitations

- Requires at least 2 snapshots for comparison
- Historical data only as good as underlying tool accuracy
- Past trends don't guarantee future performance
- Should be combined with fundamental research

## License

Educational purposes only. Not investment advice.