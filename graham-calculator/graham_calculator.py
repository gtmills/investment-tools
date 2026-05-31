#!/usr/bin/env python3
"""
Graham Number Calculator
Calculates Benjamin Graham's intrinsic value formula and margin of safety
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


def calculate_graham_number(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Graham Number and related metrics
    
    Graham Number = √(22.5 × EPS × Book Value per Share)
    
    Where:
    - 22.5 = Graham's constant (15 × 1.5, representing max P/E of 15 and max P/B of 1.5)
    - EPS = Earnings Per Share
    - Book Value per Share = Book Value / Shares Outstanding
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with Graham Number calculations and rankings
    """
    # Create a copy
    graham_df = df.copy()
    
    # Calculate EPS from P/E ratio and current price
    # EPS = Price / P/E Ratio
    graham_df['EPS'] = graham_df['Price'] / graham_df['P/E Ratio']
    
    # Calculate Book Value per Share from Price/Book ratio and current price
    # Book Value per Share = Price / (Price/Book)
    graham_df['Book_Value_Per_Share'] = graham_df['Price'] / graham_df['Price/Book']
    
    # Calculate Graham Number: √(22.5 × EPS × Book Value per Share)
    graham_df['Graham_Number'] = (22.5 * graham_df['EPS'] * graham_df['Book_Value_Per_Share']) ** 0.5
    
    # Calculate Margin of Safety
    # Margin of Safety = (Graham Number - Price) / Graham Number
    # Positive = undervalued, Negative = overvalued
    graham_df['Margin_of_Safety'] = (graham_df['Graham_Number'] - graham_df['Price']) / graham_df['Graham_Number']
    
    # Calculate Graham Number Ratio (Current Price / Graham Number)
    # < 1.0 = undervalued, > 1.0 = overvalued
    graham_df['Graham_Ratio'] = graham_df['Price'] / graham_df['Graham_Number']
    
    # Filter stocks with valid data
    required_cols = ['Graham_Number', 'Margin_of_Safety', 'Graham_Ratio']
    valid_stocks = graham_df[required_cols].notna().all(axis=1)
    graham_df = graham_df[valid_stocks].copy()
    
    # Filter out invalid values (negative or zero)
    graham_df = graham_df[graham_df['Graham_Number'] > 0].copy()
    graham_df = graham_df[graham_df['EPS'] > 0].copy()
    graham_df = graham_df[graham_df['Book_Value_Per_Share'] > 0].copy()
    
    print(f"\nStocks with valid Graham Number data: {len(graham_df)}")
    
    if len(graham_df) == 0:
        print("No stocks have valid Graham Number metrics.")
        return pd.DataFrame()
    
    # Rank by Graham Ratio (lower is better - more undervalued)
    # Rank 1 = most undervalued (lowest ratio)
    graham_df['Graham_Rank'] = graham_df['Graham_Ratio'].rank(method='min', ascending=True)
    
    # Sort by Graham Ratio (lowest = most undervalued)
    graham_df = graham_df.sort_values('Graham_Ratio', ascending=True)
    
    # Add overall rank
    graham_df['Overall_Rank'] = range(1, len(graham_df) + 1)
    
    return graham_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """
    Display Graham Number results
    
    Args:
        df: Ranked DataFrame
        top_n: Number of top stocks to display
    """
    if len(df) == 0:
        return
    
    print(f"\n{'='*140}")
    print(f"TOP {top_n} UNDERVALUED STOCKS - BENJAMIN GRAHAM'S INTRINSIC VALUE")
    print(f"{'='*140}")
    print(f"\nGraham Number = sqrt(22.5 x EPS x Book Value per Share)")
    print(f"Margin of Safety = (Graham Number - Current Price) / Graham Number")
    print(f"Graham Ratio = Current Price / Graham Number (< 1.0 = undervalued)")
    print(f"\n{'='*140}\n")
    
    # Select columns to display
    display_cols = [
        'Overall_Rank', 'Ticker', 'Company', 'Sector',
        'Price', 'Graham_Number', 'Graham_Ratio', 'Margin_of_Safety',
        'EPS', 'Book_Value_Per_Share', 'P/E Ratio', 'Price/Book',
        'Market Cap', 'ROE', 'Debt/Equity'
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
    print(f"\n{'='*140}")
    print("SUMMARY STATISTICS")
    print(f"{'='*140}")
    print(f"Total stocks analyzed: {len(df)}")
    print(f"Undervalued stocks (Graham Ratio < 1.0): {len(df[df['Graham_Ratio'] < 1.0])}")
    print(f"Fairly valued stocks (0.9 < Graham Ratio < 1.1): {len(df[(df['Graham_Ratio'] >= 0.9) & (df['Graham_Ratio'] <= 1.1)])}")
    print(f"Overvalued stocks (Graham Ratio > 1.0): {len(df[df['Graham_Ratio'] > 1.0])}")
    print(f"\nAverage Graham Ratio: {df['Graham_Ratio'].mean():.2f}")
    print(f"Median Graham Ratio: {df['Graham_Ratio'].median():.2f}")
    print(f"Average Margin of Safety: {df['Margin_of_Safety'].mean():.2%}")
    print(f"Median Margin of Safety: {df['Margin_of_Safety'].median():.2%}")
    print(f"\nMost undervalued: {df.iloc[0]['Ticker']} (Graham Ratio: {df.iloc[0]['Graham_Ratio']:.2f})")
    print(f"Most overvalued: {df.iloc[-1]['Ticker']} (Graham Ratio: {df.iloc[-1]['Graham_Ratio']:.2f})")


def save_results(df: pd.DataFrame, filename: str = 'graham_number_analysis.xlsx'):
    """
    Save results to Excel file
    
    Args:
        df: Ranked DataFrame
        filename: Output filename
    """
    if len(df) == 0:
        return
    
    # Create Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Standardized Rankings (for aggregation)
        rankings_df = df[['Ticker', 'Graham_Rank']].copy()
        rankings_df.to_excel(writer, sheet_name='Rankings', index=False)
        
        # Sheet 2: Detailed Rankings
        df.to_excel(writer, sheet_name='Detailed Rankings', index=False)
        
        # Sheet 3: Top 50 Stocks
        top_50 = df.head(50).copy()
        top_50.to_excel(writer, sheet_name='Top 50 Stocks', index=False)
        
        # Sheet 4: Methodology
        methodology = pd.DataFrame({
            'Section': [
                'Graham Number Formula',
                'Graham Number Formula',
                'Graham Number Formula',
                '',
                'Interpretation',
                'Interpretation',
                'Interpretation',
                'Interpretation',
                '',
                'Margin of Safety',
                'Margin of Safety',
                'Margin of Safety',
                '',
                'Graham Ratio',
                'Graham Ratio',
                'Graham Ratio',
                '',
                'Benjamin Graham',
                'Benjamin Graham',
                'Benjamin Graham',
                '',
                'Important Notes',
                'Important Notes',
                'Important Notes',
                'Important Notes',
                'Important Notes'
            ],
            'Description': [
                'Graham Number = √(22.5 × EPS × Book Value per Share)',
                '22.5 = Graham\'s constant (15 × 1.5)',
                '  - Max P/E of 15 × Max P/B of 1.5',
                '',
                'Graham Number represents intrinsic value',
                'Compare to current price to find undervalued stocks',
                'Lower Graham Ratio = More undervalued',
                'Higher Margin of Safety = Better value',
                '',
                'Margin of Safety = (Graham Number - Price) / Graham Number',
                'Positive = Undervalued (price below intrinsic value)',
                'Negative = Overvalued (price above intrinsic value)',
                '',
                'Graham Ratio = Current Price / Graham Number',
                '< 1.0 = Undervalued (trading below intrinsic value)',
                '> 1.0 = Overvalued (trading above intrinsic value)',
                '',
                'Benjamin Graham (1894-1976)',
                'Father of value investing',
                'Mentor to Warren Buffett',
                '',
                'This is a quantitative screening tool only',
                'Always research companies before investing',
                'Graham\'s formula is conservative by design',
                'Best used with other value metrics',
                'Not investment advice'
            ]
        })
        methodology.to_excel(writer, sheet_name='Methodology', index=False)
    
    print(f"\n{'='*140}")
    print(f"Results saved to {filename}")
    print(f"{'='*140}")


def main():
    """Main execution function"""
    print("="*140)
    print("BENJAMIN GRAHAM NUMBER CALCULATOR")
    print("="*140)
    print("\nCalculating intrinsic value using Graham's formula...")
    
    # Load data
    df = load_stock_data()
    
    # Calculate Graham Number
    graham_df = calculate_graham_number(df)
    
    if len(graham_df) > 0:
        # Display results
        display_results(graham_df, top_n=50)
        
        # Save to Excel
        save_results(graham_df)
        
        print("\n" + "="*140)
        print("ANALYSIS COMPLETE")
        print("="*140)
    else:
        print("\nNo valid data to analyze.")


if __name__ == "__main__":
    main()

