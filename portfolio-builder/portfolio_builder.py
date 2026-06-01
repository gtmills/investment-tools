#!/usr/bin/env python3
"""
Portfolio Builder Tool
Generates diversified portfolios from top-ranked stocks with sector and position constraints
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime


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


def build_portfolio(df: pd.DataFrame, portfolio_size: int = 20, 
                   max_sector_pct: float = 0.30, max_position_pct: float = 0.10,
                   min_tools: int = 6, max_rank: int = 150) -> pd.DataFrame:
    """
    Build a diversified portfolio from top-ranked stocks
    
    Args:
        df: Master rankings DataFrame
        portfolio_size: Number of stocks in portfolio
        max_sector_pct: Maximum percentage per sector (e.g., 0.30 = 30%)
        max_position_pct: Maximum percentage per stock (e.g., 0.10 = 10%)
        min_tools: Minimum number of tools that must rank the stock
        max_rank: Maximum composite score to consider
        
    Returns:
        DataFrame with portfolio stocks and allocations
    """
    # Filter stocks by criteria
    filtered = df[
        (df['Tools_Count'] >= min_tools) &
        (df['Composite_Score'] <= max_rank)
    ].copy()
    
    if len(filtered) < portfolio_size:
        print(f"[WARNING] Only {len(filtered)} stocks meet criteria. Adjusting portfolio size.")
        portfolio_size = len(filtered)
    
    # Sort by composite score (best first)
    filtered = filtered.sort_values('Composite_Score')
    
    # Build portfolio with sector constraints
    portfolio = []
    sector_counts = {}
    max_per_sector = int(portfolio_size * max_sector_pct)
    
    for _, row in filtered.iterrows():
        if len(portfolio) >= portfolio_size:
            break
            
        sector = row['Sector']
        sector_count = sector_counts.get(sector, 0)
        
        # Check sector constraint
        if sector_count < max_per_sector:
            portfolio.append(row)
            sector_counts[sector] = sector_count + 1
    
    # Convert to DataFrame
    portfolio_df = pd.DataFrame(portfolio)
    
    # Calculate equal-weight allocations (respecting max position size)
    base_weight = 1.0 / len(portfolio_df)
    max_weight = max_position_pct
    
    if base_weight > max_weight:
        print(f"[WARNING] Equal weight ({base_weight:.1%}) exceeds max position size ({max_weight:.1%})")
        portfolio_df['Weight'] = max_weight
    else:
        portfolio_df['Weight'] = base_weight
    
    # Normalize weights to sum to 100%
    total_weight = portfolio_df['Weight'].sum()
    portfolio_df['Weight'] = portfolio_df['Weight'] / total_weight
    portfolio_df['Weight_Pct'] = portfolio_df['Weight'] * 100
    
    return portfolio_df


def generate_portfolio_report(portfolio_df: pd.DataFrame, strategy_name: str) -> None:
    """
    Generate and display portfolio report
    
    Args:
        portfolio_df: Portfolio DataFrame
        strategy_name: Name of the strategy
    """
    print(f"\n{'='*140}")
    print(f"PORTFOLIO: {strategy_name}")
    print(f"{'='*140}\n")
    
    # Portfolio summary
    print(f"Total Stocks: {len(portfolio_df)}")
    print(f"Average Composite Score: {portfolio_df['Composite_Score'].mean():.1f}")
    print(f"Average Tools Coverage: {portfolio_df['Tools_Count'].mean():.1f}")
    print(f"Grade Distribution:")
    grade_dist = portfolio_df['Investment_Grade'].value_counts().sort_index()
    for grade, count in grade_dist.items():
        pct = (count / len(portfolio_df)) * 100
        print(f"  {grade}: {count} stocks ({pct:.1f}%)")
    
    # Sector allocation
    print(f"\nSector Allocation:")
    sector_weights = portfolio_df.groupby('Sector')['Weight_Pct'].sum().sort_values(ascending=False)
    for sector, weight in sector_weights.items():
        count = len(portfolio_df[portfolio_df['Sector'] == sector])
        print(f"  {sector:30s}: {weight:5.1f}% ({count} stocks)")
    
    # Top holdings
    print(f"\nTop 10 Holdings:")
    print(f"{'Rank':<6} {'Ticker':<8} {'Company':<40} {'Sector':<25} {'Grade':<8} {'Weight':<8} {'Score':<8}")
    print("-" * 140)
    
    for idx, row in portfolio_df.head(10).iterrows():
        company = row['Company'][:37] + "..." if len(str(row['Company'])) > 40 else row['Company']
        print(f"{int(row['Composite_Score']):<6} {row['Ticker']:<8} {company:<40} {row['Sector']:<25} "
              f"{row['Investment_Grade']:<8} {row['Weight_Pct']:>6.2f}% {int(row['Composite_Score']):<8}")


def save_portfolio(portfolio_df: pd.DataFrame, strategy_name: str, filename: str) -> None:
    """
    Save portfolio to Excel file
    
    Args:
        portfolio_df: Portfolio DataFrame
        strategy_name: Name of the strategy
        filename: Output filename
    """
    # Select relevant columns
    output_cols = [
        'Composite_Score', 'Ticker', 'Company', 'Sector', 'Industry',
        'Investment_Grade', 'Percentile', 'Tools_Count', 'Weight_Pct',
        'Value_Ranker', 'Magic_Formula', 'FCF_Analyzer', 'Financial_Health',
        'Graham_Calculator', 'Dividend_Aristocrats', 'Historical_Valuation', 'Earnings_Quality'
    ]
    
    # Filter to available columns
    available_cols = [col for col in output_cols if col in portfolio_df.columns]
    output_df = portfolio_df[available_cols].copy()
    
    # Rename for clarity
    output_df = output_df.rename(columns={
        'Composite_Score': 'Rank',
        'Weight_Pct': 'Weight_%'
    })
    
    # Create Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Portfolio sheet
        output_df.to_excel(writer, sheet_name='Portfolio', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': [
                'Strategy Name',
                'Portfolio Size',
                'Total Weight',
                'Average Rank',
                'Average Tools Coverage',
                'Best Rank',
                'Worst Rank',
                'Generation Date'
            ],
            'Value': [
                strategy_name,
                len(portfolio_df),
                f"{portfolio_df['Weight_Pct'].sum():.1f}%",
                f"{portfolio_df['Composite_Score'].mean():.1f}",
                f"{portfolio_df['Tools_Count'].mean():.1f}",
                int(portfolio_df['Composite_Score'].min()),
                int(portfolio_df['Composite_Score'].max()),
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sector allocation sheet
        sector_summary = portfolio_df.groupby('Sector').agg({
            'Weight_Pct': 'sum',
            'Ticker': 'count',
            'Composite_Score': 'mean'
        }).round(2)
        sector_summary.columns = ['Weight_%', 'Stock_Count', 'Avg_Rank']
        sector_summary = sector_summary.sort_values('Weight_%', ascending=False)
        sector_summary.to_excel(writer, sheet_name='Sector Allocation')
    
    print(f"\n[SUCCESS] Portfolio saved to: {filename}")


def main():
    """Main execution function"""
    print("="*140)
    print("PORTFOLIO BUILDER TOOL")
    print("="*140)
    print("\nGenerates diversified portfolios from top-ranked stocks")
    print("Applies sector and position size constraints for risk management\n")
    
    # Load master rankings
    df = load_master_rankings()
    
    # Define portfolio strategies
    strategies = [
        {
            'name': 'Conservative Portfolio',
            'size': 20,
            'max_sector_pct': 0.25,
            'max_position_pct': 0.08,
            'min_tools': 7,
            'max_rank': 100,
            'filename': 'portfolio_conservative.xlsx'
        },
        {
            'name': 'Balanced Portfolio',
            'size': 25,
            'max_sector_pct': 0.30,
            'max_position_pct': 0.10,
            'min_tools': 6,
            'max_rank': 150,
            'filename': 'portfolio_balanced.xlsx'
        },
        {
            'name': 'Aggressive Portfolio',
            'size': 30,
            'max_sector_pct': 0.35,
            'max_position_pct': 0.12,
            'min_tools': 5,
            'max_rank': 200,
            'filename': 'portfolio_aggressive.xlsx'
        }
    ]
    
    # Generate each portfolio
    for strategy in strategies:
        portfolio = build_portfolio(
            df,
            portfolio_size=strategy['size'],
            max_sector_pct=strategy['max_sector_pct'],
            max_position_pct=strategy['max_position_pct'],
            min_tools=strategy['min_tools'],
            max_rank=strategy['max_rank']
        )
        
        generate_portfolio_report(portfolio, strategy['name'])
        save_portfolio(portfolio, strategy['name'], strategy['filename'])
        print()
    
    print("="*140)
    print("PORTFOLIO GENERATION COMPLETE")
    print("="*140)
    print("\nGenerated 3 portfolio strategies:")
    print("  1. portfolio_conservative.xlsx - 20 stocks, top 100 ranks, 7+ tools")
    print("  2. portfolio_balanced.xlsx     - 25 stocks, top 150 ranks, 6+ tools")
    print("  3. portfolio_aggressive.xlsx   - 30 stocks, top 200 ranks, 5+ tools")
    print("\nEach portfolio includes:")
    print("  - Sector diversification (max 25-35% per sector)")
    print("  - Position size limits (max 8-12% per stock)")
    print("  - Equal-weight allocation within constraints")
    print("  - Detailed holdings and sector breakdown")
    print("\n" + "="*140)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution cancelled by user.")
        sys.exit(1)
