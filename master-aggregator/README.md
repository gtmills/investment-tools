# Master Investment Aggregator

Combines rankings from all investment analysis tools to identify the best overall opportunities in the S&P 500.

## Overview

The Master Aggregator is the final step in the investment analysis workflow. It:
1. Loads rankings from all 8 investment tools
2. Calculates average rank for each stock
3. Assigns composite scores (1-500, lower = better)
4. Grades stocks from A+ to F
5. Identifies the top investment opportunities

## How It Works

### Aggregation Method

For each stock:
1. **Collect Rankings**: Gathers rank from each tool (if available)
2. **Calculate Average**: Computes mean rank across all tools
3. **Assign Score**: Ranks stocks by average (1 = best overall)
4. **Calculate Percentile**: 0-100 scale (higher = better)
5. **Assign Grade**: A+ to F based on percentile

### Investment Grades

- **A+ (90-100%)**: Exceptional - Top 10% across all metrics
- **A (80-90%)**: Excellent - Top 20% opportunities
- **B+ (70-80%)**: Very Good - Strong candidates
- **B (60-70%)**: Good - Solid opportunities
- **C+ (50-60%)**: Above Average
- **C (40-50%)**: Average
- **D+ (30-40%)**: Below Average
- **D (20-30%)**: Poor
- **F (<20%)**: Very Poor - Avoid

## Usage

### Prerequisites

Run all individual tools first:

```bash
# 1. Collect base data
cd value-ranker
python sp500_pe_sorter.py

# 2. Run all analysis tools
cd ../value-ranker && python value_ranker.py
cd ../magic-formula && python magic_formula_screener.py
cd ../fcf-analyzer && python fcf_analyzer.py
cd ../financial-health && python financial_health_dashboard.py
cd ../graham-calculator && python graham_calculator.py
cd ../dividend-aristocrats && python dividend_aristocrats.py
cd ../historical-valuation && python historical_valuation.py
cd ../earnings-quality && python earnings_quality.py
```

### Run the Aggregator

```bash
cd master-aggregator
python master_aggregator.py
```

## Output

### Excel File: `master_investment_rankings.xlsx`

**Sheet 1: Top 100 Opportunities**
- Best 100 stocks by composite score
- Includes company names for easy identification
- Quick reference for top picks

**Sheet 2: All Rankings**
- Complete dataset with all tool rankings
- Individual ranks from each tool
- Company names included alongside tickers

**Sheet 3: Grade A Stocks**
- Top 20% (80th percentile and above)
- Exceptional and excellent opportunities

**Sheet 4: Grade B Stocks**
- 60-80th percentile
- Very good and good opportunities

**Sheet 5: Methodology**
- Explanation of aggregation method
- How to interpret results

## Interpretation

### Composite Score
- **1-50**: Elite opportunities - highest conviction
- **51-100**: Excellent opportunities - strong candidates
- **101-200**: Good opportunities - worth researching
- **201-300**: Average opportunities - selective
- **300+**: Below average - generally avoid

### Tools Count
Shows how many tools ranked each stock:
- **8 tools**: Complete coverage - highest confidence
- **6-7 tools**: Good coverage - reliable
- **4-5 tools**: Moderate coverage - verify
- **<4 tools**: Limited coverage - caution

### Average Rank
The mean of individual tool ranks:
- **<50**: Consistently top-ranked across tools
- **50-100**: Generally well-ranked
- **100-200**: Mixed rankings
- **>200**: Generally poorly ranked

## Investment Strategy

### Conservative Approach
1. Focus on Grade A stocks (top 20%)
2. Require 7-8 tools coverage
3. Composite score < 100
4. Research top 20 stocks thoroughly

### Balanced Approach
1. Focus on Grade A and B stocks (top 40%)
2. Require 6+ tools coverage
3. Composite score < 200
4. Research top 50 stocks

### Aggressive Approach
1. Include Grade B+ stocks (top 30%)
2. Accept 5+ tools coverage
3. Composite score < 150
4. Research top 100 stocks

## Best Practices

1. **Start with Grade A**: Focus on top 20% first
2. **Verify Coverage**: Prefer stocks ranked by 7-8 tools
3. **Research Thoroughly**: Rankings are starting point, not final answer
4. **Diversify Sectors**: Don't concentrate in one industry
5. **Check Individual Tools**: Review why stock ranks well
6. **Consider Your Goals**: Income vs growth vs value
7. **Monitor Regularly**: Re-run monthly or quarterly

## Red Flags

Even with high composite scores, avoid stocks with:
- Declining revenues (check individual tools)
- Excessive debt (check Financial Health tool)
- Negative cash flow (check FCF Analyzer)
- Recent dividend cuts (check Dividend Aristocrats)
- Accounting issues (check Earnings Quality)

## Tools Included

The aggregator combines rankings from:

1. **Value Ranker** - P/E, P/B, PEG ratios
2. **Magic Formula** - Earnings yield + Return on capital
3. **FCF Analyzer** - Free cash flow metrics
4. **Financial Health** - Altman Z-Score + Piotroski F-Score
5. **Graham Calculator** - Benjamin Graham's intrinsic value
6. **Dividend Aristocrats** - Dividend quality and growth
7. **Historical Valuation** - Sector-relative valuations
8. **Earnings Quality** - Profitability metrics

## Example Workflow

```bash
# 1. Update data (weekly/monthly)
cd value-ranker
python sp500_pe_sorter.py

# 2. Run all tools (can run in parallel)
python value_ranker.py
cd ../magic-formula && python magic_formula_screener.py
cd ../fcf-analyzer && python fcf_analyzer.py
cd ../financial-health && python financial_health_dashboard.py
cd ../graham-calculator && python graham_calculator.py
cd ../dividend-aristocrats && python dividend_aristocrats.py
cd ../historical-valuation && python historical_valuation.py
cd ../earnings-quality && python earnings_quality.py

# 3. Aggregate results
cd ../master-aggregator
python master_aggregator.py

# 4. Review results
# Open master_investment_rankings.xlsx
# Focus on Top 100 Opportunities sheet
# Research Grade A stocks in detail
```

## Limitations

- Quantitative screening only - no qualitative analysis
- Historical data - doesn't predict future
- Equal weighting of all tools - may not fit your strategy
- Requires all tools to run - missing tools reduce coverage
- No sector/industry adjustments in aggregation
- Doesn't account for market conditions or timing

## License

Educational purposes only. Not investment advice.