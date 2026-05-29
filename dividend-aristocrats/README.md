# Dividend Aristocrats Screener

Identify high-quality dividend stocks with consistent growth and reliable income streams.

## Overview

This tool analyzes S&P 500 stocks for dividend quality, focusing on:
- **Consecutive years** of dividend payments
- **Dividend growth** rates
- **Dividend safety** (payout ratio, debt levels)
- **Dividend yield**

## Key Concepts

### Dividend Aristocrats
S&P 500 companies with **25+ consecutive years** of dividend increases. These elite stocks demonstrate:
- Financial strength through multiple economic cycles
- Management commitment to shareholders
- Sustainable business models
- Reliable income generation

### Dividend Achievers
Companies with **10+ consecutive years** of dividend increases. Strong candidates for future Aristocrat status.

### Dividend Safety Score (0-100)
Composite metric based on:
- **Payout Ratio** (40 points): Lower = more sustainable
- **Consecutive Years** (30 points): More = more reliable
- **Debt/Equity** (30 points): Lower = safer dividends

## Usage

### Prerequisites
```bash
cd ../value-ranker
python sp500_pe_sorter.py
```

### Run the Screener
```bash
python dividend_aristocrats.py
```

**Note**: Fetches dividend history from Yahoo Finance (~5-10 minutes)

## Output

### Excel File: `dividend_aristocrats_analysis.xlsx`

**Sheet 1: Rankings** - Standardized format for aggregation

**Sheet 2: Detailed Rankings** - All dividend-paying stocks

**Sheet 3: Dividend Aristocrats** - 25+ year stocks only

**Sheet 4: Top 50 Stocks** - Best dividend opportunities

**Sheet 5: Methodology** - Explanation and interpretation

## Ranking Methodology

Stocks are ranked by composite score combining:
1. **Dividend Yield** (higher = better)
2. **Consecutive Years** (more = better)
3. **Dividend Growth** (higher = better)
4. **Safety Score** (higher = better)

Lower composite rank = better overall dividend stock

## Interpretation

### Top-Ranked Stocks
- High yield with strong safety
- Consistent dividend growth
- Long track record
- **Action**: Best income opportunities

### Dividend Aristocrats
- 25+ years of increases
- Proven through recessions
- Lower volatility
- **Action**: Core holdings for income portfolios

### High Yield + Low Safety
- Attractive yield but risky
- May cut dividends
- **Action**: Avoid or research carefully

## Best Practices

1. **Prioritize safety over yield** - Sustainable > high
2. **Check payout ratio** - Under 60% is safer
3. **Verify growth** - Consistent increases matter
4. **Consider total return** - Yield + growth + appreciation
5. **Diversify sectors** - Don't concentrate in one industry
6. **Reinvest dividends** - Compound returns over time

## Red Flags

Avoid stocks with:
- Payout ratio > 80% (unsustainable)
- Declining revenues
- High debt (Debt/Equity > 2.0)
- Recent dividend cuts
- Cyclical industries at peak

## License

Educational purposes only. Not investment advice.