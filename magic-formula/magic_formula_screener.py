#!/usr/bin/env python3
"""
Magic Formula Screener (Joel Greenblatt Strategy)
Ranks stocks based on Earnings Yield and Return on Capital
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


def calculate_magic_formula_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Magic Formula metrics:
    1. Earnings Yield = EBIT / Enterprise Value (approximated as inverse P/E)
    2. Return on Capital = EBIT / (Net Working Capital + Net Fixed Assets)
       Approximated using ROE and ROA as proxies
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with Magic Formula rankings
    """
    # Create a copy
    mf_df = df.copy()
    
    # Calculate Earnings Yield (approximate using inverse P/E)
    # Higher earnings yield is better
    mf_df['Earnings_Yield'] = 1 / mf_df['P/E Ratio']
    
    # Use ROE as proxy for Return on Capital
    # Higher ROE is better
    mf_df['Return_on_Capital'] = mf_df['ROE']
    
    # Filter stocks with valid data
    required_cols = ['Earnings_Yield', 'Return_on_Capital']
    valid_stocks = mf_df[required_cols].notna().all(axis=1)
    mf_df = mf_df[valid_stocks].copy()
    
    # Filter out negative or zero values
    mf_df = mf_df[mf_df['Earnings_Yield'] > 0].copy()
    mf_df = mf_df[mf_df['Return_on_Capital'] > 0].copy()
    
    print(f"\nStocks with valid Magic Formula data: {len(mf_df)}")
    
    if len(mf_df) == 0:
        print("No stocks have valid Magic Formula metrics.")
        return pd.DataFrame()
    
    # Rank each metric (1 = best)
    # For Earnings Yield: higher is better, so ascending=False
    mf_df['EY_Rank'] = mf_df['Earnings_Yield'].rank(method='min', ascending=False)
    
    # For Return on Capital: higher is better, so ascending=False
    mf_df['ROC_Rank'] = mf_df['Return_on_Capital'].rank(method='min', ascending=False)
    
    # Calculate Magic Formula Score (sum of ranks, lower is better)
    mf_df['MF_Score'] = mf_df['EY_Rank'] + mf_df['ROC_Rank']
    
    # Sort by Magic Formula Score (lowest = best)
    mf_df = mf_df.sort_values('MF_Score', ascending=True)
    
    # Add overall rank
    mf_df['MF_Rank'] = range(1, len(mf_df) + 1)
    
    return mf_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """
    Display Magic Formula results
    
    Args:
        df: Ranked DataFrame
        top_n: Number of top stocks to display
    """
    if len(df) == 0:
        return
    
    print(f"\n{'='*130}")
    print(f"MAGIC FORMULA TOP {top_n} STOCKS")
    print(f"{'='*130}")
    print(f"\nStrategy: Combine high Earnings Yield with high Return on Capital")
    print(f"Lower MF_Score = Better (sum of individual ranks)\n")
    
    # Select columns to display
    display_cols = [
        'MF_Rank', 'Ticker', 'Company', 'Sector', 'Price', 'Market Cap',
        'Earnings_Yield', 'EY_Rank', 'Return_on_Capital', 'ROC_Rank', 'MF_Score',
        'P/E Ratio', 'ROE', 'Debt/Equity'
    ]
    
    # Only include columns that exist
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Display top N stocks
    top_stocks = df.head(top_n)[available_cols]
    
    # Format for better readability
    pd.options.display.float_format = '{:.4f}'.format
    print(top_stocks.to_string(index=False))
    
    # Summary statistics
    print(f"\n{'='*130}")
    print("SUMMARY STATISTICS")
    print(f"{'='*130}")
    print(f"Total stocks ranked: {len(df)}")
    print(f"\nTop Stock: {df.iloc[0]['Ticker']} - {df.iloc[0]['Company']}")
    print(f"  Earnings Yield: {df.iloc[0]['Earnings_Yield']:.4f} (Rank: {int(df.iloc[0]['EY_Rank'])})")
    print(f"  Return on Capital: {df.iloc[0]['Return_on_Capital']:.4f} (Rank: {int(df.iloc[0]['ROC_Rank'])})")
    print(f"  Magic Formula Score: {df.iloc[0]['MF_Score']:.0f}")
    print(f"  P/E Ratio: {df.iloc[0]['P/E Ratio']:.2f}")
    print(f"  Sector: {df.iloc[0]['Sector']}")
    print(f"{'='*130}")


def save_results(df: pd.DataFrame, filename: str = 'magic_formula_ranked.xlsx'):
    """
    Save Magic Formula results to Excel file with standardized ranking format
    
    Args:
        df: Ranked DataFrame
        filename: Output filename
    """
    if len(df) == 0:
        return
    
    try:
        # Create standardized ranking output (Ticker and Rank only for aggregation)
        ranking_output = df[['Ticker', 'MF_Rank']].copy()
        ranking_output.columns = ['Ticker', 'Magic_Formula_Rank']
        
        # Select columns for detailed output
        output_cols = [
            'MF_Rank', 'Ticker', 'Company', 'Sector', 'Industry', 'Price', 'Market Cap',
            'Earnings_Yield', 'EY_Rank', 'Return_on_Capital', 'ROC_Rank', 'MF_Score',
            'P/E Ratio', 'Forward P/E', 'PEG Ratio', 'Price/Book', 'ROE', 'ROA',
            'Profit Margin', 'Operating Margin', 'Debt/Equity', 'Current Ratio',
            'Dividend Yield', 'Beta'
        ]
        
        # Only include columns that exist
        available_cols = [col for col in output_cols if col in df.columns]
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Sheet 1: Standardized ranking for aggregation (Ticker + Rank only)
            ranking_output.to_excel(writer, sheet_name='Rankings', index=False)
            
            # Sheet 2: Full ranked list with all details
            df[available_cols].to_excel(writer, sheet_name='Detailed Rankings', index=False)
            
            # Write top 50
            df.head(50)[available_cols].to_excel(writer, sheet_name='Top 50 Stocks', index=False)
            
            # Write methodology
            methodology = pd.DataFrame({
                'Magic Formula Methodology': [
                    'The Magic Formula is a value investing strategy by Joel Greenblatt.',
                    '',
                    'It ranks stocks based on two key metrics:',
                    '',
                    '1. EARNINGS YIELD (Higher is Better)',
                    '   - Measures how much the company earns relative to its price',
                    '   - Calculated as: EBIT / Enterprise Value',
                    '   - Approximated here as: 1 / P/E Ratio',
                    '   - Higher earnings yield = cheaper stock',
                    '',
                    '2. RETURN ON CAPITAL (Higher is Better)',
                    '   - Measures how efficiently company uses capital',
                    '   - Calculated as: EBIT / (Net Working Capital + Net Fixed Assets)',
                    '   - Approximated here using ROE (Return on Equity)',
                    '   - Higher ROC = better quality business',
                    '',
                    'RANKING PROCESS:',
                    '- Rank all stocks by Earnings Yield (1 = highest)',
                    '- Rank all stocks by Return on Capital (1 = highest)',
                    '- Add the two ranks together = Magic Formula Score',
                    '- Lower MF Score = Better investment opportunity',
                    '',
                    'INTERPRETATION:',
                    '- Top-ranked stocks are high-quality businesses at good prices',
                    '- Combines value (earnings yield) with quality (return on capital)',
                    '- Greenblatt recommends holding 20-30 stocks from top rankings',
                    '- Rebalance annually',
                    '',
                    'IMPORTANT NOTES:',
                    '- This is a simplified implementation using available data',
                    '- True Magic Formula uses EBIT and tangible capital',
                    '- Always do additional research before investing',
                    '- Past performance does not guarantee future results',
                ]
            })
            methodology.to_excel(writer, sheet_name='Methodology', index=False)
        
        print(f"\n{'='*130}")
        print(f"Results saved to: {filename}")
        print(f"  - Sheet 1: Rankings (standardized format for aggregation)")
        print(f"  - Sheet 2: Detailed Rankings (all {len(df)} stocks with full data)")
        print(f"  - Sheet 3: Top 50 Stocks")
        print(f"  - Sheet 4: Methodology")
        print(f"{'='*130}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main execution function"""
    print("Magic Formula Screener (Joel Greenblatt Strategy)")
    print("="*130)
    print("Finding high-quality businesses at good prices...")
    print("="*130)
    
    # Load data
    df = load_stock_data()
    
    # Calculate Magic Formula metrics and rankings
    ranked_df = calculate_magic_formula_metrics(df)
    
    if len(ranked_df) == 0:
        print("Unable to rank stocks. Exiting.")
        return
    
    # Display results
    display_results(ranked_df, top_n=50)
    
    # Save results
    save_results(ranked_df)


if __name__ == "__main__":
    main()