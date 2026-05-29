#!/usr/bin/env python3
"""
Dividend Aristocrats Screener
Identifies high-quality dividend stocks with consistent growth
"""

import pandas as pd
import yfinance as yf
import sys
from pathlib import Path
import time


def load_stock_data(filename: str = '../value-ranker/sp500_pe_sorted.xlsx') -> pd.DataFrame:
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


def fetch_dividend_history(tickers: list) -> dict:
    """
    Fetch dividend history for given tickers
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        Dictionary with dividend data per ticker
    """
    dividend_data = {}
    total = len(tickers)
    
    print(f"\nFetching dividend history for {total} stocks...")
    print("This may take several minutes...\n")
    
    for idx, ticker in enumerate(tickers, 1):
        try:
            stock = yf.Ticker(ticker)
            
            # Get dividend history
            dividends = stock.dividends
            
            if dividends is not None and len(dividends) > 0:
                # Get years with dividends
                dividend_years = dividends.groupby(dividends.index.year).sum()
                
                # Calculate consecutive years of dividends
                years_with_dividends = sorted(dividend_years[dividend_years > 0].index.tolist())
                
                consecutive_years = 0
                if len(years_with_dividends) > 0:
                    # Count consecutive years from most recent
                    current_year = years_with_dividends[-1]
                    consecutive_years = 1
                    
                    for i in range(len(years_with_dividends) - 2, -1, -1):
                        if years_with_dividends[i] == current_year - (len(years_with_dividends) - 1 - i):
                            consecutive_years += 1
                        else:
                            break
                
                # Calculate dividend growth rate (5-year CAGR if available)
                dividend_growth = None
                if len(dividend_years) >= 5:
                    recent_years = dividend_years.tail(5)
                    if len(recent_years) == 5 and recent_years.iloc[0] > 0:
                        start_div = recent_years.iloc[0]
                        end_div = recent_years.iloc[-1]
                        dividend_growth = (end_div / start_div) ** (1/4) - 1  # 4 years of growth
                
                # Get most recent annual dividend
                recent_dividend = dividend_years.iloc[-1] if len(dividend_years) > 0 else 0
                
                dividend_data[ticker] = {
                    'Consecutive_Years': consecutive_years,
                    'Dividend_Growth_5Y': dividend_growth,
                    'Recent_Annual_Dividend': recent_dividend,
                    'Total_Years_Paid': len(years_with_dividends)
                }
            else:
                dividend_data[ticker] = {
                    'Consecutive_Years': 0,
                    'Dividend_Growth_5Y': None,
                    'Recent_Annual_Dividend': 0,
                    'Total_Years_Paid': 0
                }
            
            # Progress indicator
            if idx % 50 == 0:
                print(f"Progress: {idx}/{total} stocks processed")
            
            # Small delay to avoid rate limiting
            time.sleep(0.15)
            
        except Exception as e:
            print(f"Error fetching dividend data for {ticker}: {e}")
            dividend_data[ticker] = {
                'Consecutive_Years': 0,
                'Dividend_Growth_5Y': None,
                'Recent_Annual_Dividend': 0,
                'Total_Years_Paid': 0
            }
    
    print(f"\nCompleted fetching dividend data for {total} stocks")
    return dividend_data


def analyze_dividend_stocks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze dividend stocks and calculate rankings
    
    Args:
        df: DataFrame with stock data
        
    Returns:
        DataFrame with dividend analysis and rankings
    """
    # Fetch dividend history
    dividend_data = fetch_dividend_history(df['Ticker'].tolist())
    
    # Add dividend data to dataframe
    div_df = df.copy()
    div_df['Consecutive_Years'] = div_df['Ticker'].map(lambda x: dividend_data.get(x, {}).get('Consecutive_Years', 0))
    div_df['Dividend_Growth_5Y'] = div_df['Ticker'].map(lambda x: dividend_data.get(x, {}).get('Dividend_Growth_5Y'))
    div_df['Recent_Annual_Dividend'] = div_df['Ticker'].map(lambda x: dividend_data.get(x, {}).get('Recent_Annual_Dividend', 0))
    div_df['Total_Years_Paid'] = div_df['Ticker'].map(lambda x: dividend_data.get(x, {}).get('Total_Years_Paid', 0))
    
    # Filter stocks with dividends
    div_df = div_df[div_df['Dividend Yield'] > 0].copy()
    
    print(f"\nStocks with dividend data: {len(div_df)}")
    
    if len(div_df) == 0:
        print("No stocks have dividend data.")
        return pd.DataFrame()
    
    # Calculate Dividend Safety Score (0-100)
    # Based on: Payout Ratio (lower is better), Consecutive Years, Debt/Equity
    div_df['Dividend_Safety_Score'] = 0
    
    # Payout ratio component (0-40 points)
    # Lower payout ratio = safer (more room for growth)
    div_df['Payout_Score'] = div_df['Payout Ratio'].apply(
        lambda x: 40 if pd.isna(x) or x <= 0 else max(0, 40 * (1 - min(x, 1)))
    )
    
    # Consecutive years component (0-30 points)
    # More years = more reliable
    div_df['Years_Score'] = div_df['Consecutive_Years'].apply(
        lambda x: min(30, x * 1.2)  # 25 years = 30 points
    )
    
    # Debt component (0-30 points)
    # Lower debt = safer dividends
    div_df['Debt_Score'] = div_df['Debt/Equity'].apply(
        lambda x: 30 if pd.isna(x) or x <= 0 else max(0, 30 * (1 - min(x / 2, 1)))
    )
    
    div_df['Dividend_Safety_Score'] = (
        div_df['Payout_Score'] + 
        div_df['Years_Score'] + 
        div_df['Debt_Score']
    )
    
    # Identify Dividend Aristocrats (25+ years)
    div_df['Is_Aristocrat'] = div_df['Consecutive_Years'] >= 25
    
    # Identify Dividend Achievers (10+ years)
    div_df['Is_Achiever'] = div_df['Consecutive_Years'] >= 10
    
    # Rank by different metrics
    # Dividend Yield Rank (higher yield = better, rank 1 = highest)
    div_df['Yield_Rank'] = div_df['Dividend Yield'].rank(method='min', ascending=False)
    
    # Consecutive Years Rank (more years = better, rank 1 = most years)
    div_df['Years_Rank'] = div_df['Consecutive_Years'].rank(method='min', ascending=False)
    
    # Dividend Growth Rank (higher growth = better, rank 1 = highest growth)
    valid_growth = div_df['Dividend_Growth_5Y'].notna()
    div_df.loc[valid_growth, 'Growth_Rank'] = div_df.loc[valid_growth, 'Dividend_Growth_5Y'].rank(method='min', ascending=False)
    
    # Safety Score Rank (higher score = better, rank 1 = safest)
    div_df['Safety_Rank'] = div_df['Dividend_Safety_Score'].rank(method='min', ascending=False)
    
    # Calculate Composite Dividend Score (average of ranks)
    # Only include growth rank if available
    div_df['Dividend_Score'] = div_df.apply(
        lambda row: (
            (row['Yield_Rank'] + row['Years_Rank'] + row['Safety_Rank'] + 
             (row['Growth_Rank'] if pd.notna(row.get('Growth_Rank')) else row['Yield_Rank'])) / 4
        ),
        axis=1
    )
    
    # Overall rank by composite score (lower score = better)
    div_df['Dividend_Rank'] = div_df['Dividend_Score'].rank(method='min', ascending=True)
    
    # Sort by composite score
    div_df = div_df.sort_values('Dividend_Score', ascending=True)
    
    # Add overall rank
    div_df['Overall_Rank'] = range(1, len(div_df) + 1)
    
    return div_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """
    Display dividend analysis results
    
    Args:
        df: Ranked DataFrame
        top_n: Number of top stocks to display
    """
    if len(df) == 0:
        return
    
    print(f"\n{'='*160}")
    print(f"TOP {top_n} DIVIDEND STOCKS - RANKED BY YIELD, GROWTH, CONSISTENCY, AND SAFETY")
    print(f"{'='*160}")
    
    # Show Dividend Aristocrats
    aristocrats = df[df['Is_Aristocrat'] == True]
    print(f"\nDividend Aristocrats (25+ years): {len(aristocrats)}")
    if len(aristocrats) > 0:
        print("Tickers:", ', '.join(aristocrats.head(20)['Ticker'].tolist()))
    
    # Show Dividend Achievers
    achievers = df[df['Is_Achiever'] == True]
    print(f"\nDividend Achievers (10+ years): {len(achievers)}")
    
    print(f"\n{'='*160}\n")
    
    # Select columns to display
    display_cols = [
        'Overall_Rank', 'Ticker', 'Company', 'Sector',
        'Dividend Yield', 'Consecutive_Years', 'Dividend_Growth_5Y',
        'Payout Ratio', 'Dividend_Safety_Score',
        'Current Price', 'P/E Ratio', 'ROE', 'Debt/Equity',
        'Is_Aristocrat'
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
    print(f"\n{'='*160}")
    print("SUMMARY STATISTICS")
    print(f"{'='*160}")
    print(f"Total dividend-paying stocks: {len(df)}")
    print(f"Dividend Aristocrats (25+ years): {len(aristocrats)}")
    print(f"Dividend Achievers (10+ years): {len(achievers)}")
    print(f"\nAverage Dividend Yield: {df['Dividend Yield'].mean():.2%}")
    print(f"Median Dividend Yield: {df['Dividend Yield'].median():.2%}")
    print(f"Highest Dividend Yield: {df['Dividend Yield'].max():.2%} ({df.loc[df['Dividend Yield'].idxmax(), 'Ticker']})")
    print(f"\nAverage Consecutive Years: {df['Consecutive_Years'].mean():.1f}")
    print(f"Median Consecutive Years: {df['Consecutive_Years'].median():.1f}")
    print(f"Longest Streak: {df['Consecutive_Years'].max():.0f} years ({df.loc[df['Consecutive_Years'].idxmax(), 'Ticker']})")
    
    if df['Dividend_Growth_5Y'].notna().any():
        valid_growth = df[df['Dividend_Growth_5Y'].notna()]
        print(f"\nAverage 5Y Dividend Growth: {valid_growth['Dividend_Growth_5Y'].mean():.2%}")
        print(f"Median 5Y Dividend Growth: {valid_growth['Dividend_Growth_5Y'].median():.2%}")
    
    print(f"\nAverage Dividend Safety Score: {df['Dividend_Safety_Score'].mean():.1f}/100")
    print(f"Median Dividend Safety Score: {df['Dividend_Safety_Score'].median():.1f}/100")


def save_results(df: pd.DataFrame, filename: str = 'dividend_aristocrats_analysis.xlsx'):
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
        rankings_df = df[['Ticker', 'Dividend_Rank']].copy()
        rankings_df.to_excel(writer, sheet_name='Rankings', index=False)
        
        # Sheet 2: Detailed Rankings
        df.to_excel(writer, sheet_name='Detailed Rankings', index=False)
        
        # Sheet 3: Dividend Aristocrats (25+ years)
        aristocrats = df[df['Is_Aristocrat'] == True].copy()
        if len(aristocrats) > 0:
            aristocrats.to_excel(writer, sheet_name='Dividend Aristocrats', index=False)
        
        # Sheet 4: Top 50 Stocks
        top_50 = df.head(50).copy()
        top_50.to_excel(writer, sheet_name='Top 50 Stocks', index=False)
        
        # Sheet 5: Methodology
        methodology = pd.DataFrame({
            'Section': [
                'Dividend Aristocrats',
                'Dividend Aristocrats',
                'Dividend Achievers',
                '',
                'Dividend Safety Score',
                'Dividend Safety Score',
                'Dividend Safety Score',
                'Dividend Safety Score',
                '',
                'Ranking Methodology',
                'Ranking Methodology',
                'Ranking Methodology',
                'Ranking Methodology',
                'Ranking Methodology',
                '',
                'Interpretation',
                'Interpretation',
                'Interpretation',
                'Interpretation',
                '',
                'Important Notes',
                'Important Notes',
                'Important Notes',
                'Important Notes'
            ],
            'Description': [
                'S&P 500 stocks with 25+ consecutive years of dividend increases',
                'Elite group of reliable dividend payers',
                '10+ consecutive years of dividend increases',
                '',
                'Composite score (0-100) based on:',
                '  - Payout Ratio (40 points): Lower is safer',
                '  - Consecutive Years (30 points): More is better',
                '  - Debt/Equity (30 points): Lower is safer',
                '',
                'Stocks ranked by four metrics:',
                '  1. Dividend Yield (higher = better)',
                '  2. Consecutive Years (more = better)',
                '  3. Dividend Growth (higher = better)',
                '  4. Safety Score (higher = better)',
                '',
                'Top-ranked stocks combine high yield with safety',
                'Aristocrats offer reliability and growth',
                'High safety scores indicate sustainable dividends',
                'Consider total return (yield + growth)',
                '',
                'This is a quantitative screening tool only',
                'Always research companies before investing',
                'Past dividend growth doesn\'t guarantee future increases',
                'Not investment advice'
            ]
        })
        methodology.to_excel(writer, sheet_name='Methodology', index=False)
    
    print(f"\n{'='*160}")
    print(f"Results saved to {filename}")
    print(f"{'='*160}")


def main():
    """Main execution function"""
    print("="*160)
    print("DIVIDEND ARISTOCRATS SCREENER")
    print("="*160)
    print("\nAnalyzing dividend-paying stocks for yield, growth, and safety...")
    
    # Load data
    df = load_stock_data()
    
    # Analyze dividend stocks
    div_df = analyze_dividend_stocks(df)
    
    if len(div_df) > 0:
        # Display results
        display_results(div_df, top_n=50)
        
        # Save to Excel
        save_results(div_df)
        
        print("\n" + "="*160)
        print("ANALYSIS COMPLETE")
        print("="*160)
    else:
        print("\nNo valid dividend data to analyze.")


if __name__ == "__main__":
    main()

