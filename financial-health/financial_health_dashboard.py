#!/usr/bin/env python3
"""
Financial Health Dashboard
Analyzes stocks using Altman Z-Score and Piotroski F-Score
"""

import pandas as pd
import sys
from pathlib import Path


def load_stock_data(filename: str = 'value-ranker/sp500_pe_sorted.xlsx') -> pd.DataFrame:
    """
    Load stock data from Excel file
    
    Args:
        filename: Path to the Excel file
        
    Returns:
        DataFrame with stock data
    """
    try:
        df = pd.read_excel(filename, sheet_name='Stocks with PE')
        print(f"Loaded {len(df)} stocks from {filename}")
        return df
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please run sp500_pe_sorter.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def calculate_altman_z_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Altman Z-Score for financial health assessment
    
    Z-Score = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
    Where:
    X1 = Working Capital / Total Assets
    X2 = Retained Earnings / Total Assets  
    X3 = EBIT / Total Assets
    X4 = Market Cap / Total Liabilities
    X5 = Sales / Total Assets
    
    Interpretation:
    Z > 2.99: Safe zone (low bankruptcy risk)
    1.81 < Z < 2.99: Grey zone (moderate risk)
    Z < 1.81: Distress zone (high bankruptcy risk)
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with Z-Score added
    """
    health_df = df.copy()
    
    # Approximate Z-Score using available metrics
    # X1: Working Capital / Total Assets (approximated using Current Ratio)
    # X2: Retained Earnings / Total Assets (approximated using ROA)
    # X3: EBIT / Total Assets (approximated using Operating Margin * Asset Turnover)
    # X4: Market Cap / Total Liabilities (approximated using inverse of Debt/Equity)
    # X5: Sales / Total Assets (Asset Turnover - not directly available)
    
    # Simplified Z-Score calculation with available data
    health_df['Z_Score'] = health_df.apply(
        lambda row: calculate_simplified_z_score(row),
        axis=1
    )
    
    # Classify Z-Score
    health_df['Z_Classification'] = health_df['Z_Score'].apply(classify_z_score)
    
    return health_df


def calculate_simplified_z_score(row) -> float:
    """
    Calculate simplified Z-Score using available metrics
    
    Args:
        row: DataFrame row with stock data
        
    Returns:
        Calculated Z-Score or None if insufficient data
    """
    try:
        # Use available proxies
        current_ratio = row.get('Current Ratio', None)
        roa = row.get('ROA', None)
        operating_margin = row.get('Operating Margin', None)
        debt_to_equity = row.get('Debt/Equity', None)
        
        if pd.isna(current_ratio) or pd.isna(roa) or pd.isna(operating_margin) or pd.isna(debt_to_equity):
            return None
        
        # Simplified approximation
        # X1 approximation: (Current Ratio - 1) / 2
        x1 = (current_ratio - 1) / 2 if current_ratio > 0 else 0
        
        # X2 approximation: ROA (as proxy for retained earnings efficiency)
        x2 = roa if roa > 0 else 0
        
        # X3 approximation: Operating Margin (as proxy for EBIT/Assets)
        x3 = operating_margin if operating_margin > 0 else 0
        
        # X4 approximation: Inverse of Debt/Equity ratio
        x4 = 1 / (debt_to_equity + 1) if debt_to_equity >= 0 else 0.5
        
        # X5 approximation: Assume average asset turnover of 1.0
        x5 = 1.0
        
        # Calculate Z-Score
        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)
        
        return z_score
        
    except Exception:
        return None


def classify_z_score(z_score) -> str:
    """
    Classify Z-Score into risk categories
    
    Args:
        z_score: Calculated Z-Score
        
    Returns:
        Classification string
    """
    if pd.isna(z_score):
        return 'Unknown'
    elif z_score > 2.99:
        return 'Safe'
    elif z_score > 1.81:
        return 'Grey Zone'
    else:
        return 'Distress'


def calculate_piotroski_f_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Piotroski F-Score (0-9 point financial strength test)
    
    9 criteria (1 point each):
    Profitability (4 points):
    1. Positive ROA
    2. Positive Operating Cash Flow
    3. ROA increasing
    4. Operating Cash Flow > Net Income (quality of earnings)
    
    Leverage/Liquidity (3 points):
    5. Debt/Equity decreasing
    6. Current Ratio increasing
    7. No new shares issued
    
    Operating Efficiency (2 points):
    8. Gross Margin increasing
    9. Asset Turnover increasing
    
    Interpretation:
    8-9: Strong (high quality)
    5-7: Moderate
    0-4: Weak (low quality)
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with F-Score added
    """
    health_df = df.copy()
    
    # Calculate F-Score using available metrics
    health_df['F_Score'] = health_df.apply(
        lambda row: calculate_simplified_f_score(row),
        axis=1
    )
    
    # Classify F-Score
    health_df['F_Classification'] = health_df['F_Score'].apply(classify_f_score)
    
    return health_df


def calculate_simplified_f_score(row) -> int:
    """
    Calculate simplified Piotroski F-Score using available metrics
    
    Args:
        row: DataFrame row with stock data
        
    Returns:
        F-Score (0-9) or None if insufficient data
    """
    try:
        score = 0
        
        # 1. Positive ROA
        roa = row.get('ROA', None)
        if pd.notna(roa) and roa > 0:
            score += 1
        
        # 2. Positive Operating Cash Flow (assume if ROA positive and profit margin positive)
        profit_margin = row.get('Profit Margin', None)
        if pd.notna(profit_margin) and profit_margin > 0 and pd.notna(roa) and roa > 0:
            score += 1
        
        # 3. ROA increasing (use ROE as proxy, compare to industry average)
        roe = row.get('ROE', None)
        if pd.notna(roe) and roe > 0.10:  # Above 10% threshold
            score += 1
        
        # 4. Quality of earnings (Operating Margin > Profit Margin indicates good quality)
        operating_margin = row.get('Operating Margin', None)
        if pd.notna(operating_margin) and pd.notna(profit_margin):
            if operating_margin > profit_margin * 0.8:  # Operating margin close to profit margin
                score += 1
        
        # 5. Debt/Equity decreasing (low debt is good)
        debt_to_equity = row.get('Debt/Equity', None)
        if pd.notna(debt_to_equity) and debt_to_equity < 0.5:  # Low debt
            score += 1
        
        # 6. Current Ratio increasing (good liquidity)
        current_ratio = row.get('Current Ratio', None)
        if pd.notna(current_ratio) and current_ratio > 1.5:  # Strong liquidity
            score += 1
        
        # 7. No new shares issued (assume if ROE is strong, not diluting)
        if pd.notna(roe) and roe > 0.15:  # Strong ROE suggests not diluting
            score += 1
        
        # 8. Gross Margin increasing (use Profit Margin as proxy)
        if pd.notna(profit_margin) and profit_margin > 0.15:  # Good margins
            score += 1
        
        # 9. Asset Turnover increasing (use ROA as proxy for efficiency)
        if pd.notna(roa) and roa > 0.08:  # Efficient asset use
            score += 1
        
        return score
        
    except Exception:
        return None


def classify_f_score(f_score) -> str:
    """
    Classify F-Score into quality categories
    
    Args:
        f_score: Calculated F-Score
        
    Returns:
        Classification string
    """
    if pd.isna(f_score):
        return 'Unknown'
    elif f_score >= 8:
        return 'Strong'
    elif f_score >= 5:
        return 'Moderate'
    else:
        return 'Weak'


def calculate_health_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate overall financial health rankings
    
    Args:
        df: DataFrame with Z-Score and F-Score
        
    Returns:
        DataFrame with health rankings
    """
    health_df = df.copy()
    
    # Filter stocks with both scores
    valid_stocks = health_df['Z_Score'].notna() & health_df['F_Score'].notna()
    health_df = health_df[valid_stocks].copy()
    
    print(f"\nStocks with complete health data: {len(health_df)}")
    
    if len(health_df) == 0:
        print("No stocks have complete health data.")
        return pd.DataFrame()
    
    # Rank by Z-Score (higher is better)
    health_df['Z_Rank'] = health_df['Z_Score'].rank(method='min', ascending=False)
    
    # Rank by F-Score (higher is better)
    health_df['F_Rank'] = health_df['F_Score'].rank(method='min', ascending=False)
    
    # Calculate composite Health Score (average of ranks, lower is better)
    health_df['Health_Score'] = (health_df['Z_Rank'] + health_df['F_Rank']) / 2
    
    # Sort by Health Score
    health_df = health_df.sort_values('Health_Score', ascending=True)
    
    # Add overall rank
    health_df['Health_Rank'] = range(1, len(health_df) + 1)
    
    return health_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """
    Display financial health results
    
    Args:
        df: Ranked DataFrame
        top_n: Number of top stocks to display
    """
    if len(df) == 0:
        return
    
    print(f"\n{'='*150}")
    print(f"TOP {top_n} FINANCIALLY HEALTHY STOCKS")
    print(f"{'='*150}")
    print(f"\nHigher Z-Score = Lower bankruptcy risk")
    print(f"Higher F-Score = Stronger financial quality")
    print(f"Lower Health_Rank = Better overall financial health\n")
    
    # Select columns to display
    display_cols = [
        'Health_Rank', 'Ticker', 'Company', 'Sector',
        'Z_Score', 'Z_Classification', 'Z_Rank',
        'F_Score', 'F_Classification', 'F_Rank',
        'Health_Score', 'P/E Ratio', 'Debt/Equity', 'Current Ratio'
    ]
    
    # Only include columns that exist
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Display top N stocks
    top_stocks = df.head(top_n)[available_cols].copy()
    
    # Format for better readability
    pd.options.display.float_format = '{:.2f}'.format
    print(top_stocks.to_string(index=False))
    
    # Summary statistics
    print(f"\n{'='*150}")
    print("SUMMARY STATISTICS")
    print(f"{'='*150}")
    print(f"Total stocks ranked: {len(df)}")
    print(f"\nTop Stock: {df.iloc[0]['Ticker']} - {df.iloc[0]['Company']}")
    print(f"  Z-Score: {df.iloc[0]['Z_Score']:.2f} ({df.iloc[0]['Z_Classification']})")
    print(f"  F-Score: {int(df.iloc[0]['F_Score'])} ({df.iloc[0]['F_Classification']})")
    print(f"  Health Score: {df.iloc[0]['Health_Score']:.2f}")
    print(f"  Sector: {df.iloc[0]['Sector']}")
    
    # Distribution stats
    print(f"\nZ-Score Distribution:")
    print(f"  Safe (>2.99): {(df['Z_Classification'] == 'Safe').sum()} stocks")
    print(f"  Grey Zone (1.81-2.99): {(df['Z_Classification'] == 'Grey Zone').sum()} stocks")
    print(f"  Distress (<1.81): {(df['Z_Classification'] == 'Distress').sum()} stocks")
    
    print(f"\nF-Score Distribution:")
    print(f"  Strong (8-9): {(df['F_Classification'] == 'Strong').sum()} stocks")
    print(f"  Moderate (5-7): {(df['F_Classification'] == 'Moderate').sum()} stocks")
    print(f"  Weak (0-4): {(df['F_Classification'] == 'Weak').sum()} stocks")
    print(f"{'='*150}")


def save_results(df: pd.DataFrame, filename: str = 'financial_health_analysis.xlsx'):
    """
    Save financial health results to Excel file
    
    Args:
        df: Ranked DataFrame
        filename: Output filename
    """
    if len(df) == 0:
        return
    
    try:
        # Create standardized ranking output
        ranking_output = df[['Ticker', 'Health_Rank']].copy()
        
        # Select columns for detailed output
        output_cols = [
            'Health_Rank', 'Ticker', 'Company', 'Sector', 'Industry', 'Price', 'Market Cap',
            'Z_Score', 'Z_Classification', 'Z_Rank',
            'F_Score', 'F_Classification', 'F_Rank',
            'Health_Score',
            'P/E Ratio', 'ROE', 'ROA', 'Profit Margin', 'Operating Margin',
            'Debt/Equity', 'Current Ratio', 'Dividend Yield'
        ]
        
        # Only include columns that exist
        available_cols = [col for col in output_cols if col in df.columns]
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Sheet 1: Standardized ranking
            ranking_output.to_excel(writer, sheet_name='Rankings', index=False)
            
            # Sheet 2: Detailed rankings
            df[available_cols].to_excel(writer, sheet_name='Detailed Rankings', index=False)
            
            # Sheet 3: Top 50
            df.head(50)[available_cols].to_excel(writer, sheet_name='Top 50 Stocks', index=False)
            
            # Sheet 4: Methodology
            methodology = pd.DataFrame({
                'Financial Health Methodology': [
                    'This tool assesses financial health using two proven metrics:',
                    '',
                    '1. ALTMAN Z-SCORE (Bankruptcy Prediction)',
                    '   Developed by Edward Altman in 1968',
                    '   Predicts probability of bankruptcy within 2 years',
                    '   ',
                    '   Formula: Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5',
                    '   X1 = Working Capital / Total Assets',
                    '   X2 = Retained Earnings / Total Assets',
                    '   X3 = EBIT / Total Assets',
                    '   X4 = Market Cap / Total Liabilities',
                    '   X5 = Sales / Total Assets',
                    '   ',
                    '   Interpretation:',
                    '   Z > 2.99: Safe Zone (low bankruptcy risk)',
                    '   1.81 < Z < 2.99: Grey Zone (moderate risk)',
                    '   Z < 1.81: Distress Zone (high bankruptcy risk)',
                    '   ',
                    '   Note: This implementation uses approximations based on available data',
                    '',
                    '2. PIOTROSKI F-SCORE (Financial Strength)',
                    '   Developed by Joseph Piotroski in 2000',
                    '   9-point checklist of financial health indicators',
                    '   ',
                    '   Profitability (4 points):',
                    '   - Positive ROA',
                    '   - Positive Operating Cash Flow',
                    '   - ROA increasing year-over-year',
                    '   - Operating Cash Flow > Net Income',
                    '   ',
                    '   Leverage/Liquidity (3 points):',
                    '   - Debt/Equity ratio decreasing',
                    '   - Current Ratio increasing',
                    '   - No new shares issued (no dilution)',
                    '   ',
                    '   Operating Efficiency (2 points):',
                    '   - Gross Margin increasing',
                    '   - Asset Turnover increasing',
                    '   ',
                    '   Interpretation:',
                    '   8-9: Strong (high quality company)',
                    '   5-7: Moderate (average quality)',
                    '   0-4: Weak (low quality, avoid)',
                    '',
                    'COMBINED HEALTH SCORE:',
                    '- Ranks stocks by both Z-Score and F-Score',
                    '- Health Score = Average of Z_Rank and F_Rank',
                    '- Lower Health Score = Better overall financial health',
                    '- Identifies companies that are both safe AND high quality',
                    '',
                    'BEST USE CASES:',
                    '- Risk assessment before investing',
                    '- Avoiding value traps (cheap but distressed)',
                    '- Finding quality companies at fair prices',
                    '- Portfolio risk management',
                    '',
                    'IMPORTANT NOTES:',
                    '- Scores are approximations using available data',
                    '- Always verify with company financial statements',
                    '- Past financial health does not guarantee future performance',
                    '- This is not investment advice',
                ]
            })
            methodology.to_excel(writer, sheet_name='Methodology', index=False)
        
        print(f"\n{'='*150}")
        print(f"Results saved to: {filename}")
        print(f"  - Sheet 1: Rankings (standardized format)")
        print(f"  - Sheet 2: Detailed Rankings (all {len(df)} stocks)")
        print(f"  - Sheet 3: Top 50 Stocks")
        print(f"  - Sheet 4: Methodology")
        print(f"{'='*150}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main execution function"""
    print("Financial Health Dashboard")
    print("="*150)
    print("Analyzing stocks using Altman Z-Score and Piotroski F-Score...")
    print("="*150)
    
    # Load data
    df = load_stock_data()
    
    # Calculate Z-Score
    df = calculate_altman_z_score(df)
    
    # Calculate F-Score
    df = calculate_piotroski_f_score(df)
    
    # Calculate health rankings
    ranked_df = calculate_health_rankings(df)
    
    if len(ranked_df) == 0:
        print("Unable to rank stocks. Exiting.")
        return
    
    # Display results
    display_results(ranked_df, top_n=50)
    
    # Save results
    save_results(ranked_df)


if __name__ == "__main__":
    main()
