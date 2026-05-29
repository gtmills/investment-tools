# Graham Number Calculator

Calculate Benjamin Graham's intrinsic value formula to identify undervalued stocks in the S&P 500.

## Overview

The Graham Number is a conservative valuation metric created by Benjamin Graham, the "father of value investing" and mentor to Warren Buffett. It provides a quick estimate of a stock's intrinsic value based on earnings and book value.

## Formula

```
Graham Number = √(22.5 × EPS × Book Value per Share)
```

Where:
- **22.5** = Graham's constant (15 × 1.5)
  - 15 = Maximum P/E ratio Graham considered reasonable
  - 1.5 = Maximum P/B ratio Graham considered reasonable
- **EPS** = Earnings Per Share
- **Book Value per Share** = Company's net asset value per share

## Key Metrics

### 1. Graham Number
The calculated intrinsic value of the stock based on Graham's formula.

### 2. Graham Ratio
```
Graham Ratio = Current Price / Graham Number
```
- **< 1.0** = Undervalued (trading below intrinsic value)
- **≈ 1.0** = Fairly valued
- **> 1.0** = Overvalued (trading above intrinsic value)

### 3. Margin of Safety
```
Margin of Safety = (Graham Number - Current Price) / Graham Number
```
- **Positive** = Undervalued (price below intrinsic value)
- **Negative** = Overvalued (price above intrinsic value)
- **Higher is better** = Greater safety cushion

## Usage

### Prerequisites

First, generate the stock data:
```bash
cd ../value-ranker
python sp500_pe_sorter.py
```

### Run the Calculator

```bash
python graham_calculator.py
```

## Output

### Console Output
Displays the top 50 most undervalued stocks with:
- Graham Number (intrinsic value)
- Graham Ratio (price vs intrinsic value)
- Margin of Safety
- EPS and Book Value per Share
- Key financial metrics

### Excel File: `graham_number_analysis.xlsx`

**Sheet 1: Rankings**
- Standardized format (Ticker + Graham_Rank)
- For aggregation with other tools

**Sheet 2: Detailed Rankings**
- All ranked stocks with complete data
- Typically ~450 stocks with valid data

**Sheet 3: Top 50 Stocks**
- Most undervalued stocks by Graham Ratio
- Quick reference for opportunities

**Sheet 4: Methodology**
- Formula explanation
- Interpretation guide
- Important notes

## Example Results

```
Rank  Ticker  Company                    Price    Graham_Number  Graham_Ratio  Margin_of_Safety  P/E    P/B
1     XYZ     Example Corp               45.00    75.00          0.60          40.0%             8.5    0.9
2     ABC     Another Company            120.00   180.00         0.67          33.3%             12.0   1.2
3     DEF     Third Company              85.00    110.00         0.77          22.7%             10.5   1.1
```

## Interpretation

### Highly Undervalued (Graham Ratio < 0.67)
- Trading at significant discount to intrinsic value
- Large margin of safety (> 33%)
- **Action**: Strong buy candidates (after research)

### Moderately Undervalued (0.67 < Graham Ratio < 0.85)
- Trading below intrinsic value
- Reasonable margin of safety (15-33%)
- **Action**: Good value opportunities

### Fairly Valued (0.85 < Graham Ratio < 1.15)
- Trading near intrinsic value
- Small margin of safety
- **Action**: Hold or wait for better entry

### Overvalued (Graham Ratio > 1.15)
- Trading above intrinsic value
- Negative margin of safety
- **Action**: Avoid or consider selling

## Benjamin Graham's Philosophy

Graham advocated for:
1. **Conservative valuation** - Better to be approximately right than precisely wrong
2. **Margin of safety** - Buy with a cushion against errors
3. **Fundamental analysis** - Focus on business value, not market sentiment
4. **Long-term investing** - Patience for value to be recognized

## Important Notes

### Strengths
- Simple, objective calculation
- Based on fundamental business metrics
- Conservative by design
- Proven track record over decades

### Limitations
- Doesn't account for growth potential
- May undervalue high-quality growth companies
- Ignores competitive advantages (moats)
- Book value can be misleading for asset-light businesses
- Best for traditional value stocks

## Best Practices

1. **Use as a starting point** - Not the only metric to consider
2. **Verify the numbers** - Check EPS and book value quality
3. **Understand the business** - Know what you're buying
4. **Compare to peers** - Context matters by industry
5. **Check for value traps** - Low price may reflect real problems
6. **Combine with other tools** - Use with FCF, Magic Formula, etc.
7. **Require margin of safety** - Don't buy at Graham Number, buy below it

## When Graham Number Works Best

### Good for:
- Traditional value stocks
- Asset-heavy businesses (manufacturing, retail)
- Mature, stable companies
- Cyclical stocks at bottom of cycle

### Less useful for:
- High-growth tech companies
- Asset-light businesses (software, services)
- Companies with intangible assets
- Negative earnings or book value

## Red Flags to Watch

Even with a good Graham Number, avoid stocks with:
- Declining revenues or earnings
- Excessive debt (Debt/Equity > 2.0)
- Negative cash flow
- Poor management or governance issues
- Industries in structural decline
- Accounting irregularities

## Technical Details

- **Data Source**: Yahoo Finance via yfinance library
- **EPS Calculation**: Current Price / P/E Ratio
- **Book Value Calculation**: Current Price / Price/Book Ratio
- **Ranking Method**: `rank(method='min')` - ties get same rank
- **Typical Coverage**: ~450 out of 500 S&P stocks have valid data

## Troubleshooting

**Error: "sp500_pe_sorted.xlsx not found"**
- Run `python ../value-ranker/sp500_pe_sorter.py` first

**Fewer stocks than expected**
- Some stocks have negative earnings (no P/E)
- Some stocks have negative book value
- Financial companies may have unusual metrics

**All stocks show as overvalued**
- Normal in bull markets
- Graham's formula is conservative
- Look for lowest Graham Ratios (least overvalued)

## References

- Book: "The Intelligent Investor" by Benjamin Graham
- Book: "Security Analysis" by Benjamin Graham and David Dodd
- Article: "Benjamin Graham's Net-Net Stock Strategy" - Investopedia

## License

This tool is provided as-is for educational and informational purposes only. Not investment advice.