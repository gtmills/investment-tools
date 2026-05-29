# Free Cash Flow Analyzer

A Python tool that analyzes S&P 500 stocks based on Free Cash Flow (FCF) metrics to identify companies generating strong cash flows at attractive valuations.

## Overview

Free Cash Flow is one of the most important metrics in value investing because:
- **Cash is real** - harder to manipulate than accounting earnings
- **Shows true profitability** - after all capital expenditures
- **Indicates shareholder returns** - available for dividends, buybacks, debt reduction
- **Better predictor of value** - more reliable than P/E ratios

## Key Metrics

### 1. Free Cash Flow Yield
```
FCF Yield = Free Cash Flow / Market Capitalization
```
- Measures cash generation per dollar of market value
- Higher is better (more cash for your investment)
- Good value typically: > 5%
- Compare to dividend yield and earnings yield

### 2. FCF Growth
- Year-over-year growth in Free Cash Flow
- Positive growth = improving business
- Consistent growth = quality company
- Combines with yield for complete picture

### 3. FCF Quality
- FCF > Net Income = High quality (cash-backed earnings)
- FCF < Net Income = Lower quality (accrual-based)
- Consistent FCF = reliable business model

## How It Works

1. **Loads Stock Data**: Reads from sp500_pe_sorted.xlsx
2. **Fetches FCF Data**: Gets cash flow statements from Yahoo Finance
3. **Calculates Metrics**:
   - Latest Free Cash Flow
   - FCF Yield (FCF / Market Cap)
   - FCF Growth (year-over-year)
4. **Ranks Stocks**:
   - By FCF Yield (higher = better)
   - By FCF Growth (higher = better)
   - Composite FCF Score (average of ranks)
5. **Filters Results**: Only positive FCF (excludes cash-burning companies)

## Usage

### Prerequisites

First, generate the stock data:
```bash
cd ../value-ranker
python sp500_pe_sorter.py
```

### Run the Analyzer

```bash
python fcf_analyzer.py
```

**Note**: This tool fetches additional data from Yahoo Finance, so it will take several minutes to complete (~500 stocks).

## Output

### Console Output
Displays the top 50 stocks by FCF metrics with:
- FCF Rank and Score
- FCF Yield and Growth
- Individual rankings
- Key financial metrics
- Summary statistics

### Excel File: `fcf_analysis.xlsx`

**Sheet 1: Rankings**
- Standardized format (Ticker + FCF_Rank)
- For aggregation with other tools

**Sheet 2: Detailed Rankings**
- All ranked stocks with complete data
- FCF metrics and financial ratios
- Typically ~400-450 stocks with positive FCF

**Sheet 3: Top 50 Stocks**
- Best 50 stocks by FCF Score
- Quick reference for opportunities

**Sheet 4: Methodology**
- Detailed explanation
- Interpretation guide
- Important notes

## Example Results

```
FCF_Rank  Ticker  Company                    FCF_Yield  FCF_Yield_Rank  FCF_Growth  FCF_Growth_Rank  FCF_Score
1         AAPL    Apple Inc.                 0.0523     15              0.1234      8                11.5
2         MSFT    Microsoft Corporation      0.0445     28              0.1567      3                15.5
3         GOOGL   Alphabet Inc.              0.0612     8               0.0987      18               13.0
```

## Interpretation

### High FCF Yield + High Growth
- **Best opportunities** - generating lots of cash AND growing
- Quality businesses at reasonable prices
- Look for FCF Yield > 5% and Growth > 10%

### High FCF Yield + Low/Negative Growth
- **Value plays** - cheap but mature or declining
- May be cyclical or facing headwinds
- Verify business isn't in structural decline

### Low FCF Yield + High Growth
- **Growth stocks** - expensive but expanding rapidly
- May be worth premium if growth sustainable
- Not traditional value investments

### Negative FCF
- **Cash burn** - spending more than generating
- Excluded from rankings
- Avoid for value investing (unless turnaround story)

## Why FCF Beats Earnings

| Metric | Earnings (Net Income) | Free Cash Flow |
|--------|----------------------|----------------|
| Manipulation | Easier (accruals, timing) | Harder (actual cash) |
| Capital Needs | Ignores reinvestment | Accounts for capex |
| Shareholder Value | Theoretical | Available for distribution |
| Quality Signal | Can be misleading | More reliable |

## Red Flags to Watch

Even with good FCF metrics, be cautious of:
- **Declining revenues** - FCF from cost-cutting, not growth
- **High debt** - FCF needed for debt service
- **One-time items** - Verify FCF is sustainable
- **Working capital games** - Delaying payments to boost FCF
- **Deferred maintenance** - Cutting capex unsustainably

## Best Practices

1. **Compare to Peers**: FCF yield varies by industry
2. **Check Consistency**: Look for stable/growing FCF over 3-5 years
3. **Verify Quality**: Ensure FCF > Net Income
4. **Consider Debt**: High FCF with high debt may not be available for shareholders
5. **Read Filings**: Verify cash flow statement details
6. **Combine Metrics**: Use with other value tools for complete picture

## Industry Considerations

### High FCF Yield Industries
- Technology (low capex)
- Consumer goods
- Healthcare
- Financial services

### Low FCF Yield Industries
- Utilities (high capex)
- Telecom (infrastructure)
- Manufacturing (equipment)
- Real estate (property)

## Technical Details

- **Data Source**: Yahoo Finance via yfinance library
- **FCF Calculation**: Operating Cash Flow - Capital Expenditures
- **Ranking Method**: `rank(method='min')` - ties get same rank
- **Filtering**: Excludes negative FCF
- **Typical Coverage**: ~400-450 out of 500 S&P stocks have positive FCF

## Limitations

- Historical data may not predict future FCF
- Doesn't account for debt levels or obligations
- Industry differences in capital intensity
- One-time items can distort recent FCF
- Growth rates based on limited history
- Doesn't consider competitive moats or management quality

## Troubleshooting

**Error: "sp500_pe_sorted.xlsx not found"**
- Run `python ../value-ranker/sp500_pe_sorter.py` first

**Fewer stocks than expected**
- Some companies have negative FCF (excluded)
- Some lack sufficient cash flow history
- Financial companies may have different reporting

**Slow execution**
- Fetching cash flow statements takes time
- ~500 API calls with rate limiting
- Expect 5-10 minutes for full run

## References

- Book: "The Little Book of Valuation" by Aswath Damodaran
- Article: "Free Cash Flow: The Real Measure of Value" - Investopedia
- Research: Academic studies showing FCF predicts returns better than earnings

## License

This tool is provided as-is for educational and informational purposes.