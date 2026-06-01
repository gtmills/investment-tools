#!/usr/bin/env python3
"""
Alert System
Monitors ranking changes and identifies significant movements in stock rankings
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import os


def load_current_rankings() -> pd.DataFrame:
    """
    Load the current master rankings
    
    Returns:
        DataFrame with current rankings
    """
    try:
        df = pd.read_excel('../master_investment_rankings.xlsx', sheet_name='All Rankings')
        print(f"[SUCCESS] Loaded {len(df)} current rankings")
        return df
    except FileNotFoundError:
        print("[ERROR] Current rankings file not found. Run master_aggregator.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load current rankings: {e}")
        sys.exit(1)


def load_previous_rankings() -> pd.DataFrame:
    """
    Load the most recent historical rankings
    
    Returns:
        DataFrame with previous rankings, or None if not found
    """
    historical_dir = Path('../historical-data')
    
    if not historical_dir.exists():
        print("[INFO] No historical data found. This appears to be the first run.")
        return None
    
    # Find most recent historical file
    ranking_files = sorted(historical_dir.glob('rankings_*.xlsx'), reverse=True)
    
    if not ranking_files:
        print("[INFO] No previous rankings found. This appears to be the first run.")
        return None
    
    try:
        previous_file = ranking_files[0]
        df = pd.read_excel(previous_file, sheet_name='All Rankings')
        print(f"[SUCCESS] Loaded {len(df)} previous rankings from {previous_file.name}")
        return df
    except Exception as e:
        print(f"[WARNING] Failed to load previous rankings: {e}")
        return None


def detect_grade_upgrades(current_df: pd.DataFrame, previous_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect stocks that upgraded to Grade A or A+
    
    Args:
        current_df: Current rankings
        previous_df: Previous rankings
        
    Returns:
        DataFrame with upgraded stocks
    """
    if previous_df is None:
        return pd.DataFrame()
    
    # Merge on ticker
    merged = current_df.merge(
        previous_df[['Ticker', 'Investment_Grade', 'Composite_Score']],
        on='Ticker',
        suffixes=('_current', '_previous'),
        how='inner'
    )
    
    # Define grade hierarchy
    grade_order = {'F': 0, 'D': 1, 'C': 2, 'B': 3, 'B+': 4, 'A': 5, 'A+': 6}
    
    # Find upgrades to A or A+
    upgrades = merged[
        (merged['Investment_Grade_current'].isin(['A', 'A+'])) &
        (~merged['Investment_Grade_previous'].isin(['A', 'A+']))
    ].copy()
    
    if len(upgrades) > 0:
        upgrades['Rank_Change'] = upgrades['Composite_Score_previous'] - upgrades['Composite_Score_current']
        upgrades = upgrades.sort_values('Composite_Score_current')
    
    return upgrades


def detect_significant_movers(current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                              threshold: int = 50) -> tuple:
    """
    Detect stocks with significant ranking changes
    
    Args:
        current_df: Current rankings
        previous_df: Previous rankings
        threshold: Minimum rank change to be considered significant
        
    Returns:
        Tuple of (improvers, decliners) DataFrames
    """
    if previous_df is None:
        return pd.DataFrame(), pd.DataFrame()
    
    # Merge on ticker
    merged = current_df.merge(
        previous_df[['Ticker', 'Composite_Score', 'Investment_Grade']],
        on='Ticker',
        suffixes=('_current', '_previous'),
        how='inner'
    )
    
    # Calculate rank change (negative = improvement)
    merged['Rank_Change'] = merged['Composite_Score_current'] - merged['Composite_Score_previous']
    
    # Significant improvers (rank decreased by threshold or more)
    improvers = merged[merged['Rank_Change'] <= -threshold].copy()
    improvers = improvers.sort_values('Rank_Change')
    
    # Significant decliners (rank increased by threshold or more)
    decliners = merged[merged['Rank_Change'] >= threshold].copy()
    decliners = decliners.sort_values('Rank_Change', ascending=False)
    
    return improvers, decliners


def detect_new_top_stocks(current_df: pd.DataFrame, previous_df: pd.DataFrame, 
                         top_n: int = 50) -> pd.DataFrame:
    """
    Detect stocks newly entering the top N
    
    Args:
        current_df: Current rankings
        previous_df: Previous rankings
        top_n: Top N threshold
        
    Returns:
        DataFrame with new top stocks
    """
    if previous_df is None:
        return pd.DataFrame()
    
    # Get current top N tickers
    current_top = set(current_df.nsmallest(top_n, 'Composite_Score')['Ticker'])
    
    # Get previous top N tickers
    previous_top = set(previous_df.nsmallest(top_n, 'Composite_Score')['Ticker'])
    
    # Find new entries
    new_entries = current_top - previous_top
    
    if not new_entries:
        return pd.DataFrame()
    
    # Get details for new entries
    new_stocks = current_df[current_df['Ticker'].isin(new_entries)].copy()
    
    # Add previous rank if available
    previous_ranks = previous_df.set_index('Ticker')['Composite_Score'].to_dict()
    new_stocks['Previous_Rank'] = new_stocks['Ticker'].map(previous_ranks)
    new_stocks['Rank_Improvement'] = new_stocks['Previous_Rank'] - new_stocks['Composite_Score']
    
    new_stocks = new_stocks.sort_values('Composite_Score')
    
    return new_stocks


def generate_alert_report(upgrades: pd.DataFrame, improvers: pd.DataFrame, 
                         decliners: pd.DataFrame, new_top: pd.DataFrame) -> None:
    """
    Generate and display alert report
    
    Args:
        upgrades: Stocks upgraded to Grade A/A+
        improvers: Significant improvers
        decliners: Significant decliners
        new_top: New entries to top 50
    """
    print(f"\n{'='*140}")
    print("INVESTMENT ALERT SYSTEM - RANKING CHANGES DETECTED")
    print(f"{'='*140}\n")
    
    # Grade upgrades
    if len(upgrades) > 0:
        print(f"🎯 GRADE UPGRADES TO A/A+ ({len(upgrades)} stocks)")
        print("-" * 140)
        print(f"{'Ticker':<8} {'Company':<40} {'Sector':<25} {'Old Grade':<12} {'New Grade':<12} {'Rank Change':<12}")
        print("-" * 140)
        
        for _, row in upgrades.head(10).iterrows():
            company = str(row['Company'])[:37] + "..." if len(str(row['Company'])) > 40 else row['Company']
            print(f"{row['Ticker']:<8} {company:<40} {row['Sector']:<25} "
                  f"{row['Investment_Grade_previous']:<12} {row['Investment_Grade_current']:<12} "
                  f"+{int(row['Rank_Change']):<11}")
        
        if len(upgrades) > 10:
            print(f"... and {len(upgrades) - 10} more")
        print()
    else:
        print("✓ No grade upgrades to A/A+ detected\n")
    
    # Significant improvers
    if len(improvers) > 0:
        print(f"📈 SIGNIFICANT IMPROVERS ({len(improvers)} stocks with +50 rank improvement)")
        print("-" * 140)
        print(f"{'Ticker':<8} {'Company':<40} {'Sector':<25} {'Old Rank':<10} {'New Rank':<10} {'Change':<10}")
        print("-" * 140)
        
        for _, row in improvers.head(10).iterrows():
            company = str(row['Company'])[:37] + "..." if len(str(row['Company'])) > 40 else row['Company']
            print(f"{row['Ticker']:<8} {company:<40} {row['Sector']:<25} "
                  f"{int(row['Composite_Score_previous']):<10} {int(row['Composite_Score_current']):<10} "
                  f"{int(row['Rank_Change']):<10}")
        
        if len(improvers) > 10:
            print(f"... and {len(improvers) - 10} more")
        print()
    else:
        print("✓ No significant improvers detected\n")
    
    # Significant decliners
    if len(decliners) > 0:
        print(f"📉 SIGNIFICANT DECLINERS ({len(decliners)} stocks with -50 rank decline)")
        print("-" * 140)
        print(f"{'Ticker':<8} {'Company':<40} {'Sector':<25} {'Old Rank':<10} {'New Rank':<10} {'Change':<10}")
        print("-" * 140)
        
        for _, row in decliners.head(10).iterrows():
            company = str(row['Company'])[:37] + "..." if len(str(row['Company'])) > 40 else row['Company']
            print(f"{row['Ticker']:<8} {company:<40} {row['Sector']:<25} "
                  f"{int(row['Composite_Score_previous']):<10} {int(row['Composite_Score_current']):<10} "
                  f"+{int(row['Rank_Change']):<10}")
        
        if len(decliners) > 10:
            print(f"... and {len(decliners) - 10} more")
        print()
    else:
        print("✓ No significant decliners detected\n")
    
    # New top 50 entries
    if len(new_top) > 0:
        print(f"⭐ NEW TOP 50 ENTRIES ({len(new_top)} stocks)")
        print("-" * 140)
        print(f"{'Ticker':<8} {'Company':<40} {'Sector':<25} {'New Rank':<10} {'Previous Rank':<15} {'Improvement':<12}")
        print("-" * 140)
        
        for _, row in new_top.iterrows():
            company = str(row['Company'])[:37] + "..." if len(str(row['Company'])) > 40 else row['Company']
            prev_rank = f"{int(row['Previous_Rank'])}" if pd.notna(row['Previous_Rank']) else "New"
            improvement = f"+{int(row['Rank_Improvement'])}" if pd.notna(row['Rank_Improvement']) else "N/A"
            print(f"{row['Ticker']:<8} {company:<40} {row['Sector']:<25} "
                  f"{int(row['Composite_Score']):<10} {prev_rank:<15} {improvement:<12}")
        print()
    else:
        print("✓ No new entries to top 50\n")


def save_alerts(upgrades: pd.DataFrame, improvers: pd.DataFrame, 
                decliners: pd.DataFrame, new_top: pd.DataFrame, filename: str) -> None:
    """
    Save alerts to Excel file
    
    Args:
        upgrades: Grade upgrades
        improvers: Significant improvers
        decliners: Significant decliners
        new_top: New top 50 entries
        filename: Output filename
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            'Alert Type': [
                'Grade Upgrades to A/A+',
                'Significant Improvers (+50 ranks)',
                'Significant Decliners (-50 ranks)',
                'New Top 50 Entries'
            ],
            'Count': [
                len(upgrades),
                len(improvers),
                len(decliners),
                len(new_top)
            ],
            'Generated': [
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Individual alert sheets
        if len(upgrades) > 0:
            upgrades_output = upgrades[[
                'Ticker', 'Company', 'Sector', 'Investment_Grade_previous', 
                'Investment_Grade_current', 'Composite_Score_previous', 
                'Composite_Score_current', 'Rank_Change'
            ]].copy()
            upgrades_output.columns = [
                'Ticker', 'Company', 'Sector', 'Previous_Grade', 
                'Current_Grade', 'Previous_Rank', 'Current_Rank', 'Rank_Change'
            ]
            upgrades_output.to_excel(writer, sheet_name='Grade Upgrades', index=False)
        
        if len(improvers) > 0:
            improvers_output = improvers[[
                'Ticker', 'Company', 'Sector', 'Composite_Score_previous',
                'Composite_Score_current', 'Rank_Change', 'Investment_Grade_current'
            ]].copy()
            improvers_output.columns = [
                'Ticker', 'Company', 'Sector', 'Previous_Rank',
                'Current_Rank', 'Rank_Change', 'Current_Grade'
            ]
            improvers_output.to_excel(writer, sheet_name='Significant Improvers', index=False)
        
        if len(decliners) > 0:
            decliners_output = decliners[[
                'Ticker', 'Company', 'Sector', 'Composite_Score_previous',
                'Composite_Score_current', 'Rank_Change', 'Investment_Grade_current'
            ]].copy()
            decliners_output.columns = [
                'Ticker', 'Company', 'Sector', 'Previous_Rank',
                'Current_Rank', 'Rank_Change', 'Current_Grade'
            ]
            decliners_output.to_excel(writer, sheet_name='Significant Decliners', index=False)
        
        if len(new_top) > 0:
            new_top_output = new_top[[
                'Ticker', 'Company', 'Sector', 'Composite_Score',
                'Previous_Rank', 'Rank_Improvement', 'Investment_Grade'
            ]].copy()
            new_top_output.columns = [
                'Ticker', 'Company', 'Sector', 'Current_Rank',
                'Previous_Rank', 'Rank_Improvement', 'Current_Grade'
            ]
            new_top_output.to_excel(writer, sheet_name='New Top 50', index=False)
    
    print(f"[SUCCESS] Alerts saved to: {filename}")


def main():
    """Main execution function"""
    print("="*140)
    print("INVESTMENT ALERT SYSTEM")
    print("="*140)
    print("\nMonitoring ranking changes and identifying significant movements\n")
    
    # Load rankings
    current_df = load_current_rankings()
    previous_df = load_previous_rankings()
    
    if previous_df is None:
        print("\n" + "="*140)
        print("FIRST RUN - NO ALERTS")
        print("="*140)
        print("\nNo previous rankings available for comparison.")
        print("Run this tool again after the next ranking update to see alerts.")
        print("\n" + "="*140)
        return
    
    # Detect changes
    print("\nAnalyzing ranking changes...\n")
    
    upgrades = detect_grade_upgrades(current_df, previous_df)
    improvers, decliners = detect_significant_movers(current_df, previous_df, threshold=50)
    new_top = detect_new_top_stocks(current_df, previous_df, top_n=50)
    
    # Generate report
    generate_alert_report(upgrades, improvers, decliners, new_top)
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'investment_alerts_{timestamp}.xlsx'
    save_alerts(upgrades, improvers, decliners, new_top, filename)
    
    print("="*140)
    print("ALERT ANALYSIS COMPLETE")
    print("="*140)
    print(f"\nTotal alerts detected: {len(upgrades) + len(improvers) + len(decliners) + len(new_top)}")
    print(f"  - Grade upgrades to A/A+: {len(upgrades)}")
    print(f"  - Significant improvers: {len(improvers)}")
    print(f"  - Significant decliners: {len(decliners)}")
    print(f"  - New top 50 entries: {len(new_top)}")
    print(f"\nDetailed alerts saved to: {filename}")
    print("\n" + "="*140)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution cancelled by user.")
        sys.exit(1)
