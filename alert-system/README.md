# Alert System

Monitors ranking changes and identifies significant movements in stock rankings between analysis runs.

## Overview

The Alert System compares current rankings with the most recent historical rankings to detect:
- **Grade Upgrades**: Stocks moving into Grade A or A+
- **Significant Movers**: Stocks with large ranking changes (+/- 50 positions)
- **New Top 50 Entries**: Stocks newly entering the elite top 50

## Features

- **Automated Comparison**: Compares current vs. previous rankings
- **Multiple Alert Types**: Grade upgrades, improvers, decliners, new top entries
- **Detailed Reports**: Console output and Excel files
- **Historical Integration**: Works with historical tracker data
- **Timestamped Outputs**: Each alert run is saved with timestamp

## Usage

```bash
cd alert-system
python alert_system.py
```

**Note**: Requires at least two ranking runs to generate alerts. On first run, it will indicate no previous data is available.

## Alert Types

### 1. Grade Upgrades to A/A+
Identifies stocks that have upgraded from lower grades (B+, B, C, D, F) to Grade A or A+.

**Why it matters**: These stocks have significantly improved their overall ranking and may represent emerging opportunities.

**Example**:
```
Ticker   Company                    Sector          Old Grade    New Grade    Rank Change
NVDA     NVIDIA Corporation         Technology      B+           A+           +45
```

### 2. Significant Improvers
Stocks that improved their composite score by 50+ positions.

**Why it matters**: Large improvements may indicate improving fundamentals or market recognition of value.

**Example**:
```
Ticker   Company                    Sector          Old Rank     New Rank     Change
AMD      Advanced Micro Devices     Technology      150          85           -65
```

### 3. Significant Decliners
Stocks that declined in composite score by 50+ positions.

**Why it matters**: Large declines may signal deteriorating fundamentals or increased valuation concerns.

**Example**:
```
Ticker   Company                    Sector          Old Rank     New Rank     Change
XYZ      Example Corp               Financials      75           140          +65
```

### 4. New Top 50 Entries
Stocks that newly entered the top 50 rankings.

**Why it matters**: These are newly identified elite opportunities worth investigating.

**Example**:
```
Ticker   Company                    Sector          New Rank     Previous Rank    Improvement
GOOGL    Alphabet Inc.              Technology      48           125              +77
```

## Output Files

Each run generates a timestamped Excel file: `investment_alerts_YYYYMMDD_HHMM.xlsx`

### Sheets Included:

1. **Summary**: Overview of all alert types and counts
2. **Grade Upgrades**: Detailed list of stocks upgraded to A/A+
3. **Significant Improvers**: Stocks with +50 rank improvement
4. **Significant Decliners**: Stocks with -50 rank decline
5. **New Top 50**: Stocks newly entering top 50

## Integration with Other Tools

The Alert System works with:
- **Master Aggregator**: Source of current rankings
- **Historical Tracker**: Source of previous rankings
- **Portfolio Builder**: Identify new candidates for portfolios

## Workflow

1. Run master aggregator to generate current rankings
2. Historical tracker automatically saves dated copy
3. Run alert system to compare current vs. previous
4. Review alerts for actionable opportunities
5. Investigate flagged stocks in detail

## Customization

You can adjust alert thresholds in the code:

```python
# Change significant mover threshold (default: 50)
improvers, decliners = detect_significant_movers(current_df, previous_df, threshold=50)

# Change top N threshold (default: 50)
new_top = detect_new_top_stocks(current_df, previous_df, top_n=50)
```

## Example Output

```
================================================================================
INVESTMENT ALERT SYSTEM - RANKING CHANGES DETECTED
================================================================================

🎯 GRADE UPGRADES TO A/A+ (5 stocks)
--------------------------------------------------------------------------------
Ticker   Company                                  Sector                    Old Grade    New Grade    Rank Change
NVDA     NVIDIA Corporation                       Technology                B+           A+           +45
AMD      Advanced Micro Devices                   Technology                B            A            +38
...

📈 SIGNIFICANT IMPROVERS (12 stocks with +50 rank improvement)
--------------------------------------------------------------------------------
Ticker   Company                                  Sector                    Old Rank     New Rank     Change
AMD      Advanced Micro Devices                   Technology                150          85           -65
GOOGL    Alphabet Inc.                            Technology                125          48           -77
...

⭐ NEW TOP 50 ENTRIES (3 stocks)
--------------------------------------------------------------------------------
Ticker   Company                                  Sector                    New Rank     Previous Rank    Improvement
GOOGL    Alphabet Inc.                            Technology                48           125              +77
...
```

## Best Practices

1. **Run Regularly**: Execute after each master aggregator run
2. **Investigate Upgrades**: Research stocks newly entering Grade A/A+
3. **Verify Improvers**: Understand why stocks improved significantly
4. **Monitor Decliners**: Check if portfolio holdings are declining
5. **Track New Top 50**: Consider adding to watchlist or portfolio
6. **Combine with Research**: Use alerts as starting point, not final decision

## Limitations

- Requires at least two ranking runs for comparison
- Only compares to most recent previous run (not long-term trends)
- Does not analyze reasons for changes
- No email/notification integration (manual review required)

## Future Enhancements

Potential improvements:
- Email/SMS notifications for critical alerts
- Configurable alert thresholds per user
- Long-term trend analysis (multiple periods)
- Sector-specific alert thresholds
- Integration with portfolio holdings
- Automated watchlist updates

## Notes

- First run will show "No previous rankings available"
- Alerts are generated by comparing to most recent historical file
- All alerts are saved to timestamped Excel files
- Console output shows top 10 per category
- Excel files contain complete lists