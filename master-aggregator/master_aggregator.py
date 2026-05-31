#!/usr/bin/env python3
"""
Master Investment Aggregator
Combines rankings from all investment tools to identify the best overall opportunities
"""

import pandas as pd
import sys
from pathlib import Path
import os
import time
from datetime import datetime


def load_rankings(tool_name: str, filename: str, rank_column: str) -> pd.DataFrame:
    """
    Load rankings from a tool's output file
    
    Args:
        tool_name: Name of the tool
        filename: Path to the Excel file
        rank_column: Name of the rank column
        
    Returns:
        DataFrame with Ticker and rank
    """
    try:
        df = pd.read_excel(filename, sheet_name='Rankings')
        if 'Ticker' not in df.columns or rank_column not in df.columns:
            print(f"Warning: {tool_name} - Missing required columns")
            return pd.DataFrame(columns=['Ticker', tool_name])
        
        # Rename rank column to tool name
        df = df[['Ticker', rank_column]].copy()
        df.columns = ['Ticker', tool_name]
        
        print(f"[SUCCESS] Loaded {len(df)} stocks from {tool_name}")
        return df
    except FileNotFoundError:
        print(f"[FAILED] {tool_name} - File not found: {filename}")
        return pd.DataFrame(columns=['Ticker', tool_name])
    except Exception as e:
        print(f"[FAILED] {tool_name} - Error loading: {e}")
        return pd.DataFrame(columns=['Ticker', tool_name])


def load_company_info() -> pd.DataFrame:
    """
    Load company information from the source data file
    
    Returns:
        DataFrame with Ticker, Company, Sector, and Industry columns
    """
    try:
        df = pd.read_excel('sp500_pe_sorted.xlsx', sheet_name='Stocks with PE')
        return df[['Ticker', 'Company', 'Sector', 'Industry']].copy()
    except Exception as e:
        print(f"Warning: Could not load company information: {e}")
        return pd.DataFrame(columns=['Ticker', 'Company', 'Sector', 'Industry'])


def aggregate_rankings() -> pd.DataFrame:
    """
    Aggregate rankings from all tools
    
    Returns:
        DataFrame with combined rankings
    """
    print("="*140)
    print("MASTER INVESTMENT AGGREGATOR")
    print("="*140)
    print("\nLoading rankings from all tools...\n")
    
    # Define all tools and their ranking files
    tools = {
        'Value_Ranker': {
            'file': 'value-ranker/sp500_value_ranked.xlsx',
            'rank_col': 'Overall_Rank'
        },
        'Magic_Formula': {
            'file': 'magic_formula_ranked.xlsx',
            'rank_col': 'MF_Rank'
        },
        'FCF_Analyzer': {
            'file': 'fcf_analysis.xlsx',
            'rank_col': 'FCF_Rank'
        },
        'Financial_Health': {
            'file': 'financial_health_analysis.xlsx',
            'rank_col': 'Health_Rank'
        },
        'Graham_Calculator': {
            'file': 'graham_number_analysis.xlsx',
            'rank_col': 'Graham_Rank'
        },
        'Dividend_Aristocrats': {
            'file': 'dividend_aristocrats_analysis.xlsx',
            'rank_col': 'Dividend_Rank'
        },
        'Historical_Valuation': {
            'file': 'historical_valuation_analysis.xlsx',
            'rank_col': 'Historical_Rank'
        },
        'Earnings_Quality': {
            'file': 'earnings_quality_analysis.xlsx',
            'rank_col': 'Quality_Rank'
        }
    }
    
    # Load all rankings
    rankings_list = []
    loaded_tools = []
    
    for tool_name, config in tools.items():
        df = load_rankings(tool_name, config['file'], config['rank_col'])
        if len(df) > 0:
            rankings_list.append(df)
            loaded_tools.append(tool_name)
    
    if len(rankings_list) == 0:
        print("\n[ERROR] No tool rankings found. Please run the individual tools first.")
        sys.exit(1)
    
    print(f"\n{'='*140}")
    print(f"Successfully loaded {len(loaded_tools)} tools: {', '.join(loaded_tools)}")
    print(f"{'='*140}\n")
    
    # Merge all rankings
    merged_df = rankings_list[0]
    for df in rankings_list[1:]:
        merged_df = merged_df.merge(df, on='Ticker', how='outer')
    
    # Add company information (names, sector, industry)
    company_info = load_company_info()
    if len(company_info) > 0:
        merged_df = merged_df.merge(company_info, on='Ticker', how='left')
        print(f"Added company information for {merged_df['Company'].notna().sum()} stocks\n")
    
    # Calculate average rank (lower is better)
    # Only average across tools where the stock has a ranking
    rank_columns = [col for col in merged_df.columns if col not in ['Ticker', 'Company', 'Sector', 'Industry']]
    
    # Calculate average rank (ignoring NaN values)
    merged_df['Average_Rank'] = merged_df[rank_columns].mean(axis=1, skipna=True)
    
    # Count how many tools ranked each stock
    merged_df['Tools_Count'] = merged_df[rank_columns].notna().sum(axis=1)
    
    # Calculate composite score (normalized to 1-500 scale)
    # Lower average rank = better score
    merged_df = merged_df.sort_values('Average_Rank', ascending=True)
    merged_df['Composite_Score'] = range(1, len(merged_df) + 1)
    
    # Calculate percentile (0-100, higher is better)
    merged_df['Percentile'] = 100 * (1 - (merged_df['Composite_Score'] - 1) / len(merged_df))
    
    # Add investment grade
    merged_df['Investment_Grade'] = merged_df['Percentile'].apply(classify_investment_grade)
    
    return merged_df, loaded_tools


def classify_investment_grade(percentile: float) -> str:
    """Classify stocks by investment grade based on percentile"""
    if percentile >= 90:
        return 'A+ (Exceptional)'
    elif percentile >= 80:
        return 'A (Excellent)'
    elif percentile >= 70:
        return 'B+ (Very Good)'
    elif percentile >= 60:
        return 'B (Good)'
    elif percentile >= 50:
        return 'C+ (Above Average)'
    elif percentile >= 40:
        return 'C (Average)'
    elif percentile >= 30:
        return 'D+ (Below Average)'
    elif percentile >= 20:
        return 'D (Poor)'
    else:
        return 'F (Very Poor)'


def calculate_sector_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate rankings within each sector
    
    Args:
        df: DataFrame with overall rankings and Sector column
        
    Returns:
        DataFrame with sector-specific rankings and best stock per sector
    """
    if 'Sector' not in df.columns:
        print("\n[WARNING] Sector column not found. Skipping sector-adjusted rankings.")
        return pd.DataFrame()
    
    # Filter out stocks without sector information
    df_with_sector = df[df['Sector'].notna()].copy()
    
    if len(df_with_sector) == 0:
        print("\n[WARNING] No stocks with sector information. Skipping sector-adjusted rankings.")
        return pd.DataFrame()
    
    # Calculate sector-specific rankings based on Composite_Score
    df_with_sector['Sector_Rank'] = df_with_sector.groupby('Sector')['Composite_Score'].rank(method='min')
    
    # Calculate sector percentile
    df_with_sector['Sector_Percentile'] = df_with_sector.groupby('Sector')['Composite_Score'].rank(pct=True) * 100
    
    # Get best stock per sector (lowest Composite_Score = best)
    best_per_sector = df_with_sector.loc[df_with_sector.groupby('Sector')['Composite_Score'].idxmin()].copy()
    
    # Sort by overall Composite_Score
    best_per_sector = best_per_sector.sort_values('Composite_Score')
    
    # Select relevant columns for display
    columns_to_show = ['Ticker', 'Company', 'Sector', 'Composite_Score', 'Investment_Grade',
                       'Percentile', 'Sector_Rank', 'Sector_Percentile', 'Average_Rank', 'Tools_Count']
    
    best_per_sector = best_per_sector[columns_to_show]
    
    return best_per_sector


def display_results(df: pd.DataFrame, loaded_tools: list, top_n: int = 50):
    """Display aggregated results"""
    print(f"\n{'='*140}")
    print(f"TOP {top_n} INVESTMENT OPPORTUNITIES - MASTER AGGREGATOR")
    print(f"{'='*140}")
    print(f"\nCombined rankings from {len(loaded_tools)} investment tools")
    print(f"Lower Composite Score = Better overall opportunity (1 = best, {len(df)} = worst)")
    print(f"\n{'='*140}\n")
    
    # Select columns to display
    display_cols = ['Composite_Score', 'Ticker', 'Company', 'Sector', 'Investment_Grade', 'Percentile',
                    'Average_Rank', 'Tools_Count'] + loaded_tools
    
    # Filter to available columns
    display_cols = [col for col in display_cols if col in df.columns]
    
    # Get top N stocks
    top_stocks = df.head(top_n)[display_cols].copy()
    
    # Format for display
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 25)
    
    print(top_stocks.to_string(index=False))
    
    # Summary statistics
    print(f"\n{'='*140}")
    print("SUMMARY STATISTICS")
    print(f"{'='*140}")
    print(f"Total stocks analyzed: {len(df)}")
    print(f"Stocks ranked by all {len(loaded_tools)} tools: {len(df[df['Tools_Count'] == len(loaded_tools)])}")
    print(f"Average tools per stock: {df['Tools_Count'].mean():.1f}")
    
    # Grade distribution
    print(f"\nInvestment Grade Distribution:")
    grade_counts = df['Investment_Grade'].value_counts().sort_index()
    for grade, count in grade_counts.items():
        print(f"  {grade}: {count} stocks ({count/len(df)*100:.1f}%)")
    
    # Sector concentration in top stocks
    if 'Sector' in df.columns:
        print(f"\nSector Distribution (Top 50 Stocks):")
        top_50_sectors = df.head(50)['Sector'].value_counts()
        for sector, count in top_50_sectors.head(10).items():
            print(f"  {sector}: {count} stocks ({count/50*100:.1f}%)")
    
    print(f"\nTop 10 Best Opportunities:")
    for i, row in df.head(10).iterrows():
        company = f" ({row['Company']})" if 'Company' in row and pd.notna(row['Company']) else ""
        print(f"  #{row['Composite_Score']}: {row['Ticker']}{company} - {row['Investment_Grade']} (Percentile: {row['Percentile']:.1f}%)")
    
    # Best stock per sector
    if 'Sector' in df.columns:
        sector_rankings = calculate_sector_rankings(df)
        if not sector_rankings.empty:
            print(f"\n{'='*140}")
            print("BEST STOCK PER SECTOR")
            print(f"{'='*140}")
            print(f"Showing the top-ranked stock in each sector\n")
            
            for i, row in sector_rankings.iterrows():
                company = f" ({row['Company']})" if 'Company' in row and pd.notna(row['Company']) else ""
                print(f"  {row['Sector']:25s} -> {row['Ticker']:6s}{company:40s} - Rank #{int(row['Composite_Score'])} overall, #{int(row['Sector_Rank'])} in sector")


def save_results(df: pd.DataFrame, loaded_tools: list, filename: str = 'master_investment_rankings.xlsx', export_csv: bool = True, timestamp: str = ''):
    """
    Save aggregated results to Excel file and optionally CSV
    
    Args:
        df: DataFrame with aggregated rankings
        loaded_tools: List of tool names
        filename: Excel output filename
        export_csv: Whether to also export CSV files
        timestamp: Timestamp string for display (e.g., "2026-05-31 16:50")
    """
    # Try to save Excel file with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Sheet 1: Top 100 Opportunities
                top_100 = df.head(100).copy()
                top_100.to_excel(writer, sheet_name='Top 100 Opportunities', index=False)
                
                # Sheet 2: All Rankings
                df.to_excel(writer, sheet_name='All Rankings', index=False)
                
                # Sheet 3: Grade A Stocks (Top 20%)
                grade_a = df[df['Percentile'] >= 80].copy()
                grade_a.to_excel(writer, sheet_name='Grade A Stocks', index=False)
                
                # Sheet 4: Grade B Stocks (60-80%)
                grade_b = df[(df['Percentile'] >= 60) & (df['Percentile'] < 80)].copy()
                grade_b.to_excel(writer, sheet_name='Grade B Stocks', index=False)
                
                # Sheet 5: Best Stock Per Sector
                sector_rankings = calculate_sector_rankings(df)
                if not sector_rankings.empty:
                    sector_rankings.to_excel(writer, sheet_name='Best Per Sector', index=False)
                
                # Sheet 6: Methodology
                methodology = pd.DataFrame({
                    'Section': [
                        'Master Aggregator',
                        'Master Aggregator',
                        'Master Aggregator',
                        '',
                        'Composite Score',
                        'Composite Score',
                        'Composite Score',
                        '',
                        'Investment Grades',
                        'Investment Grades',
                        'Investment Grades',
                        'Investment Grades',
                        'Investment Grades',
                        'Investment Grades',
                        '',
                        'Tools Included',
                        'Tools Included',
                        '',
                        'How to Use',
                        'How to Use',
                        'How to Use',
                        'How to Use',
                        '',
                        'Important Notes',
                        'Important Notes',
                        'Important Notes',
                        '',
                        'Last Updated'
                    ],
                    'Description': [
                        'Combines rankings from all investment analysis tools',
                        'Calculates average rank across all tools',
                        'Lower composite score = better overall opportunity',
                        '',
                        'Composite Score: 1 to ~500 (1 = best)',
                        'Average Rank: Mean of individual tool ranks',
                        'Percentile: 0-100 (higher = better)',
                        '',
                        'A+ (90-100%): Exceptional opportunities',
                        'A (80-90%): Excellent opportunities',
                        'B+ (70-80%): Very good opportunities',
                        'B (60-70%): Good opportunities',
                        'C (40-60%): Average opportunities',
                        'D/F (<40%): Below average opportunities',
                        '',
                        f'Currently using {len(loaded_tools)} tools:',
                        ', '.join(loaded_tools),
                        '',
                        'Focus on Grade A and B stocks',
                        'Research top 50 stocks in detail',
                        'Diversify across sectors',
                        'Combine with your own analysis',
                        '',
                        'This is a quantitative screening tool only',
                        'Always research companies before investing',
                        'Not investment advice',
                        '',
                        f'Last Updated: {timestamp if timestamp else "N/A"}'
                    ]
                })
                methodology.to_excel(writer, sheet_name='Methodology', index=False)
            break  # Success, exit retry loop
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"\n[WARNING] File '{filename}' is locked (possibly open in Excel).")
                print(f"Retrying in 2 seconds... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                print(f"\n[ERROR] Could not save '{filename}' - file is locked.")
                print("Please close the file in Excel and run the script again.")
                print("\nCSV exports will still be created if enabled.")
    
    print(f"\n{'='*140}")
    print(f"Results saved to {filename}")
    
    # Export CSV files if requested
    if export_csv:
        csv_dir = 'csv-exports'
        os.makedirs(csv_dir, exist_ok=True)
        
        # Generate timestamp for CSV filenames
        csv_timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # Export top 100 opportunities
        csv_top100 = f'{csv_dir}/top_100_opportunities_{csv_timestamp}.csv'
        df.head(100).to_csv(csv_top100, index=False)
        print(f"CSV export: {csv_top100}")
        
        # Export all rankings
        csv_all = f'{csv_dir}/all_rankings_{csv_timestamp}.csv'
        df.to_csv(csv_all, index=False)
        print(f"CSV export: {csv_all}")
        
        # Export Grade A stocks
        csv_grade_a = f'{csv_dir}/grade_a_stocks_{csv_timestamp}.csv'
        df[df['Percentile'] >= 80].to_csv(csv_grade_a, index=False)
        print(f"CSV export: {csv_grade_a}")
    
    print(f"{'='*140}")


def main():
    """Main execution function"""
    # Generate timestamp for this run
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Aggregate all rankings
    df, loaded_tools = aggregate_rankings()
    
    # Display results
    display_results(df, loaded_tools, top_n=50)
    
    # Save to Excel with timestamp
    save_results(df, loaded_tools, timestamp=timestamp)
    
    print("\n" + "="*140)
    print("MASTER AGGREGATION COMPLETE")
    print("="*140)
    print("\nNext Steps:")
    print("1. Review the top 50 stocks in 'master_investment_rankings.xlsx'")
    print("2. Focus on Grade A and B stocks (top 40%)")
    print("3. Research individual companies before investing")
    print("4. Diversify across sectors and strategies")
    print("5. Consider your own risk tolerance and investment goals")


if __name__ == "__main__":
    main()

