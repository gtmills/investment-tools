#!/usr/bin/env python3
"""
Free Cash Flow Analyzer
Analyzes stocks based on Free Cash Flow yield and quality metrics
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


def fetch_fcf_data(tickers: list) -> dict:
    """
    Fetch Free Cash Flow data for given tickers
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        Dictionary with FCF data per ticker
    """
    fcf_data = {}
    total = len(tickers)
    
    print(f"\nFetching Free Cash Flow data for {total} stocks...")
    
    for idx, ticker in enumerate(tickers, 1):
        try:
            stock = yf.Ticker(ticker)
            
            # Get cash flow statement
            cash_flow = stock.cashflow
            
            if cash_flow is not None and not cash_flow.empty:
                # Get Free Cash Flow (Operating Cash Flow - Capital Expenditures)
                if 'Free Cash Flow' in cash_flow.index:
                    fcf_values = cash_flow.loc['Free Cash Flow']
                elif 'Operating Cash Flow' in cash_flow.index and 'Capital Expenditure' in cash_flow.index:
                    ocf = cash_flow.loc['Operating Cash Flow']
                    capex = cash_flow.loc['Capital Expenditure']
                    fcf_values = ocf + capex  # capex is negative
                else:
                    fcf_values = None
                
                if fcf_values is not None and len(fcf_values) > 0:
                    # Get most recent FCF
                    latest_fcf = fcf_values.iloc[0] if not pd.isna(fcf_values.iloc[0]) else None
                    
                    # Calculate FCF growth if we have multiple years
                    fcf_growth = None
                    if len(fcf_values) >= 2:
                        recent = fcf_values.iloc[0]
                        older = fcf_values.iloc[1]
                        if not pd.isna(recent) and not pd.isna(older) and older != 0:
                            fcf_growth = (recent - older) / abs(older)
                    
                    fcf_data[ticker] = {
                        'Latest_FCF': latest_fcf,
                        'FCF_Growth': fcf_growth,
                        'FCF_History': fcf_values.tolist()[:5]  # Last 5 years
                    }
            
            # Progress indicator
            if idx % 50 == 0:
                print(f"Progress: {idx}/{total} stocks processed")
            
            # Small delay to avoid rate limiting
            time.sleep(0.15)
            
        except Exception as e:
            print(f"Error fetching FCF data for {ticker}: {e}")
            fcf_data[ticker] = {
                'Latest_FCF': None,
                'FCF_Growth': None,
                'FCF_History': []
            }
    
    return fcf_data


def calculate_fcf_metrics(df: pd.DataFrame, fcf_data: dict) -> pd.DataFrame:
    """
    Calculate FCF-based metrics and rankings
    
    Args:
        df: DataFrame with stock data
        fcf_data: Dictionary with FCF data
        
    Returns:
        DataFrame with FCF rankings
    """
    # Create a copy
    fcf_df = df.copy()
    
    # Add FCF data to dataframe
    fcf_df['Latest_FCF'] = fcf_df['Ticker'].map(lambda x: fcf_data.get(x, {}).get('Latest_FCF'))
    fcf_df['FCF_Growth'] = fcf_df['Ticker'].map(lambda x: fcf_data.get(x, {}).get('FCF_Growth'))
    
    # Calculate FCF Yield = FCF / Market Cap
    fcf_df['FCF_Yield'] = fcf_df.apply(
        lambda row: row['Latest_FCF'] / row['Market Cap'] if pd.notna(row['Latest_FCF']) and pd.notna(row['Market Cap']) and row['Market Cap'] > 0 else None,
        axis=1
    )
    
    # Filter stocks with valid FCF Yield
    valid_stocks = fcf_df['FCF_Yield'].notna()
    fcf_df = fcf_df[valid_stocks].copy()
    
    # Filter out negative FCF yields (companies burning cash)
    fcf_df = fcf_df[fcf_df['FCF_Yield'] > 0].copy()
    
    print(f"\nStocks with positive Free Cash Flow: {len(fcf_df)}")
    
    if len(fcf_df) == 0:
        print("No stocks have positive FCF data.")
        return pd.DataFrame()
    
    # Rank by FCF Yield (higher is better)
    fcf_df['FCF_Yield_Rank'] = fcf_df['FCF_Yield'].rank(method='min', ascending=False)
    
    # Rank by FCF Growth (higher is better) - only for stocks with growth data
    fcf_with_growth = fcf_df['FCF_Growth'].notna()
    if fcf_with_growth.sum() > 0:
        fcf_df.loc[fcf_with_growth, 'FCF_Growth_Rank'] = fcf_df.loc[fcf_with_growth, 'FCF_Growth'].rank(method='min', ascending=False)
    
    # Calculate composite FCF Score (lower is better)
    # For stocks with growth data, average both ranks
    # For stocks without growth data, use only yield rank
    fcf_df['FCF_Score'] = fcf_df.apply(
        lambda row: (row['FCF_Yield_Rank'] + row['FCF_Growth_Rank']) / 2 if pd.notna(row.get('FCF_Growth_Rank')) else row['FCF_Yield_Rank'],
        axis=1
    )
    
    # Sort by FCF Score (lowest = best)
    fcf_df = fcf_df.sort_values('FCF_Score', ascending=True)
    
    # Add overall rank
    fcf_df['FCF_Rank'] = range(1, len(fcf_df) + 1)
    
    return fcf_df


def display_results(df: pd.DataFrame, top_n: int = 50):
    """
    Display FCF analysis results
    
    Args:
        df: Ranked DataFrame
        top_n: Number of top stocks to display
    """
    if len(df) == 0:
        return
    
    print(f"\n{'='*140}")
    print(f"TOP {top_n} STOCKS BY FREE CASH FLOW METRICS")
    print(f"{'='*140}")
    print(f"\nHigher FCF Yield = Better (more cash generated per dollar of market cap)")
    print(f"Lower FCF_Rank = Better overall value\n")
    
    # Select columns to display
    display_cols = [
        'FCF_Rank', 'Ticker', 'Company', 'Sector', 'Price', 'Market Cap',
        'Latest_FCF', 'FCF_Yield', 'FCF_Yield_Rank', 'FCF_Growth', 'FCF_Growth_Rank',
        'FCF_Score', 'P/E Ratio', 'Debt/Equity'
    ]
    
    # Only include columns that exist
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Display top N stocks
    top_stocks = df.head(top_n)[available_cols].copy()
    
    # Format for better readability
    pd.options.display.float_format = '{:.4f}'.format
    print(top_stocks.to_string(index=False))
    
    # Summary statistics
    print(f"\n{'='*140}")
    print("SUMMARY STATISTICS")
    print(f"{'='*140}")
    print(f"Total stocks ranked: {len(df)}")
    print(f"\nTop Stock: {df.iloc[0]['Ticker']} - {df.iloc[0]['Company']}")
    print(f"  FCF Yield: {df.iloc[0]['FCF_Yield']:.4f} ({df.iloc[0]['FCF_Yield']:.2%})")
    print(f"  FCF Yield Rank: {int(df.iloc[0]['FCF_Yield_Rank'])}")
    if pd.notna(df.iloc[0].get('FCF_Growth')):
        print(f"  FCF Growth: {df.iloc[0]['FCF_Growth']:.2%}")
        print(f"  FCF Growth Rank: {int(df.iloc[0]['FCF_Growth_Rank'])}")
    print(f"  FCF Score: {df.iloc[0]['FCF_Score']:.2f}")
    print(f"  Sector: {df.iloc[0]['Sector']}")
    
    # Additional stats
    print(f"\nAverage FCF Yield: {df['FCF_Yield'].mean():.2%}")
    print(f"Median FCF Yield: {df['FCF_Yield'].median():.2%}")
    if df['FCF_Growth'].notna().sum() > 0:
        print(f"Average FCF Growth: {df['FCF_Growth'].mean():.2%}")
    print(f"{'='*140}")


def save_results(df: pd.DataFrame, filename: str = 'fcf_analysis.xlsx'):
    """
    Save FCF analysis results to Excel file with standardized ranking format
    
    Args:
        df: Ranked DataFrame
        filename: Output filename
    """
    if len(df) == 0:
        return
    
    try:
        # Create standardized ranking output (Ticker and Rank only for aggregation)
        ranking_output = df[['Ticker', 'FCF_Rank']].copy()
        ranking_output.columns = ['Ticker', 'FCF_Rank']
        
        # Select columns for detailed output
        output_cols = [
            'FCF_Rank', 'Ticker', 'Company', 'Sector', 'Industry', 'Price', 'Market Cap',
            'Latest_FCF', 'FCF_Yield', 'FCF_Yield_Rank', 'FCF_Growth', 'FCF_Growth_Rank', 'FCF_Score',
            'P/E Ratio', 'Forward P/E', 'PEG Ratio', 'Price/Book', 'ROE', 'ROA',
            'Profit Margin', 'Operating Margin', 'Debt/Equity', 'Current Ratio',
            'Dividend Yield', 'Beta'
        ]
        
        # Only include columns that exist
        available_cols = [col for col in output_cols if col in df.columns]
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Sheet 1: Standardized ranking for aggregation
            ranking_output.to_excel(writer, sheet_name='Rankings', index=False)
            
            # Sheet 2: Full ranked list with all details
            df[available_cols].to_excel(writer, sheet_name='Detailed Rankings', index=False)
            
            # Sheet 3: Top 50
            df.head(50)[available_cols].to_excel(writer, sheet_name='Top 50 Stocks', index=False)
            
            # Sheet 4: Methodology
            methodology = pd.DataFrame({
                'Free Cash Flow Analysis Methodology': [
                    'Free Cash Flow (FCF) is the cash a company generates after accounting for capital expenditures.',
                    'It represents cash available for dividends, buybacks, debt reduction, or growth investments.',
                    '',
                    'KEY METRICS:',
                    '',
                    '1. FREE CASH FLOW YIELD (Higher is Better)',
                    '   - Formula: FCF / Market Capitalization',
                    '   - Measures how much cash the company generates per dollar of market value',
                    '   - Higher yield = more cash generation relative to price',
                    '   - Typical good value: > 5%',
                    '',
                    '2. FCF GROWTH (Higher is Better)',
                    '   - Year-over-year growth in Free Cash Flow',
                    '   - Positive growth indicates improving cash generation',
                    '   - Consistent growth is a sign of business quality',
                    '',
                    '3. FCF vs NET INCOME',
                    '   - FCF > Net Income = High quality earnings (cash-backed)',
                    '   - FCF < Net Income = Lower quality (accrual-based)',
                    '',
                    'RANKING PROCESS:',
                    '- Rank all stocks by FCF Yield (1 = highest yield)',
                    '- Rank all stocks by FCF Growth (1 = highest growth)',
                    '- FCF Score = Average of both ranks (or just yield if no growth data)',
                    '- Lower FCF Score = Better investment opportunity',
                    '',
                    'WHY FCF MATTERS:',
                    '- Cash is harder to manipulate than earnings',
                    '- Shows true economic profitability',
                    '- Indicates ability to return cash to shareholders',
                    '- Essential for dividend sustainability',
                    '- Better predictor of long-term value than P/E',
                    '',
                    'INTERPRETATION:',
                    '- High FCF Yield + High Growth = Excellent opportunity',
                    '- High FCF Yield + Low Growth = Value play',
                    '- Low FCF Yield + High Growth = Growth stock (expensive)',
                    '- Negative FCF = Cash burn (avoid for value investing)',
                    '',
                    'IMPORTANT NOTES:',
                    '- Only includes stocks with positive FCF',
                    '- Capital-intensive businesses naturally have lower FCF',
                    '- Compare FCF yield to industry peers',
                    '- Always verify data with company filings',
                    '- This is not investment advice',
                ]
            })
            methodology.to_excel(writer, sheet_name='Methodology', index=False)
        
        print(f"\n{'='*140}")
        print(f"Results saved to: {filename}")
        print(f"  - Sheet 1: Rankings (standardized format for aggregation)")
        print(f"  - Sheet 2: Detailed Rankings (all {len(df)} stocks with full data)")
        print(f"  - Sheet 3: Top 50 Stocks")
        print(f"  - Sheet 4: Methodology")
        print(f"{'='*140}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main execution function"""
    print("Free Cash Flow Analyzer")
    print("="*140)
    print("Analyzing stocks based on Free Cash Flow generation...")
    print("="*140)
    
    # Load data
    df = load_stock_data()
    
    # Get list of tickers
    tickers = df['Ticker'].tolist()
    
    # Fetch FCF data
    fcf_data = fetch_fcf_data(tickers)
    
    # Calculate FCF metrics and rankings
    ranked_df = calculate_fcf_metrics(df, fcf_data)
    
    if len(ranked_df) == 0:
        print("Unable to rank stocks. Exiting.")
        return
    
    # Display results
    display_results(ranked_df, top_n=50)
    
    # Save results
    save_results(ranked_df)


if __name__ == "__main__":
    main()

# Made with Bob
