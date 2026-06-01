# Momentum Overlay Tool

Adds price momentum metrics to value rankings to identify stocks with both value and momentum characteristics.

## Overview

The Momentum Overlay combines value investing with momentum investing by:
- Adding 3-month, 6-month, and 12-month price returns to all stocks
- Calculating composite momentum scores
- Identifying "Value + Momentum" opportunities (top value stocks with positive momentum)
- Warning about "Falling Knives" (top value stocks with negative momentum)

## Features

- **Multiple Timeframes**: 3M, 6M, and 12M price returns
- **Momentum Scoring**: Composite momentum score from all timeframes
- **Value + Momentum**: Stocks with both strong value and positive momentum
- **Falling Knives Detection**: Top value stocks with declining prices (potential value traps)
- **Momentum Categories**: Strong/Moderate/Weak Positive/Negative classifications

## Usage

```bash
cd momentum-overlay
python momentum_overlay.py
```

**Note**: Takes 5-10 minutes to fetch price data for all stocks.

## Output

Generates timestamped Excel file: `momentum_analysis_YYYYMMDD_HHMM.xlsx`

### Sheets:
1. **All Stocks**: Complete rankings with momentum metrics
2. **Value + Momentum**: Top 100 value stocks with positive momentum
3. **Falling Knives**: Top 100 value stocks with negative momentum
4. **Summary**: Key statistics and metrics

## Strategy

### Value + Momentum Approach
Combines two proven strategies:
- **Value**: Low valuations (P/E, P/B, etc.)
- **Momentum**: Rising prices (positive returns)

Research shows combining value and momentum often outperforms either strategy alone.

### Avoiding Falling Knives
Identifies value stocks with declining prices that may be:
- Facing fundamental problems
- In secular decline
- Value traps (cheap for a reason)

## Momentum Categories

- **Strong Positive**: ≥20% average return
- **Moderate Positive**: 10-20% average return
- **Weak Positive**: 0-10% average return
- **Weak Negative**: 0 to -10% average return
- **Moderate Negative**: -10 to -20% average return
- **Strong Negative**: ≤-20% average return

## Best Practices

1. **Focus on Value + Momentum**: These stocks have both quality and price action
2. **Avoid Falling Knives**: Research carefully before buying declining stocks
3. **Consider Timeframes**: Look for consistency across 3M, 6M, and 12M
4. **Combine with Fundamentals**: Momentum doesn't replace fundamental analysis
5. **Update Regularly**: Momentum changes quickly - refresh monthly

## Integration

Works with:
- **Master Aggregator**: Source of value rankings
- **Portfolio Builder**: Build momentum-aware portfolios
- **Alert System**: Track momentum changes

## Limitations

- Historical returns don't guarantee future performance
- Momentum can reverse quickly
- High momentum stocks may be overvalued
- Requires regular updates for accuracy

## Notes

- Fetches real-time price data from Yahoo Finance
- Rate limited to avoid API restrictions
- Some stocks may have incomplete data
- Momentum calculated from adjusted close prices