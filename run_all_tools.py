#!/usr/bin/env python3
"""
Run All Investment Tools
Executes all analysis tools in sequence and generates master aggregation
"""

import subprocess
import sys
from pathlib import Path
import time


def run_tool(name: str, script_path: str, description: str) -> bool:
    """
    Run a single tool
    
    Args:
        name: Tool name
        script_path: Path to the Python script
        description: Tool description
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*140}")
    print(f"Running: {name}")
    print(f"Description: {description}")
    print(f"{'='*140}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✓ {name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {name} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ {name} failed: {e}")
        return False


def main():
    """Main execution function"""
    print("="*140)
    print("INVESTMENT TOOLS SUITE - COMPLETE ANALYSIS")
    print("="*140)
    print("\nThis will run all 9 investment analysis tools in sequence.")
    print("Total estimated time: 15-25 minutes")
    print("\nTools to run:")
    print("  1. S&P 500 Data Collector (5-10 min)")
    print("  2. Value Ranker (<1 min)")
    print("  3. Magic Formula Screener (<1 min)")
    print("  4. Free Cash Flow Analyzer (5-10 min)")
    print("  5. Financial Health Dashboard (<1 min)")
    print("  6. Graham Number Calculator (<1 min)")
    print("  7. Dividend Aristocrats Screener (5-10 min)")
    print("  8. Historical Valuation Analyzer (<1 min)")
    print("  9. Earnings Quality Analyzer (<1 min)")
    print(" 10. Master Aggregator (<1 min)")
    print("\n" + "="*140)
    
    input("\nPress Enter to start, or Ctrl+C to cancel...")
    
    start_time = time.time()
    results = {}
    
    # Define all tools in execution order
    tools = [
        {
            'name': 'S&P 500 Data Collector',
            'script': 'value-ranker/sp500_pe_sorter.py',
            'description': 'Fetches comprehensive data for all S&P 500 stocks'
        },
        {
            'name': 'Value Ranker',
            'script': 'value-ranker/value_ranker.py',
            'description': 'Ranks stocks by P/E, P/B, and PEG ratios'
        },
        {
            'name': 'Magic Formula Screener',
            'script': 'magic-formula/magic_formula_screener.py',
            'description': 'Joel Greenblatt\'s quality + value strategy'
        },
        {
            'name': 'Free Cash Flow Analyzer',
            'script': 'fcf-analyzer/fcf_analyzer.py',
            'description': 'Analyzes cash generation and quality'
        },
        {
            'name': 'Financial Health Dashboard',
            'script': 'financial-health/financial_health_dashboard.py',
            'description': 'Altman Z-Score and Piotroski F-Score analysis'
        },
        {
            'name': 'Graham Number Calculator',
            'script': 'graham-calculator/graham_calculator.py',
            'description': 'Benjamin Graham\'s intrinsic value formula'
        },
        {
            'name': 'Dividend Aristocrats Screener',
            'script': 'dividend-aristocrats/dividend_aristocrats.py',
            'description': 'Dividend quality, growth, and safety analysis'
        },
        {
            'name': 'Historical Valuation Analyzer',
            'script': 'historical-valuation/historical_valuation.py',
            'description': 'Sector-relative valuation analysis'
        },
        {
            'name': 'Earnings Quality Analyzer',
            'script': 'earnings-quality/earnings_quality.py',
            'description': 'Profitability and earnings quality metrics'
        },
        {
            'name': 'Master Aggregator',
            'script': 'master-aggregator/master_aggregator.py',
            'description': 'Combines all rankings into composite scores'
        }
    ]
    
    # Run each tool
    for tool in tools:
        success = run_tool(tool['name'], tool['script'], tool['description'])
        results[tool['name']] = success
        
        if not success and tool['name'] == 'S&P 500 Data Collector':
            print("\n✗ Data collection failed. Cannot continue.")
            sys.exit(1)
        
        # Small delay between tools
        time.sleep(1)
    
    # Summary
    elapsed_time = time.time() - start_time
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    print(f"\n{'='*140}")
    print("EXECUTION SUMMARY")
    print(f"{'='*140}")
    print(f"Total time: {elapsed_time/60:.1f} minutes")
    print(f"Successful: {successful}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print(f"\nResults by tool:")
    for name, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"  {status}: {name}")
    
    if failed == 0:
        print(f"\n{'='*140}")
        print("ALL TOOLS COMPLETED SUCCESSFULLY!")
        print(f"{'='*140}")
        print("\nNext steps:")
        print("1. Open 'master-aggregator/master_investment_rankings.xlsx'")
        print("2. Review the 'Top 100 Opportunities' sheet")
        print("3. Focus on Grade A and B stocks (top 40%)")
        print("4. Research individual companies before investing")
        print("5. Diversify across sectors and strategies")
    else:
        print(f"\n{'='*140}")
        print(f"COMPLETED WITH {failed} FAILURE(S)")
        print(f"{'='*140}")
        print("\nSome tools failed. Review the output above for details.")
        print("The Master Aggregator will work with available data.")
    
    print(f"\n{'='*140}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution cancelled by user.")
        sys.exit(1)

