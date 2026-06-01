# Portfolio Builder Tool

Generates diversified investment portfolios from top-ranked stocks with automatic sector and position size constraints.

## Overview

The Portfolio Builder takes the master investment rankings and constructs optimized portfolios that balance:
- **Stock Quality**: Focus on top-ranked opportunities
- **Diversification**: Sector allocation limits
- **Risk Management**: Position size constraints
- **Tool Coverage**: Minimum number of ranking tools

## Features

- **Three Pre-Built Strategies**: Conservative, Balanced, and Aggressive portfolios
- **Sector Diversification**: Automatic limits on sector concentration
- **Position Sizing**: Maximum allocation per stock
- **Equal Weighting**: Within constraints, stocks are equally weighted
- **Detailed Reports**: Holdings, sector allocation, and summary statistics

## Usage

```bash
cd portfolio-builder
python portfolio_builder.py
```

This generates three portfolio files:
- `portfolio_conservative.xlsx` - 20 stocks, top 100 ranks, 7+ tools
- `portfolio_balanced.xlsx` - 25 stocks, top 150 ranks, 6+ tools
- `portfolio_aggressive.xlsx` - 30 stocks, top 200 ranks, 5+ tools

## Portfolio Strategies

### Conservative Portfolio
- **Size**: 20 stocks
- **Rank Range**: Top 100 (best opportunities)
- **Min Tools**: 7 (highest conviction)
- **Max Sector**: 25% (strong diversification)
- **Max Position**: 8% (conservative sizing)
- **Best For**: Risk-averse investors, retirement accounts

### Balanced Portfolio
- **Size**: 25 stocks
- **Rank Range**: Top 150
- **Min Tools**: 6
- **Max Sector**: 30%
- **Max Position**: 10%
- **Best For**: Most investors, balanced approach

### Aggressive Portfolio
- **Size**: 30 stocks
- **Rank Range**: Top 200
- **Min Tools**: 5
- **Max Sector**: 35%
- **Max Position**: 12%
- **Best For**: Higher risk tolerance, growth focus

## Output Files

Each portfolio Excel file contains three sheets:

### 1. Portfolio Sheet
Complete list of holdings with:
- Rank (composite score)
- Ticker and Company name
- Sector and Industry
- Investment Grade
- Allocation percentage
- Individual tool rankings

### 2. Summary Sheet
Portfolio statistics:
- Strategy name and parameters
- Total stocks and weight
- Average rank and tools coverage
- Best and worst ranks
- Generation timestamp

### 3. Sector Allocation Sheet
Sector breakdown showing:
- Weight percentage per sector
- Number of stocks per sector
- Average rank per sector

## Customization

You can modify the strategies in the script by adjusting:

```python
strategies = [
    {
        'name': 'Your Strategy Name',
        'size': 20,                    # Number of stocks
        'max_sector_pct': 0.25,        # Max 25% per sector
        'max_position_pct': 0.08,      # Max 8% per stock
        'min_tools': 7,                # Min tools coverage
        'max_rank': 100,               # Max composite score
        'filename': 'your_portfolio.xlsx'
    }
]
```

## Requirements

- Master rankings must be generated first
- Run `master_aggregator.py` before portfolio builder
- Requires pandas and openpyxl

## Example Output

```
PORTFOLIO: Conservative Portfolio
================================================================================

Total Stocks: 20
Average Composite Score: 45.3
Average Tools Coverage: 7.2
Grade Distribution:
  A+: 12 stocks (60.0%)
  A: 8 stocks (40.0%)

Sector Allocation:
  Technology                    : 25.0% (5 stocks)
  Healthcare                    : 20.0% (4 stocks)
  Financials                    : 15.0% (3 stocks)
  ...

Top 10 Holdings:
Rank   Ticker   Company                                  Sector                    Grade    Weight   Score
--------------------------------------------------------------------------------------------------------
12     AAPL     Apple Inc.                              Technology                A+       5.00%    12
15     MSFT     Microsoft Corporation                   Technology                A+       5.00%    15
...
```

## Best Practices

1. **Rebalance Regularly**: Regenerate portfolios monthly or quarterly
2. **Review Holdings**: Research individual companies before investing
3. **Consider Taxes**: Account for tax implications when rebalancing
4. **Monitor Changes**: Track which stocks enter/exit the portfolio
5. **Combine Strategies**: Consider splitting capital across multiple strategies
6. **Add Qualitative Analysis**: Use quantitative rankings as starting point

## Limitations

- Equal weighting within constraints (no optimization)
- No consideration of correlations between stocks
- No transaction cost modeling
- No tax-loss harvesting
- Historical data only (no forward-looking analysis)

## Integration with Other Tools

The Portfolio Builder works seamlessly with:
- **Master Aggregator**: Source of rankings
- **Historical Tracker**: Monitor portfolio changes over time
- **Individual Tools**: Deep dive into specific stocks

## Notes

- Portfolios are generated using equal weighting
- Sector limits prevent over-concentration
- Position limits prevent single-stock risk
- Minimum tools requirement ensures conviction
- All constraints are applied simultaneously