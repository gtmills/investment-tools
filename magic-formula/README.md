# Magic Formula Screener

A Python implementation of Joel Greenblatt's "Magic Formula" investing strategy that identifies high-quality businesses trading at attractive prices.

## Overview

The Magic Formula combines two key metrics to find the best investment opportunities:

1. **Earnings Yield** - How much the company earns relative to its price (value metric)
2. **Return on Capital** - How efficiently the company uses its capital (quality metric)

By ranking stocks on both metrics and combining the ranks, we identify companies that are both high-quality AND reasonably priced.

## Strategy Background

Created by Joel Greenblatt and detailed in his book "The Little Book That Beats the Market", the Magic Formula has historically outperformed the market by focusing on:
- **Good companies** (high return on capital)
- **At bargain prices** (high earnings yield)

## How It Works

1. **Calculate Earnings Yield**: Approximated as `1 / P/E Ratio`
   - Higher is better (means cheaper relative to earnings)
   
2. **Calculate Return on Capital**: Using ROE as a proxy
   - Higher is better (means more efficient use of capital)

3. **Rank Each Metric**: Assign ranks 1-N (1 = best)
   - Earnings Yield Rank (1 = highest earnings yield)
   - Return on Capital Rank (1 = highest ROC)

4. **Calculate Magic Formula Score**: Sum of both ranks
   - Lower score = better investment opportunity
   - Example: EY_Rank=5 + ROC_Rank=3 = MF_Score of 8

5. **Sort by Score**: Lowest scores are the best opportunities

## Usage

### Prerequisites

First, generate the stock data:
```bash
cd ../value-ranker
python sp500_pe_sorter.py
```

### Run the Screener

```bash
python magic_formula_screener.py
```

## Output

### Console Output
Displays the top 50 Magic Formula stocks with:
- Magic Formula Rank and Score
- Individual ranks for Earnings Yield and Return on Capital
- Key financial metrics (P/E, ROE, Debt/Equity)
- Company details (sector, market cap, price)

### Excel File: `magic_formula_ranked.xlsx`

**Sheet 1: Magic Formula Rankings**
- All ranked stocks (typically ~450 stocks)
- Complete financial data
- Individual and composite rankings

**Sheet 2: Top 50 Stocks**
- Best 50 stocks by Magic Formula Score
- Quick reference for top opportunities

**Sheet 3: Methodology**
- Detailed explanation of the strategy
- How to interpret the rankings
- Important notes and disclaimers

## Example Results

```
MF_Rank  Ticker  Company                    Sector        Earnings_Yield  EY_Rank  Return_on_Capital  ROC_Rank  MF_Score
1        CHTR    Charter Communications     Communication 0.2597          2        0.1450             8         10
2        CI      The Cigna Group            Healthcare    0.4082          1        0.1234             15        16
3        AIG     American International     Financials    0.0760          55       0.0987             4         59
```

## Interpretation

### Top-Ranked Stocks (Low MF Score)
- Combine high earnings yield (cheap) with high return on capital (quality)
- Represent the "sweet spot" of value + quality
- Should be researched further before investing

### Understanding the Scores

**Magic Formula Score = EY_Rank + ROC_Rank**

- Score of 10: Both metrics ranked in top 10 (excellent)
- Score of 50: Average of ranks around 25 each (good)
- Score of 100+: At least one metric ranked poorly (avoid)

## Greenblatt's Recommendations

1. **Portfolio Size**: Hold 20-30 stocks from the top rankings
2. **Diversification**: Don't put all eggs in one basket
3. **Rebalancing**: Review and rebalance annually
4. **Patience**: Strategy works over 3-5 year periods
5. **Discipline**: Stick with the system even during underperformance

## Important Notes

### Approximations Used
- **Earnings Yield**: Uses `1/P/E` instead of `EBIT/Enterprise Value`
- **Return on Capital**: Uses ROE instead of `EBIT/(Working Capital + Fixed Assets)`

These approximations are necessary due to data availability but maintain the spirit of the strategy.

### Limitations

1. **Not Investment Advice**: This is a quantitative screening tool only
2. **Simplified Metrics**: True Magic Formula uses more complex calculations
3. **No Qualitative Analysis**: Doesn't consider management, moat, or industry trends
4. **Historical Data**: Past performance doesn't guarantee future results
5. **Requires Research**: Always investigate companies before investing

## Best Practices

1. **Start with Top 50**: Focus on stocks with lowest MF Scores
2. **Do Your Homework**: Research each company's business model
3. **Check Financials**: Review debt levels, cash flow, earnings quality
4. **Understand the Business**: Know what the company does and why it's profitable
5. **Diversify**: Spread investments across multiple sectors
6. **Be Patient**: Give the strategy time to work (3-5 years minimum)

## When to Avoid a Stock

Even with a good Magic Formula Score, avoid stocks with:
- Excessive debt (Debt/Equity > 2.0)
- Declining revenues or earnings
- Poor cash flow generation
- Questionable accounting practices
- Industries in structural decline

## Technical Details

- **Data Source**: Yahoo Finance via yfinance library
- **Ranking Method**: `rank(method='min')` - ties get the same rank
- **Filtering**: Excludes negative or zero values
- **Typical Coverage**: ~450 out of 500 S&P stocks have valid data

## Troubleshooting

**Error: "sp500_pe_sorted.xlsx not found"**
- Run `python ../value-ranker/sp500_pe_sorter.py` first

**Fewer stocks than expected**
- Some stocks lack P/E data (negative earnings)
- Some stocks lack ROE data (financial companies)

## References

- Book: "The Little Book That Beats the Market" by Joel Greenblatt
- Website: [Magic Formula Investing](https://www.magicformulainvesting.com/)

## License

This tool is provided as-is for educational and informational purposes.