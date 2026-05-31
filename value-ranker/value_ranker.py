#!/usr/bin/env python3
"""
S&P 500 Value Stock Ranker
Ranks stocks based on P/E, P/B, and PEG ratios to identify potential value investments
"""

import pandas as pd
import sys
from pathlib import Path


def load_stock_data(filename: str = 'sp500_pe_sorted.xlsx') -> tuple[pd.DataFrame, str]:
    """
    Load stock data from Excel file
    
    Args:
        filename: Path to the Excel file
        
    Returns:
        Tuple of (DataFrame with stock data, filename)
    """
    try:
        df = pd.read_excel(filename, sheet_name='Stocks with PE')
        print(f"Loaded {len(df)} stocks from {filename}")
        return df, filename
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please run sp500_pe_sorter.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def rank_stocks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rank stocks based on P/E, P/B, and PEG ratios
    Lower values are better (ranked 1 = best)
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with rankings and composite score
    """
    # Create a copy to avoid modifying original
    ranked_df = df.copy()
    
    # Filter stocks that have all three metrics
    required_cols = ['P/E Ratio', 'Price/Book', 'PEG Ratio']
    
    # Check which columns exist
    missing_cols = [col for col in required_cols if col not in ranked_df.columns]
    if missing_cols:
        print(f"Warning: Missing columns: {missing_cols}")
        return pd.DataFrame()
    
    # Filter out rows with missing values in any of the three metrics
    valid_stocks = ranked_df[required_cols].notna().all(axis=1)
    ranked_df = ranked_df[valid_stocks].copy()
    
    # Also filter out negative or zero values (invalid for valuation metrics)
    for col in required_cols:
        ranked_df = ranked_df[ranked_df[col] > 0].copy()
    
    print(f"\nStocks with valid P/E, P/B, and PEG data: {len(ranked_df)}")
    
    if len(ranked_df) == 0:
        print("No stocks have all three metrics available.")
        return pd.DataFrame()
    
    # Rank each metric (1 = lowest/best value, higher = worse value)
    ranked_df['PE_Rank'] = ranked_df['P/E Ratio'].rank(method='min')
    ranked_df['PB_Rank'] = ranked_df['Price/Book'].rank(method='min')
    ranked_df['PEG_Rank'] = ranked_df['PEG Ratio'].rank(method='min')
    
    # Calculate average rank (composite score)
    ranked_df['Avg_Rank'] = (ranked_df['PE_Rank'] + ranked_df['PB_Rank'] + ranked_df['PEG_Rank']) / 3
    
    # Sort by average rank (lowest = best value)
    ranked_df = ranked_df.sort_values('Avg_Rank', ascending=True)
    
    # Add overall rank based on average
    ranked_df['Overall_Rank'] = range(1, len(ranked_df) + 1)
    
    return ranked_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """
    Display ranking results
    
    Args:
        df: Ranked DataFrame
        top_n: Number of top stocks to display
    """
    if len(df) == 0:
        return
    
    print(f"\n{'='*120}")
    print(f"TOP {top_n} VALUE STOCKS - RANKED BY P/E, P/B, AND PEG RATIOS")
    print(f"{'='*120}")
    print(f"\nLower ranks = Better value (Rank 1 = Best)")
    print(f"Overall Rank = Average of P/E Rank, P/B Rank, and PEG Rank\n")
    
    # Select columns to display
    display_cols = [
        'Overall_Rank', 'Ticker', 'Company', 'Sector', 'Price', 'Market Cap',
        'P/E Ratio', 'PE_Rank', 'Price/Book', 'PB_Rank', 'PEG Ratio', 'PEG_Rank', 'Avg_Rank'
    ]
    
    # Display top N stocks
    top_stocks = df.head(top_n)[display_cols]
    print(top_stocks.to_string(index=False))
    
    # Summary statistics
    print(f"\n{'='*120}")
    print("SUMMARY STATISTICS")
    print(f"{'='*120}")
    print(f"Total stocks ranked: {len(df)}")
    print(f"\nTop Stock: {df.iloc[0]['Ticker']} - {df.iloc[0]['Company']}")
    print(f"  P/E Ratio: {df.iloc[0]['P/E Ratio']:.2f} (Rank: {int(df.iloc[0]['PE_Rank'])})")
    print(f"  P/B Ratio: {df.iloc[0]['Price/Book']:.2f} (Rank: {int(df.iloc[0]['PB_Rank'])})")
    print(f"  PEG Ratio: {df.iloc[0]['PEG Ratio']:.2f} (Rank: {int(df.iloc[0]['PEG_Rank'])})")
    print(f"  Average Rank: {df.iloc[0]['Avg_Rank']:.2f}")
    print(f"{'='*120}")


def save_results(df: pd.DataFrame, source_filename: str):
    """
    Save ranked results to a new Excel file
    
    Args:
        df: Ranked DataFrame
        source_filename: Original Excel filename (for reference)
    """
    if len(df) == 0:
        return
    
    # Create output filename
    output_filename = 'value-ranker/sp500_value_ranked.xlsx'
    
    try:
        
        # Select all relevant columns
        output_cols = [
            'Overall_Rank', 'Ticker', 'Company', 'Sector', 'Industry', 'Price', 'Market Cap',
            'P/E Ratio', 'PE_Rank', 'Price/Book', 'PB_Rank', 'PEG Ratio', 'PEG_Rank', 'Avg_Rank',
            'Forward P/E', 'Price/Sales', 'Dividend Yield', 'Profit Margin', 'ROE', 'ROA',
            'Revenue Growth', 'Earnings Growth', 'Debt/Equity', 'Beta'
        ]
        
        # Only include columns that exist
        available_cols = [col for col in output_cols if col in df.columns]
        
        # Create standardized ranking output for aggregation (Ticker and Rank only)
        ranking_output = df[['Ticker', 'Overall_Rank']].copy()
        
        # Create new Excel file with all sheets
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            # Sheet 1: Standardized ranking for aggregation (Ticker + Rank only)
            ranking_output.to_excel(writer, sheet_name='Rankings', index=False)
            
            # Sheet 2: Full ranked list with all details
            df[available_cols].to_excel(writer, sheet_name='Value Rankings', index=False)
            
            # Write top 50
            df.head(50)[available_cols].to_excel(writer, sheet_name='Top 50 Value Stocks', index=False)
            
            # Write methodology explanation
            methodology = pd.DataFrame({
                'Ranking Methodology': [
                    'This tool ranks S&P 500 stocks based on three key value metrics:',
                    '',
                    '1. P/E Ratio (Price-to-Earnings): Lower is better',
                    '   - Measures how much you pay for each dollar of earnings',
                    '   - Lower P/E suggests stock may be undervalued',
                    '',
                    '2. P/B Ratio (Price-to-Book): Lower is better',
                    '   - Compares stock price to book value per share',
                    '   - Lower P/B suggests stock trading below its net asset value',
                    '',
                    '3. PEG Ratio (Price/Earnings-to-Growth): Lower is better',
                    '   - P/E ratio divided by earnings growth rate',
                    '   - Accounts for growth; PEG < 1 often considered undervalued',
                    '',
                    'Ranking Process:',
                    '- Each metric is ranked 1 to N (1 = lowest/best value)',
                    '- Average Rank = (PE_Rank + PB_Rank + PEG_Rank) / 3',
                    '- Stocks sorted by Average Rank (lowest = best overall value)',
                    '',
                    'Note: Only stocks with all three metrics are included in rankings.',
                    'Lower ranks indicate potentially better value investments.',
                ]
            })
            methodology.to_excel(writer, sheet_name='Value Methodology', index=False)
        
        print(f"\n{'='*120}")
        print(f"Results saved to: {output_filename}")
        print(f"  - Sheet 1: Rankings (standardized format for aggregation)")
        print(f"  - Sheet 2: Value Rankings (all {len(df)} stocks with full data)")
        print(f"  - Sheet 3: Top 50 Value Stocks")
        print(f"  - Sheet 4: Value Methodology")
        print(f"{'='*120}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main execution function"""
    print("S&P 500 Value Stock Ranker")
    print("="*120)
    print("Ranking stocks based on P/E, P/B, and PEG ratios...")
    print("="*120)
    
    # Load data
    df, source_file = load_stock_data()
    
    # Rank stocks
    ranked_df = rank_stocks(df)
    
    if len(ranked_df) == 0:
        print("Unable to rank stocks. Exiting.")
        return
    
    # Display results
    display_results(ranked_df, top_n=50)
    
    # Save results to the same Excel file
    save_results(ranked_df, source_file)


if __name__ == "__main__":
    main()