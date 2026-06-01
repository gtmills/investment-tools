#!/usr/bin/env python3
"""
Momentum Overlay Tool
Adds price momentum metrics to value rankings to identify stocks with both value and momentum
"""

import pandas as pd
import yfinance as yf
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time


def load_master_rankings() -> pd.DataFrame:
    """
    Load the master investment rankings
    
    Returns:
        DataFrame with master rankings
    """
    try:
        df = pd.read_excel('../master_investment_rankings.xlsx', sheet_name='All Rankings')
        print(f"[SUCCESS] Loaded {len(df)} stocks from master rankings")
        return df
    except FileNotFoundError:
        print("[ERROR] Master rankings file not found. Run master_aggregator.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load master rankings: {e}")
        sys.exit(1)


def fetch_momentum_data(ticker: str) -> dict:
    """
    Fetch momentum metrics for a single stock
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with momentum metrics
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get historical data for past year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=400)  # Extra buffer for trading days
        
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty or len(hist) < 60:
            return {
                '3M_Return': None,
                '6M_Return': None,
                '12M_Return': None,
                'Current_Price': None
            }
        
        # Get current price
        current_price = hist['Close'].iloc[-1]
        
        # Calculate returns
        returns = {}
        
        # 3-month return (approximately 63 trading days)
        if len(hist) >= 63:
            price_3m_ago = hist['Close'].iloc[-63]
            returns['3M_Return'] = ((current_price - price_3m_ago) / price_3m_ago) * 100
        else:
            returns['3M_Return'] = None
        
        # 6-month return (approximately 126 trading days)
        if len(hist) >= 126:
            price_6m_ago = hist['Close'].iloc[-126]
            returns['6M_Return'] = ((current_price - price_6m_ago) / price_6m_ago) * 100
        else:
            returns['6M_Return'] = None
        
        # 12-month return (approximately 252 trading days)
        if len(hist) >= 252:
            price_12m_ago = hist['Close'].iloc[-252]
            returns['12M_Return'] = ((current_price - price_12m_ago) / price_12m_ago) * 100
        else:
            returns['12M_Return'] = None
        
        returns['Current_Price'] = current_price
        
        return returns
        
    except Exception as e:
        print(f"  [WARNING] Failed to fetch momentum for {ticker}: {e}")
        return {
            '3M_Return': None,
            '6M_Return': None,
            '12M_Return': None,
            'Current_Price': None
        }


def add_momentum_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add momentum metrics to all stocks
    
    Args:
        df: Master rankings DataFrame
        
    Returns:
        DataFrame with momentum metrics added
    """
    print("\nFetching momentum data for all stocks...")
    print("This will take 5-10 minutes due to API rate limits.\n")
    
    momentum_data = []
    total = len(df)
    
    for idx, row in df.iterrows():
        ticker = row['Ticker']
        
        if (idx + 1) % 50 == 0:
            print(f"Progress: {idx + 1}/{total} stocks ({((idx + 1)/total)*100:.1f}%)")
        
        momentum = fetch_momentum_data(ticker)
        momentum_data.append(momentum)
        
        # Rate limiting
        time.sleep(0.1)
    
    # Add momentum columns
    momentum_df = pd.DataFrame(momentum_data)
    result_df = pd.concat([df, momentum_df], axis=1)
    
    print(f"\n[SUCCESS] Added momentum data for {total} stocks")
    
    return result_df


def calculate_momentum_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate composite momentum score
    
    Args:
        df: DataFrame with momentum metrics
        
    Returns:
        DataFrame with momentum score added
    """
    # Create momentum score (average of available returns)
    df['Momentum_Score'] = df[['3M_Return', '6M_Return', '12M_Return']].mean(axis=1)
    
    # Rank by momentum (higher is better)
    df['Momentum_Rank'] = df['Momentum_Score'].rank(ascending=False, na_option='bottom')
    
    # Classify momentum
    def classify_momentum(score):
        if pd.isna(score):
            return 'Unknown'
        elif score >= 20:
            return 'Strong Positive'
        elif score >= 10:
            return 'Moderate Positive'
        elif score >= 0:
            return 'Weak Positive'
        elif score >= -10:
            return 'Weak Negative'
        elif score >= -20:
            return 'Moderate Negative'
        else:
            return 'Strong Negative'
    
    df['Momentum_Category'] = df['Momentum_Score'].apply(classify_momentum)
    
    return df


def identify_value_momentum_stocks(df: pd.DataFrame, top_value_n: int = 100, 
                                   min_momentum: float = 0) -> pd.DataFrame:
    """
    Identify stocks with both strong value and positive momentum
    
    Args:
        df: DataFrame with value and momentum metrics
        top_value_n: Consider top N value stocks
        min_momentum: Minimum momentum score
        
    Returns:
        DataFrame with value+momentum stocks
    """
    # Get top value stocks
    top_value = df.nsmallest(top_value_n, 'Composite_Score')
    
    # Filter for positive momentum
    value_momentum = top_value[
        (top_value['Momentum_Score'] >= min_momentum) &
        (top_value['Momentum_Score'].notna())
    ].copy()
    
    # Sort by composite score
    value_momentum = value_momentum.sort_values('Composite_Score')
    
    return value_momentum


def generate_momentum_report(df: pd.DataFrame, value_momentum: pd.DataFrame) -> None:
    """
    Generate and display momentum analysis report
    
    Args:
        df: Full DataFrame with momentum
        value_momentum: Value+momentum stocks
    """
    print(f"\n{'='*140}")
    print("MOMENTUM OVERLAY ANALYSIS")
    print(f"{'='*140}\n")
    
    # Overall momentum statistics
    print("MOMENTUM STATISTICS")
    print("-" * 140)
    print(f"Stocks with momentum data: {df['Momentum_Score'].notna().sum()}")
    print(f"Average 3M return: {df['3M_Return'].mean():.2f}%")
    print(f"Average 6M return: {df['6M_Return'].mean():.2f}%")
    print(f"Average 12M return: {df['12M_Return'].mean():.2f}%")
    print(f"Average momentum score: {df['Momentum_Score'].mean():.2f}%")
    
    # Momentum category distribution
    print(f"\nMomentum Category Distribution:")
    momentum_dist = df['Momentum_Category'].value_counts()
    for category, count in momentum_dist.items():
        pct = (count / len(df)) * 100
        print(f"  {category:20s}: {count:3d} stocks ({pct:5.1f}%)")
    
    # Value + Momentum stocks
    print(f"\n{'='*140}")
    print(f"VALUE + MOMENTUM OPPORTUNITIES ({len(value_momentum)} stocks)")
    print(f"{'='*140}")
    print("Top value stocks (rank ≤100) with positive momentum\n")
    
    if len(value_momentum) > 0:
        print(f"{'Rank':<6} {'Ticker':<8} {'Company':<35} {'Grade':<8} {'3M%':<8} {'6M%':<8} {'12M%':<8} {'Mom Score':<10}")
        print("-" * 140)
        
        for _, row in value_momentum.head(20).iterrows():
            company = str(row['Company'])[:32] + "..." if len(str(row['Company'])) > 35 else row['Company']
            print(f"{int(row['Composite_Score']):<6} {row['Ticker']:<8} {company:<35} {row['Investment_Grade']:<8} "
                  f"{row['3M_Return']:>6.1f}% {row['6M_Return']:>6.1f}% {row['12M_Return']:>6.1f}% "
                  f"{row['Momentum_Score']:>8.1f}%")
        
        if len(value_momentum) > 20:
            print(f"\n... and {len(value_momentum) - 20} more stocks")
    else:
        print("No stocks found with both top value ranking and positive momentum.")
    
    # Falling knives warning
    print(f"\n{'='*140}")
    print("FALLING KNIVES WARNING")
    print(f"{'='*140}")
    print("Top value stocks with strong negative momentum (potential value traps)\n")
    
    top_value = df.nsmallest(100, 'Composite_Score')
    falling_knives = top_value[
        (top_value['Momentum_Score'] < -10) &
        (top_value['Momentum_Score'].notna())
    ].sort_values('Momentum_Score')
    
    if len(falling_knives) > 0:
        print(f"{'Rank':<6} {'Ticker':<8} {'Company':<35} {'Grade':<8} {'3M%':<8} {'6M%':<8} {'12M%':<8} {'Mom Score':<10}")
        print("-" * 140)
        
        for _, row in falling_knives.head(10).iterrows():
            company = str(row['Company'])[:32] + "..." if len(str(row['Company'])) > 35 else row['Company']
            print(f"{int(row['Composite_Score']):<6} {row['Ticker']:<8} {company:<35} {row['Investment_Grade']:<8} "
                  f"{row['3M_Return']:>6.1f}% {row['6M_Return']:>6.1f}% {row['12M_Return']:>6.1f}% "
                  f"{row['Momentum_Score']:>8.1f}%")
    else:
        print("No falling knives detected in top 100 value stocks.")


def save_momentum_analysis(df: pd.DataFrame, value_momentum: pd.DataFrame, filename: str) -> None:
    """
    Save momentum analysis to Excel file
    
    Args:
        df: Full DataFrame with momentum
        value_momentum: Value+momentum stocks
        filename: Output filename
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # All stocks with momentum
        output_cols = [
            'Composite_Score', 'Ticker', 'Company', 'Sector', 'Investment_Grade',
            '3M_Return', '6M_Return', '12M_Return', 'Momentum_Score', 'Momentum_Rank',
            'Momentum_Category', 'Tools_Count', 'Percentile'
        ]
        available_cols = [col for col in output_cols if col in df.columns]
        df[available_cols].to_excel(writer, sheet_name='All Stocks', index=False)
        
        # Value + Momentum opportunities
        if len(value_momentum) > 0:
            value_momentum[available_cols].to_excel(writer, sheet_name='Value + Momentum', index=False)
        
        # Falling knives
        top_value = df.nsmallest(100, 'Composite_Score')
        falling_knives = top_value[
            (top_value['Momentum_Score'] < -10) &
            (top_value['Momentum_Score'].notna())
        ].sort_values('Momentum_Score')
        
        if len(falling_knives) > 0:
            falling_knives[available_cols].to_excel(writer, sheet_name='Falling Knives', index=False)
        
        # Summary statistics
        summary_data = {
            'Metric': [
                'Total Stocks',
                'Stocks with Momentum Data',
                'Average 3M Return (%)',
                'Average 6M Return (%)',
                'Average 12M Return (%)',
                'Average Momentum Score (%)',
                'Value + Momentum Stocks',
                'Falling Knives (Top 100)',
                'Generated'
            ],
            'Value': [
                len(df),
                df['Momentum_Score'].notna().sum(),
                f"{df['3M_Return'].mean():.2f}",
                f"{df['6M_Return'].mean():.2f}",
                f"{df['12M_Return'].mean():.2f}",
                f"{df['Momentum_Score'].mean():.2f}",
                len(value_momentum),
                len(falling_knives),
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\n[SUCCESS] Momentum analysis saved to: {filename}")


def main():
    """Main execution function"""
    print("="*140)
    print("MOMENTUM OVERLAY TOOL")
    print("="*140)
    print("\nAdding price momentum metrics to value rankings")
    print("Identifies stocks with both value and momentum characteristics\n")
    
    # Load rankings
    df = load_master_rankings()
    
    # Add momentum metrics
    df = add_momentum_metrics(df)
    
    # Calculate momentum scores
    df = calculate_momentum_score(df)
    
    # Identify value + momentum stocks
    value_momentum = identify_value_momentum_stocks(df, top_value_n=100, min_momentum=0)
    
    # Generate report
    generate_momentum_report(df, value_momentum)
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'momentum_analysis_{timestamp}.xlsx'
    save_momentum_analysis(df, value_momentum, filename)
    
    print("\n" + "="*140)
    print("MOMENTUM ANALYSIS COMPLETE")
    print("="*140)
    print(f"\nKey Findings:")
    print(f"  - Value + Momentum stocks: {len(value_momentum)}")
    print(f"  - Average momentum score: {df['Momentum_Score'].mean():.2f}%")
    print(f"  - Stocks with positive momentum: {(df['Momentum_Score'] > 0).sum()}")
    print(f"\nOutput saved to: {filename}")
    print("\n" + "="*140)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution cancelled by user.")
        sys.exit(1)
