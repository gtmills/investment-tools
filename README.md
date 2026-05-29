# S&P 500 P/E Ratio Sorter

A Python script that fetches all S&P 500 stocks and sorts them by their P/E (Price-to-Earnings) ratio from lowest to highest.

## Features

- Automatically fetches the current list of S&P 500 companies from Wikipedia
- Retrieves comprehensive real-time stock data using Yahoo Finance API
- Sorts stocks by P/E ratio (lowest to highest)
- Exports results to Excel spreadsheet with multiple sheets
- Shows summary statistics (min, max, average, median P/E ratios)

### Data Fields Included

**Valuation Metrics:**
- P/E Ratio (Trailing)
- Forward P/E
- PEG Ratio
- Price/Book Ratio
- Price/Sales Ratio

**Market Metrics:**
- Current Price
- Market Cap
- Enterprise Value
- Sector & Industry

**Profitability Metrics:**
- Profit Margin
- Operating Margin
- Return on Equity (ROE)
- Return on Assets (ROA)

**Growth Metrics:**
- Revenue Growth
- Earnings Growth

**Dividend Metrics:**
- Dividend Yield
- Payout Ratio

**Financial Health:**
- Debt/Equity Ratio
- Current Ratio

**Trading Metrics:**
- Beta
- 52-Week High/Low
- Average Volume

## Requirements

- Python 3.7 or higher
- Internet connection

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install requests beautifulsoup4 pandas yfinance lxml
```

## Usage

Run the script:

```bash
python sp500_pe_sorter.py
```

The script will:
1. Fetch the list of S&P 500 companies (~500 stocks)
2. Retrieve comprehensive stock data for each stock (this may take a few minutes)
3. Display the sorted results in the terminal
4. Save the results to `sp500_pe_sorted.xlsx` (Excel format)

## Output

The script provides:

- **Console output**: Formatted table showing key metrics for all stocks sorted by P/E ratio
- **Excel file**: `sp500_pe_sorted.xlsx` containing:
  - **Sheet 1 (Stocks with PE)**: All stocks with P/E data, sorted lowest to highest, with 25+ data fields
  - **Sheet 2 (Stocks without PE)**: Companies without P/E data (negative earnings or unavailable)
  - **Sheet 3 (Summary)**: Summary statistics and key metrics

### Sample Output

```
================================================================================
S&P 500 STOCKS SORTED BY P/E RATIO (LOWEST TO HIGHEST)
================================================================================

Stocks with P/E data: 485
Stocks without P/E data: 15

================================================================================

Ticker  Company                    Sector        Price    Market Cap    P/E Ratio  Forward P/E  Dividend Yield  ROE      Debt/Equity
------  -------------------------  ------------  -------  ------------  ---------  -----------  --------------  -------  -----------
CI      The Cigna Group            Healthcare    278.22   75.2B         2.45       8.12         0.0523          0.145    0.89
CHTR    Charter Communications     Communication 143.12   18.5B         3.87       6.45         0.0000          -0.234   4.56
...
```

## Notes

- Some stocks may not have complete data (e.g., companies with negative earnings won't have P/E ratios)
- The script includes a small delay between API calls to avoid rate limiting
- P/E ratios are trailing P/E (based on last 12 months of earnings)
- Data is fetched in real-time and reflects current market conditions
- Market Cap and Enterprise Value are in actual dollar amounts (not abbreviated)
- Percentages (margins, yields, growth rates) are in decimal format (0.15 = 15%)

## Troubleshooting

If you encounter rate limiting issues:
- Increase the `time.sleep()` value in the script
- Run the script during off-peak hours

If Wikipedia structure changes:
- The script may need updates to the web scraping logic

## License

This script is provided as-is for educational and informational purposes.

## Planned Tools (TODO)

### High Priority

1. **Graham Number Calculator**
   - Calculate Benjamin Graham's intrinsic value: `√(22.5 × EPS × Book Value)`
   - Show margin of safety vs current price
   - Classic value investing fundamental
   - Complements existing P/E and P/B analysis

2. **Dividend Aristocrats Screener**
   - Filter stocks with 25+ years consecutive dividend increases
   - Rank by dividend yield, growth rate, payout ratio
   - Calculate dividend safety score
   - Income-focused investing tool

3. **Historical Valuation Analyzer**
   - Compare current P/E to 5-year average P/E
   - Calculate valuation z-scores
   - Identify if stock is cheap vs its own history
   - Catch cyclical opportunities and mean reversion plays

4. **Earnings Quality Analyzer**
   - Compare earnings to cash flow
   - Calculate accrual ratios
   - Identify accounting red flags
   - Prevent value traps

### Medium Priority

5. **Sector Rotation Analyzer**
   - Relative value within sectors
   - Sector-adjusted rankings
   - Account for sector-specific valuation norms

6. **Quality Score Ranker**
   - Composite score: ROE, ROA, margins, consistency
   - Pure quality ranking (separate from Magic Formula)

### Lower Priority

7. **Momentum + Value Hybrid**
   - Combine value metrics with price momentum
   - Avoid falling knives and value traps

8. **Insider Trading Tracker**
   - Track insider buying activity
   - Combine with value metrics
   - Requires SEC filing data integration