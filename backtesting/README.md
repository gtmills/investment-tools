# Backtesting Framework

Simple backtesting tool to evaluate how investment strategies would have performed historically.

## Overview

Tests strategy performance by:
- Selecting stocks based on current rankings
- Fetching historical 12-month returns
- Calculating equal-weight portfolio returns
- Comparing multiple strategies

## Features

- **Multiple Strategies**: Test Conservative, Balanced, and Aggressive approaches
- **Historical Returns**: 12-month lookback period
- **Performance Metrics**: Portfolio return, win rate, best/worst performers
- **Excel Reports**: Detailed results for each strategy

## Usage

```bash
cd backtesting
python backtesting_framework.py
```

**Note**: Takes 5-10 minutes to fetch historical price data.

## Strategies Tested

### 1. Conservative
- Top 50 ranks
- Grade A+ only
- 20 stocks

### 2. Balanced
- Top 100 ranks
- Grade A or better
- 25 stocks

### 3. Aggressive
- Top 150 ranks
- Grade B+ or better
- 30 stocks

## Output

Generates: `backtest_results_YYYYMMDD_HHMM.xlsx`

### Sheets:
1. **Summary**: Comparison of all strategies
2. **Strategy Details**: Individual stock returns for each strategy

## Important Notes

- **Past performance ≠ future results**
- **Simplified approach**: Equal weighting, no rebalancing
- **Survivorship bias**: Only tests current S&P 500 stocks
- **Limited period**: 12-month lookback only
- **No transaction costs**: Assumes zero trading costs

## Limitations

- Does not account for stocks removed from S&P 500
- No consideration of dividends
- Equal weighting may not be optimal
- Single time period tested
- No risk-adjusted metrics (Sharpe ratio, etc.)

## Best Practices

1. **Use as guidance only**: Not a guarantee of future performance
2. **Consider multiple periods**: Run after each ranking update
3. **Combine with research**: Backtest results are just one data point
4. **Understand limitations**: Be aware of what's not included
5. **Compare to benchmark**: Consider S&P 500 returns for same period

## Future Enhancements

- Multiple time periods
- Risk-adjusted returns (Sharpe ratio)
- Maximum drawdown calculation
- Benchmark comparison (S&P 500)
- Transaction cost modeling
- Dividend inclusion
- Rebalancing simulation