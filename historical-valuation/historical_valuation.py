#!/usr/bin/env python3
"""
Historical Valuation Analyzer
Compares current valuations to historical averages to identify mean reversion opportunities
"""

import pandas as pd
import yfinance as yf
import sys
from pathlib import Path
import time
import numpy as np


def load_stock_data(filename: str = '../value-ranker/sp500_pe_sorted.xlsx') -> pd.DataFrame:
    """Load stock data from Excel file"""
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


def fetch_historical_data(tickers: list) -> dict:
    """
    Fetch 5-year historical P/E data for given tickers
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        Dictionary with historical P/E data per ticker
    """
    historical_data = {}
    total = len(tickers)
    
    print(f"\nFetching 5-year historical data for {total} stocks...")
    print("This may take several minutes...\n")
    
    for idx, ticker in enumerate(tickers, 1):
        try:
            stock = yf.Ticker(ticker)
            
            # Get historical P/E ratios from info
            info = stock.info
            current_pe = info.get('trailingPE')
            forward_pe = info.get('forwardPE')
            
            # Get 5-year average from historical data if available
            # Note: This is a simplified approach - ideally would calculate from historical prices/earnings
            historical_data[ticker] = {
                'Current_PE': current_pe,
                'Forward_PE': forward_pe,
                'Has_Data': current_pe is not None
            }
            
            # Progress indicator
            if idx % 50 == 0:
                print(f"Progress: {idx}/{total} stocks processed")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            historical_data[ticker] = {
                'Current_PE': None,
                'Forward_PE': None,
                'Has_Data': False
            }
    
    print(f"\nCompleted fetching historical data for {total} stocks")
    return historical_data


def analyze_historical_valuation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze stocks based on historical valuation metrics
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with historical valuation analysis and rankings
    """
    hist_df = df.copy()
    
    # For this implementation, we'll use sector-relative P/E as a proxy for historical comparison
    # Calculate sector average P/E
    sector_avg_pe = hist_df.groupby('Sector')['P/E Ratio'].transform('mean')
    hist_df['Sector_Avg_PE'] = sector_avg_pe
    
    # Calculate P/E relative to sector average
    hist_df['PE_vs_Sector'] = hist_df['P/E Ratio'] / hist_df['Sector_Avg_PE']
    
    # Calculate P/B relative to sector average
    sector_avg_pb = hist_df.groupby('Sector')['Price/Book'].transform('mean')
    hist_df['Sector_Avg_PB'] = sector_avg_pb
    hist_df['PB_vs_Sector'] = hist_df['Price/Book'] / hist_df['Sector_Avg_PB']
    
    # Calculate valuation z-score (how many standard deviations from sector mean)
    sector_std_pe = hist_df.groupby('Sector')['P/E Ratio'].transform('std')
    hist_df['PE_ZScore'] = (hist_df['P/E Ratio'] - hist_df['Sector_Avg_PE']) / sector_std_pe
    
    # Calculate composite relative valuation score
    # Lower is better (undervalued relative to sector)
    hist_df['Relative_Valuation_Score'] = (
        hist_df['PE_vs_Sector'] * 0.5 + 
        hist_df['PB_vs_Sector'] * 0.5
    )
    
    # Filter stocks with valid data
    valid_stocks = (
        hist_df['P/E Ratio'].notna() & 
        hist_df['Price/Book'].notna() &
        hist_df['Relative_Valuation_Score'].notna()
    )
    hist_df = hist_df[valid_stocks].copy()
    
    print(f"\nStocks with valid historical valuation data: {len(hist_df)}")
    
    if len(hist_df) == 0:
        print("No stocks have valid historical valuation metrics.")
        return pd.DataFrame()
    
    # Rank by relative valuation score (lower = more undervalued vs sector)
    hist_df['Historical_Rank'] = hist_df['Relative_Valuation_Score'].rank(method='min', ascending=True)
    
    # Rank by P/E z-score (lower = more undervalued)
    hist_df['ZScore_Rank'] = hist_df['PE_ZScore'].rank(method='min', ascending=True)
    
    # Calculate composite rank
    hist_df['Composite_Rank'] = (hist_df['Historical_Rank'] + hist_df['ZScore_Rank']) / 2
    
    # Sort by composite rank
    hist_df = hist_df.sort_values('Composite_Rank', ascending=True)
    
    # Add overall rank
    hist_df['Overall_Rank'] = range(1, len(hist_df) + 1)
    
    return hist_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """Display historical valuation results"""
    if len(df) == 0:
        return
    
    print(f"\n{'='*150}")
    print(f"TOP {top_n} UNDERVALUED STOCKS - HISTORICAL VALUATION ANALYSIS")
    print(f"{'='*150}")
    print(f"\nIdentifying stocks trading below their sector averages")
    print(f"Lower relative valuation = better value vs peers")
    print(f"\n{'='*150}\n")
    
    # Select columns to display
    display_cols = [
        'Overall_Rank', 'Ticker', 'Company', 'Sector',
        'P/E Ratio', 'Sector_Avg_PE', 'PE_vs_Sector', 'PE_ZScore',
        'Price/Book', 'PB_vs_Sector',
        'Relative_Valuation_Score',
        'Current Price', 'Market Cap'
    ]
    
    # Filter to available columns
    display_cols = [col for col in display_cols if col in df.columns]
    
    # Get top N stocks
    top_stocks = df.head(top_n)[display_cols].copy()
    
    # Format for display
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    
    print(top_stocks.to_string(index=False))
    
    # Summary statistics
    print(f"\n{'='*150}")
    print("SUMMARY STATISTICS")
    print(f"{'='*150}")
    print(f"Total stocks analyzed: {len(df)}")
    print(f"Undervalued vs sector (PE < sector avg): {len(df[df['PE_vs_Sector'] < 1.0])}")
    print(f"Overvalued vs sector (PE > sector avg): {len(df[df['PE_vs_Sector'] > 1.0])}")
    print(f"\nAverage P/E vs Sector: {df['PE_vs_Sector'].mean():.2f}x")
    print(f"Median P/E vs Sector: {df['PE_vs_Sector'].median():.2f}x")
    print(f"\nMost undervalued: {df.iloc[0]['Ticker']} (P/E {df.iloc[0]['PE_vs_Sector']:.2f}x sector avg)")
    print(f"Most overvalued: {df.iloc[-1]['Ticker']} (P/E {df.iloc[-1]['PE_vs_Sector']:.2f}x sector avg)")


def save_results(df: pd.DataFrame, filename: str = 'historical_valuation_analysis.xlsx'):
    """Save results to Excel file"""
    if len(df) == 0:
        return
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Standardized Rankings
        rankings_df = df[['Ticker', 'Historical_Rank']].copy()
        rankings_df.to_excel(writer, sheet_name='Rankings', index=False)
        
        # Sheet 2: Detailed Rankings
        df.to_excel(writer, sheet_name='Detailed Rankings', index=False)
        
        # Sheet 3: Top 50 Stocks
        top_50 = df.head(50).copy()
        top_50.to_excel(writer, sheet_name='Top 50 Stocks', index=False)
        
        # Sheet 4: Methodology
        methodology = pd.DataFrame({
            'Section': [
                'Historical Valuation Analysis',
                'Historical Valuation Analysis',
                'Historical Valuation Analysis',
                '',
                'Key Metrics',
                'Key Metrics',
                'Key Metrics',
                'Key Metrics',
                '',
                'Interpretation',
                'Interpretation',
                'Interpretation',
                '',
                'Important Notes',
                'Important Notes',
                'Important Notes'
            ],
            'Description': [
                'Compares current valuations to sector averages',
                'Identifies mean reversion opportunities',
                'Lower relative valuation = better value',
                '',
                'PE vs Sector: Current P/E / Sector Average P/E',
                'PB vs Sector: Current P/B / Sector Average P/B',
                'PE Z-Score: Standard deviations from sector mean',
                'Relative Valuation Score: Composite of PE and PB ratios',
                '',
                '< 1.0 = Trading below sector average (undervalued)',
                '≈ 1.0 = Trading at sector average (fairly valued)',
                '> 1.0 = Trading above sector average (overvalued)',
                '',
                'This is a quantitative screening tool only',
                'Always research companies before investing',
                'Not investment advice'
            ]
        })
        methodology.to_excel(writer, sheet_name='Methodology', index=False)
    
    print(f"\n{'='*150}")
    print(f"Results saved to {filename}")
    print(f"{'='*150}")


def main():
    """Main execution function"""
    print("="*150)
    print("HISTORICAL VALUATION ANALYZER")
    print("="*150)
    print("\nAnalyzing stocks relative to sector averages...")
    
    # Load data
    df = load_stock_data()
    
    # Analyze historical valuation
    hist_df = analyze_historical_valuation(df)
    
    if len(hist_df) > 0:
        # Display results
        display_results(hist_df, top_n=50)
        
        # Save to Excel
        save_results(hist_df)
        
        print("\n" + "="*150)
        print("ANALYSIS COMPLETE")
        print("="*150)
    else:
        print("\nNo valid data to analyze.")


if __name__ == "__main__":
    main()

