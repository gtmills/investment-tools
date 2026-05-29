# Financial Health Dashboard

Analyzes S&P 500 stocks using two proven financial health metrics: **Altman Z-Score** (bankruptcy prediction) and **Piotroski F-Score** (financial strength assessment).

## Overview

This tool helps identify financially healthy companies and avoid value traps by combining:
- **Altman Z-Score**: Predicts bankruptcy risk
- **Piotroski F-Score**: Measures financial quality (0-9 scale)

## Key Metrics

### Altman Z-Score
Predicts probability of bankruptcy within 2 years.

**Interpretation:**
- **Z > 2.99**: Safe Zone (low risk)
- **1.81 < Z < 2.99**: Grey Zone (moderate risk)  
- **Z < 1.81**: Distress Zone (high risk)

### Piotroski F-Score
9-point financial strength checklist (1 point each):

**Profitability (4 points):**
- Positive ROA
- Positive Operating Cash Flow
- ROA increasing
- OCF > Net Income

**Leverage/Liquidity (3 points):**
- Debt decreasing
- Current Ratio increasing
- No share dilution

**Efficiency (2 points):**
- Gross Margin increasing
- Asset Turnover increasing

**Interpretation:**
- **8-9**: Strong (high quality)
- **5-7**: Moderate
- **0-4**: Weak (avoid)

## Usage

```bash
python financial_health_dashboard.py
```

## Output

**Excel file: `financial_health_analysis.xlsx`**
- Sheet 1: Rankings (standardized)
- Sheet 2: Detailed Rankings
- Sheet 3: Top 50 Stocks
- Sheet 4: Methodology

## Best Use Cases

- Risk assessment before investing
- Avoiding value traps
- Finding quality companies
- Portfolio risk management

## License

Educational purposes only.