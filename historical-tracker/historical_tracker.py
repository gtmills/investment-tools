#!/usr/bin/env python3
"""
Historical Investment Rankings Tracker
Saves dated copies of master rankings and tracks changes over time
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import shutil


def create_historical_snapshot():
    """
    Create a dated snapshot of current master rankings
    
    Returns:
        str: Path to the saved snapshot file
    """
    # Create historical-data directory if it doesn't exist
    hist_dir = Path('historical-data')
    hist_dir.mkdir(exist_ok=True)
    
    # Get current date for filename
    date_str = datetime.now().strftime('%Y-%m-%d')
    snapshot_file = hist_dir / f'rankings_{date_str}.xlsx'
    
    # Check if master rankings file exists
    master_file = 'master_investment_rankings.xlsx'
    if not os.path.exists(master_file):
        print(f"[ERROR] Master rankings file not found: {master_file}")
        print("Please run the Master Aggregator first.")
        return None
    
    # Copy master rankings to historical snapshot
    try:
        shutil.copy2(master_file, snapshot_file)
        print(f"[SUCCESS] Created historical snapshot: {snapshot_file}")
        return str(snapshot_file)
    except Exception as e:
        print(f"[ERROR] Failed to create snapshot: {e}")
        return None


def list_historical_snapshots():
    """
    List all available historical snapshots
    
    Returns:
        list: List of snapshot filenames sorted by date
    """
    hist_dir = Path('historical-data')
    if not hist_dir.exists():
        return []
    
    snapshots = sorted(hist_dir.glob('rankings_*.xlsx'))
    return [s.name for s in snapshots]


def compare_rankings(date1: str = None, date2: str = None):
    """
    Compare rankings between two dates
    
    Args:
        date1: First date (YYYY-MM-DD) or None for oldest
        date2: Second date (YYYY-MM-DD) or None for latest
        
    Returns:
        DataFrame with comparison results
    """
    hist_dir = Path('historical-data')
    
    # Get available snapshots
    snapshots = sorted(hist_dir.glob('rankings_*.xlsx'))
    if len(snapshots) < 2:
        print("[ERROR] Need at least 2 historical snapshots to compare")
        return None
    
    # Select files to compare
    if date1 is None:
        file1 = snapshots[0]
    else:
        file1 = hist_dir / f'rankings_{date1}.xlsx'
        
    if date2 is None:
        file2 = snapshots[-1]
    else:
        file2 = hist_dir / f'rankings_{date2}.xlsx'
    
    if not file1.exists() or not file2.exists():
        print(f"[ERROR] Snapshot files not found")
        return None
    
    try:
        # Load both rankings
        df1 = pd.read_excel(file1, sheet_name='Top 100 Opportunities')
        df2 = pd.read_excel(file2, sheet_name='Top 100 Opportunities')
        
        # Extract dates from filenames
        date1_str = file1.stem.replace('rankings_', '')
        date2_str = file2.stem.replace('rankings_', '')
        
        # Merge on Ticker
        comparison = df1[['Ticker', 'Company', 'Composite_Score', 'Investment_Grade']].merge(
            df2[['Ticker', 'Composite_Score', 'Investment_Grade']],
            on='Ticker',
            how='outer',
            suffixes=(f'_{date1_str}', f'_{date2_str}')
        )
        
        # Calculate rank change
        comparison['Rank_Change'] = (
            comparison[f'Composite_Score_{date1_str}'] - 
            comparison[f'Composite_Score_{date2_str}']
        )
        
        # Identify new entries and exits
        comparison['Status'] = 'Stable'
        comparison.loc[comparison[f'Composite_Score_{date1_str}'].isna(), 'Status'] = 'New Entry'
        comparison.loc[comparison[f'Composite_Score_{date2_str}'].isna(), 'Status'] = 'Dropped Out'
        
        # Sort by latest composite score
        comparison = comparison.sort_values(f'Composite_Score_{date2_str}', ascending=True)
        
        return comparison, date1_str, date2_str
        
    except Exception as e:
        print(f"[ERROR] Failed to compare rankings: {e}")
        return None


def generate_tracking_report():
    """
    Generate a comprehensive tracking report
    """
    print("="*100)
    print("HISTORICAL INVESTMENT RANKINGS TRACKER")
    print("="*100)
    
    # List available snapshots
    snapshots = list_historical_snapshots()
    
    if len(snapshots) == 0:
        print("\nNo historical snapshots found.")
        print("Creating first snapshot...")
        create_historical_snapshot()
        print("\nRun this tool again after collecting more snapshots to see trends.")
        return
    
    print(f"\nAvailable snapshots: {len(snapshots)}")
    for snapshot in snapshots:
        print(f"  - {snapshot}")
    
    if len(snapshots) < 2:
        print("\nNeed at least 2 snapshots to compare trends.")
        print("Creating new snapshot...")
        create_historical_snapshot()
        return
    
    # Compare oldest vs newest
    print(f"\n{'='*100}")
    print("RANKING CHANGES ANALYSIS")
    print(f"{'='*100}")
    
    result = compare_rankings()
    if result is None:
        return
    
    comparison, date1, date2 = result
    
    print(f"\nComparing: {date1} vs {date2}")
    print(f"Total stocks tracked: {len(comparison)}")
    
    # Show biggest movers
    print(f"\n{'='*100}")
    print("TOP 10 BIGGEST IMPROVERS (Lower rank = better)")
    print(f"{'='*100}")
    
    improvers = comparison[comparison['Rank_Change'] > 0].nlargest(10, 'Rank_Change')
    if len(improvers) > 0:
        print(improvers[['Ticker', 'Company', 'Rank_Change', 'Status']].to_string(index=False))
    else:
        print("No improvers found")
    
    print(f"\n{'='*100}")
    print("TOP 10 BIGGEST DECLINERS")
    print(f"{'='*100}")
    
    decliners = comparison[comparison['Rank_Change'] < 0].nsmallest(10, 'Rank_Change')
    if len(decliners) > 0:
        print(decliners[['Ticker', 'Company', 'Rank_Change', 'Status']].to_string(index=False))
    else:
        print("No decliners found")
    
    # Show new entries
    new_entries = comparison[comparison['Status'] == 'New Entry']
    if len(new_entries) > 0:
        print(f"\n{'='*100}")
        print(f"NEW ENTRIES TO TOP 100: {len(new_entries)}")
        print(f"{'='*100}")
        print(new_entries[['Ticker', 'Company']].head(10).to_string(index=False))
    
    # Show dropped out
    dropped = comparison[comparison['Status'] == 'Dropped Out']
    if len(dropped) > 0:
        print(f"\n{'='*100}")
        print(f"DROPPED FROM TOP 100: {len(dropped)}")
        print(f"{'='*100}")
        print(dropped[['Ticker', 'Company']].head(10).to_string(index=False))
    
    # Save comparison report
    report_file = f'historical-data/comparison_{date1}_vs_{date2}.xlsx'
    try:
        comparison.to_excel(report_file, index=False)
        print(f"\n{'='*100}")
        print(f"Detailed comparison saved to: {report_file}")
        print(f"{'='*100}")
    except Exception as e:
        print(f"\n[ERROR] Failed to save comparison report: {e}")


def main():
    """Main execution function"""
    # Create new snapshot
    print("Creating new historical snapshot...")
    snapshot = create_historical_snapshot()
    
    if snapshot:
        print("\n")
        # Generate tracking report
        generate_tracking_report()


if __name__ == "__main__":
    main()