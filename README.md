# Investment Tools Suite

A comprehensive Python-based toolkit for value investing analysis of S&P 500 stocks. This suite combines **8 specialized analysis tools** plus a **Master Aggregator** that ranks all stocks from 1-500 to identify the best investment opportunities.

## 🎯 Quick Start

**Run everything at once:**
```bash
python run_all_tools.py
```

This executes all 9 tools in sequence (~15-25 minutes) and generates the master rankings.

## Overview

This project provides eight specialized analysis tools plus a master aggregator:

1. **Value Ranker** - Traditional value metrics (P/E, P/B, PEG)
2. **Magic Formula** - Joel Greenblatt's quality + value strategy
3. **Free Cash Flow Analyzer** - Cash generation metrics
4. **Financial Health** - Altman Z-Score + Piotroski F-Score
5. **Graham Calculator** - Benjamin Graham's intrinsic value
6. **Dividend Aristocrats** - Dividend quality and consistency
7. **Historical Valuation** - Sector-relative valuations
8. **Earnings Quality** - Profitability and earnings analysis
9. **Master Aggregator** - Combines all rankings (1-500 scale)

## Key Features

- **Comprehensive Analysis**: 8 different investment methodologies
- **Master Rankings**: Composite scores from 1-500 (1 = best opportunity)
- **Investment Grades**: A+ to F grading system
- **Automated Workflow**: Run all tools with one command
- **Excel Outputs**: Detailed spreadsheets for each analysis
- **S&P 500 Coverage**: Analyzes all ~500 stocks

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

## Project Structure

```
investment-tools/
├── run_all_tools.py                    # Run all tools in sequence
├── requirements.txt                     # Python dependencies
├── README.md                           # This file
│
├── value-ranker/                       # Core data + value ranking
│   ├── sp500_pe_sorter.py             # Data collector (run first!)
│   ├── value_ranker.py                # P/E, P/B, PEG ranking
│   └── VALUE_RANKER_README.md
│
├── magic-formula/                      # Greenblatt's strategy
│   ├── magic_formula_screener.py
│   └── README.md
│
├── fcf-analyzer/                       # Free cash flow analysis
│   ├── fcf_analyzer.py
│   └── README.md
│
├── financial-health/                   # Bankruptcy & quality scores
│   ├── financial_health_dashboard.py
│   └── README.md
│
├── graham-calculator/                  # Graham's intrinsic value
│   ├── graham_calculator.py
│   └── README.md
│
├── dividend-aristocrats/               # Dividend quality screening
│   ├── dividend_aristocrats.py
│   └── README.md
│
├── historical-valuation/               # Sector-relative analysis
│   ├── historical_valuation.py
│   └── README.md
│
├── earnings-quality/                   # Profitability analysis
│   ├── earnings_quality.py
│   └── README.md
│
└── master-aggregator/                  # Combines all rankings
    ├── master_aggregator.py
    └── README.md
```

## Installation

### Requirements
- Python 3.7 or higher
- Internet connection

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests beautifulsoup4 pandas yfinance lxml openpyxl
```

## Usage

### Option 1: Run Everything (Recommended)

```bash
python run_all_tools.py
```

This runs all 9 tools in sequence and generates the master rankings. Takes 15-25 minutes.

### Option 2: Run Tools Individually

```bash
# Step 1: Collect S&P 500 data (required first step)
cd value-ranker
python sp500_pe_sorter.py

# Step 2: Run individual analysis tools (any order)
python value_ranker.py
cd ../magic-formula && python magic_formula_screener.py
cd ../fcf-analyzer && python fcf_analyzer.py
cd ../financial-health && python financial_health_dashboard.py
cd ../graham-calculator && python graham_calculator.py
cd ../dividend-aristocrats && python dividend_aristocrats.py
cd ../historical-valuation && python historical_valuation.py
cd ../earnings-quality && python earnings_quality.py

# Step 3: Generate master rankings
cd ../master-aggregator
python master_aggregator.py
```

## Master Rankings Output

The **Master Aggregator** produces `master_investment_rankings.xlsx` with:

### Investment Grades (A+ to F)
- **A+ (Top 10%)**: Exceptional opportunities - highest conviction
- **A (Top 20%)**: Excellent opportunities - strong candidates
- **B+ (Top 30%)**: Very good opportunities
- **B (Top 40%)**: Good opportunities
- **C (40-60%)**: Average opportunities
- **D/F (Bottom 40%)**: Below average - generally avoid

### Composite Scores (1-500)
- **1-50**: Elite opportunities
- **51-100**: Excellent opportunities
- **101-200**: Good opportunities
- **201-300**: Average opportunities
- **300+**: Below average

### Example Output

```
Rank  Ticker  Grade           Percentile  Avg_Rank  Tools  Value  Magic  FCF  Health  Graham  Dividend  Historical  Quality
1     AAPL    A+ (Exceptional) 98.5%      12.3      8      15     8      10   5       20      18        12          15
2     MSFT    A+ (Exceptional) 97.8%      15.7      8      22     12     8    12      15      25        18          10
3     GOOGL   A (Excellent)    96.2%      18.9      8      18     15     12   8       25      30        15          20
...
```

## Data Fields Collected

The base data collector fetches 25+ metrics per stock.

## Future Enhancements (TODO)

### High Priority

1. **Fix Value Ranker & Magic Formula Integration**
   - Value Ranker: Update to use 'Rankings' sheet format
   - Magic Formula: Fix column name mismatches
   - Currently only 6/8 tools load in Master Aggregator

2. **Add Sector/Industry to Master Rankings**
   - Include Sector and Industry columns from source data
   - Enable sector-based filtering and analysis
   - Support diversification decisions

3. **Historical Tracking System**
   - Save dated copies of master rankings
   - Track ranking changes over time
   - Identify consistent performers vs volatile rankings
   - Generate trend analysis reports

### Medium Priority

4. **Sector-Adjusted Rankings**
   - Calculate rankings within each sector
   - Identify best stock per sector
   - Account for sector-specific valuation norms

5. **Portfolio Builder Tool**
   - Generate diversified portfolios from top-ranked stocks
   - Apply constraints: max % per sector, max % per stock
   - Optimize for composite score while diversifying

6. **Backtesting Framework**
   - Test strategy performance with historical data
   - Compare against S&P 500 benchmark
   - Calculate returns, Sharpe ratio, max drawdown

7. **Alert System**
   - Monitor stocks moving into Grade A
   - Track significant ranking changes
   - Notify when new stocks enter top 50

### Quick Wins

8. **Summary Statistics**
   - Average P/E of top 50 stocks
   - Average dividend yield by grade
   - Sector concentration metrics
   - Market cap distribution

9. **CSV Export Option**
   - Add CSV export alongside Excel
   - Lighter format for programmatic analysis

10. **Timestamp Outputs**
    - Include data collection date in filenames
    - Add "Last Updated" field in Excel files

### Advanced Features

11. **Visualization Dashboard**
    - Grade distribution charts
    - Top 20 stocks bar chart
    - Sector breakdown analysis
    - Tool coverage heatmap

12. **Momentum Overlay**
    - Add 3/6/12-month price momentum
    - Combine value + momentum strategy
    - Avoid falling knives

13. **Insider Trading Integration**
    - Track SEC Form 4 filings
    - Monitor insider buying/selling
    - Combine with value rankings

14. **Web Interface**
    - Flask/Streamlit web app
    - Interactive filtering and sorting
    - Drill-down to individual tool details

## License

This script is provided as-is for educational and informational purposes.

## Investment Strategy Guide

### Conservative Approach
1. Focus on **Grade A stocks** (top 20%)
2. Require **7-8 tools coverage**
3. Composite score **< 100**
4. Research top 20 stocks thoroughly

### Balanced Approach  
1. Focus on **Grade A and B stocks** (top 40%)
2. Require **6+ tools coverage**
3. Composite score **< 200**
4. Research top 50 stocks

### Aggressive Approach
1. Include **Grade B+ stocks** (top 30%)
2. Accept **5+ tools coverage**
3. Composite score **< 150**
4. Research top 100 stocks

## Best Practices

1. **Start with Master Rankings**: Review `master_investment_rankings.xlsx` first
2. **Focus on Grade A**: Top 20% have highest conviction
3. **Verify Coverage**: Prefer stocks ranked by 7-8 tools
4. **Research Thoroughly**: Rankings are starting point, not final answer
5. **Check Individual Tools**: Understand why a stock ranks well
6. **Diversify Sectors**: Don't concentrate in one industry
7. **Update Regularly**: Re-run monthly or quarterly
8. **Combine with Your Analysis**: Add qualitative factors

## Tool Descriptions

### 1. Value Ranker
- **Metrics**: P/E, P/B, PEG ratios
- **Best for**: Traditional value investors
- **Output**: `sp500_value_ranked.xlsx`

### 2. Magic Formula (Greenblatt)
- **Metrics**: Earnings Yield + Return on Capital
- **Best for**: Quality at reasonable prices
- **Output**: `magic_formula_ranked.xlsx`

### 3. Free Cash Flow Analyzer
- **Metrics**: FCF Yield, FCF Growth
- **Best for**: Cash generation focus
- **Output**: `fcf_analysis.xlsx`
- **Note**: Takes 5-10 minutes (fetches additional data)

### 4. Financial Health Dashboard
- **Metrics**: Altman Z-Score, Piotroski F-Score
- **Best for**: Risk assessment, avoiding value traps
- **Output**: `financial_health_analysis.xlsx`

### 5. Graham Number Calculator
- **Metrics**: Intrinsic value, Margin of safety
- **Best for**: Conservative value investing
- **Output**: `graham_number_analysis.xlsx`

### 6. Dividend Aristocrats Screener
- **Metrics**: Dividend yield, growth, safety, consistency
- **Best for**: Income investors
- **Output**: `dividend_aristocrats_analysis.xlsx`
- **Note**: Takes 5-10 minutes (fetches dividend history)

### 7. Historical Valuation Analyzer
- **Metrics**: Sector-relative P/E and P/B
- **Best for**: Mean reversion opportunities
- **Output**: `historical_valuation_analysis.xlsx`

### 8. Earnings Quality Analyzer
- **Metrics**: Profit margins, ROE, ROA
- **Best for**: Identifying high-quality earnings
- **Output**: `earnings_quality_analysis.xlsx`

### 9. Master Aggregator
- **Combines**: All 8 tool rankings
- **Output**: Composite scores 1-500, Investment grades A+ to F
- **File**: `master_investment_rankings.xlsx`

## Execution Time

- **S&P 500 Data Collector**: 5-10 minutes
- **Value Ranker**: < 1 minute
- **Magic Formula**: < 1 minute
- **FCF Analyzer**: 5-10 minutes
- **Financial Health**: < 1 minute
- **Graham Calculator**: < 1 minute
- **Dividend Aristocrats**: 5-10 minutes
- **Historical Valuation**: < 1 minute
- **Earnings Quality**: < 1 minute
- **Master Aggregator**: < 1 minute

**Total**: 15-25 minutes for complete analysis

## Troubleshooting

**"sp500_pe_sorted.xlsx not found"**
- Run `python value-ranker/sp500_pe_sorter.py` first

**Rate limiting errors**
- Increase `time.sleep()` values in scripts
- Run during off-peak hours

**Fewer stocks than expected**
- Normal - some stocks lack required metrics
- Negative earnings = no P/E ratio
- Financial companies may lack certain data

**Master Aggregator shows missing tools**
- Run individual tools first
- Aggregator works with available data

## Important Notes

- **Not Investment Advice**: These are quantitative screening tools only
- **Requires Research**: Always investigate companies before investing
- **Historical Data**: Past metrics don't guarantee future performance
- **Quantitative Only**: No qualitative analysis (management, moats, etc.)
- **Equal Weighting**: All tools weighted equally in aggregation
- **Update Regularly**: Re-run monthly or quarterly for fresh data

## References

- **Magic Formula**: "The Little Book That Beats the Market" by Joel Greenblatt
- **Graham Number**: "The Intelligent Investor" by Benjamin Graham
- **FCF Analysis**: "The Little Book of Valuation" by Aswath Damodaran
- **Altman Z-Score**: Edward Altman's bankruptcy prediction model
- **Piotroski F-Score**: Joseph Piotroski's financial strength analysis

## Contributing

Each tool has its own detailed README with methodology, interpretation guides, and examples. See individual directories for more information.