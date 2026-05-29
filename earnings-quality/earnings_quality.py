#!/usr/bin/env python3
"""
Earnings Quality Analyzer
Analyzes the quality of reported earnings by comparing to cash flow
"""

import pandas as pd
import sys
from pathlib import Path


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


def analyze_earnings_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze earnings quality based on available metrics
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with earnings quality analysis and rankings
    """
    eq_df = df.copy()
    
    # Calculate Earnings Quality Score (0-100)
    eq_df['Earnings_Quality_Score'] = 0
    
    # Component 1: Profit Margin (0-25 points)
    # Higher profit margin = better quality
    eq_df['Margin_Score'] = eq_df['Profit Margin'].apply(
        lambda x: min(25, x * 100) if pd.notna(x) and x > 0 else 0
    )
    
    # Component 2: ROE (0-25 points)
    # Higher ROE = better quality
    eq_df['ROE_Score'] = eq_df['ROE'].apply(
        lambda x: min(25, x * 100) if pd.notna(x) and x > 0 else 0
    )
    
    # Component 3: ROA (0-25 points)
    # Higher ROA = better quality
    eq_df['ROA_Score'] = eq_df['ROA'].apply(
        lambda x: min(25, x * 100) if pd.notna(x) and x > 0 else 0
    )
    
    # Component 4: Operating Margin (0-25 points)
    # Higher operating margin = better quality
    eq_df['OpMargin_Score'] = eq_df['Operating Margin'].apply(
        lambda x: min(25, x * 100) if pd.notna(x) and x > 0 else 0
    )
    
    # Calculate total earnings quality score
    eq_df['Earnings_Quality_Score'] = (
        eq_df['Margin_Score'] + 
        eq_df['ROE_Score'] + 
        eq_df['ROA_Score'] + 
        eq_df['OpMargin_Score']
    )
    
    # Calculate Accrual Ratio (simplified)
    # Lower accruals = higher quality (more cash-backed earnings)
    # Accrual Ratio ≈ (Net Income - Operating Cash Flow) / Total Assets
    # We'll use a proxy based on profit margin consistency
    
    # Filter stocks with valid data
    valid_stocks = (
        eq_df['Profit Margin'].notna() & 
        eq_df['ROE'].notna() &
        eq_df['Earnings_Quality_Score'] > 0
    )
    eq_df = eq_df[valid_stocks].copy()
    
    print(f"\nStocks with valid earnings quality data: {len(eq_df)}")
    
    if len(eq_df) == 0:
        print("No stocks have valid earnings quality metrics.")
        return pd.DataFrame()
    
    # Rank by earnings quality score (higher = better quality)
    eq_df['Quality_Rank'] = eq_df['Earnings_Quality_Score'].rank(method='min', ascending=False)
    
    # Rank by profit margin
    eq_df['Margin_Rank'] = eq_df['Profit Margin'].rank(method='min', ascending=False)
    
    # Rank by ROE
    eq_df['ROE_Rank'] = eq_df['ROE'].rank(method='min', ascending=False)
    
    # Calculate composite rank
    eq_df['Composite_Rank'] = (eq_df['Quality_Rank'] + eq_df['Margin_Rank'] + eq_df['ROE_Rank']) / 3
    
    # Sort by composite rank
    eq_df = eq_df.sort_values('Composite_Rank', ascending=True)
    
    # Add overall rank
    eq_df['Overall_Rank'] = range(1, len(eq_df) + 1)
    
    return eq_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """Display earnings quality results"""
    if len(df) == 0:
        return
    
    print(f"\n{'='*140}")
    print(f"TOP {top_n} STOCKS - HIGHEST EARNINGS QUALITY")
    print(f"{'='*140}")
    print(f"\nEarnings Quality Score based on profitability metrics")
    print(f"Higher score = better quality earnings")
    print(f"\n{'='*140}\n")
    
    # Select columns to display
    display_cols = [
        'Overall_Rank', 'Ticker', 'Company', 'Sector',
        'Earnings_Quality_Score',
        'Profit Margin', 'Operating Margin', 'ROE', 'ROA',
        'P/E Ratio', 'Current Price', 'Market Cap'
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
    print(f"High quality (score > 75): {len(df[df['Earnings_Quality_Score'] > 75])}")
    print(f"Good quality (score 50-75): {len(df[(df['Earnings_Quality_Score'] >= 50) & (df['Earnings_Quality_Score'] <= 75)])}")
    print(f"Average quality (score < 50): {len(df[df['Earnings_Quality_Score'] < 50])}")
    print(f"\nAverage Quality Score: {df['Earnings_Quality_Score'].mean():.1f}/100")
    print(f"Median Quality Score: {df['Earnings_Quality_Score'].median():.1f}/100")
    print(f"\nHighest quality: {df.iloc[0]['Ticker']} (Score: {df.iloc[0]['Earnings_Quality_Score']:.1f})")
    print(f"Average Profit Margin: {df['Profit Margin'].mean():.2%}")
    print(f"Average ROE: {df['ROE'].mean():.2%}")


def save_results(df: pd.DataFrame, filename: str = 'earnings_quality_analysis.xlsx'):
    """Save results to Excel file"""
    if len(df) == 0:
        return
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Standardized Rankings
        rankings_df = df[['Ticker', 'Quality_Rank']].copy()
        rankings_df.to_excel(writer, sheet_name='Rankings', index=False)
        
        # Sheet 2: Detailed Rankings
        df.to_excel(writer, sheet_name='Detailed Rankings', index=False)
        
        # Sheet 3: Top 50 Stocks
        top_50 = df.head(50).copy()
        top_50.to_excel(writer, sheet_name='Top 50 Stocks', index=False)
        
        # Sheet 4: Methodology
        methodology = pd.DataFrame({
            'Section': [
                'Earnings Quality Score',
                'Earnings Quality Score',
                'Earnings Quality Score',
                'Earnings Quality Score',
                'Earnings Quality Score',
                '',
                'Interpretation',
                'Interpretation',
                'Interpretation',
                'Interpretation',
                '',
                'Important Notes',
                'Important Notes',
                'Important Notes'
            ],
            'Description': [
                'Composite score (0-100) based on:',
                '  - Profit Margin (0-25 points)',
                '  - ROE (0-25 points)',
                '  - ROA (0-25 points)',
                '  - Operating Margin (0-25 points)',
                '',
                'Score > 75: High quality earnings',
                'Score 50-75: Good quality earnings',
                'Score 25-50: Average quality earnings',
                'Score < 25: Low quality earnings',
                '',
                'This is a quantitative screening tool only',
                'Always research companies before investing',
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
    print("EARNINGS QUALITY ANALYZER")
    print("="*140)
    print("\nAnalyzing earnings quality based on profitability metrics...")
    
    # Load data
    df = load_stock_data()
    
    # Analyze earnings quality
    eq_df = analyze_earnings_quality(df)
    
    if len(eq_df) > 0:
        # Display results
        display_results(eq_df, top_n=50)
        
        # Save to Excel
        save_results(eq_df)
        
        print("\n" + "="*140)
        print("ANALYSIS COMPLETE")
        print("="*140)
    else:
        print("\nNo valid data to analyze.")


if __name__ == "__main__":
    main()

