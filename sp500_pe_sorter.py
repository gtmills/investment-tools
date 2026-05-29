#!/usr/bin/env python3
"""
S&P 500 Stock P/E Ratio Sorter
Fetches S&P 500 stocks and sorts them by P/E ratio (lowest to highest)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from typing import List, Dict
import time


def get_sp500_tickers() -> List[str]:
    """
    Scrape S&P 500 ticker symbols from Wikipedia
    
    Returns:
        List of ticker symbols
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        
        tickers = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if cols:
                ticker = cols[0].text.strip()
                tickers.append(ticker)
        
        print(f"Found {len(tickers)} S&P 500 stocks")
        return tickers
    
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        return []


def get_stock_pe_data(tickers: List[str]) -> List[Dict]:
    """
    Fetch P/E ratio data for given tickers using yfinance
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        List of dictionaries containing stock data
    """
    stock_data = []
    total = len(tickers)
    
    print(f"\nFetching P/E data for {total} stocks...")
    
    for idx, ticker in enumerate(tickers, 1):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get P/E ratio (trailing P/E)
            pe_ratio = info.get('trailingPE', None)
            
            # Get additional useful info
            company_name = info.get('longName', ticker)
            current_price = info.get('currentPrice', info.get('regularMarketPrice', None))
            
            stock_data.append({
                'Ticker': ticker,
                'Company': company_name,
                'Price': current_price,
                'P/E Ratio': pe_ratio
            })
            
            # Progress indicator
            if idx % 50 == 0:
                print(f"Progress: {idx}/{total} stocks processed")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            stock_data.append({
                'Ticker': ticker,
                'Company': 'N/A',
                'Price': None,
                'P/E Ratio': None
            })
    
    return stock_data


def sort_and_display_stocks(stock_data: List[Dict]) -> pd.DataFrame:
    """
    Sort stocks by P/E ratio and display results
    
    Args:
        stock_data: List of stock data dictionaries
        
    Returns:
        Sorted DataFrame
    """
    # Create DataFrame
    df = pd.DataFrame(stock_data)
    
    # Filter out stocks without P/E data
    df_with_pe = df[df['P/E Ratio'].notna()].copy()
    df_without_pe = df[df['P/E Ratio'].isna()].copy()
    
    # Sort by P/E ratio (lowest to highest)
    df_with_pe = df_with_pe.sort_values('P/E Ratio', ascending=True)
    
    print(f"\n{'='*80}")
    print(f"S&P 500 STOCKS SORTED BY P/E RATIO (LOWEST TO HIGHEST)")
    print(f"{'='*80}")
    print(f"\nStocks with P/E data: {len(df_with_pe)}")
    print(f"Stocks without P/E data: {len(df_without_pe)}")
    print(f"\n{'='*80}\n")
    
    # Display stocks with P/E ratios
    print(df_with_pe.to_string(index=False))
    
    # Optionally show stocks without P/E data
    if len(df_without_pe) > 0:
        print(f"\n{'='*80}")
        print(f"STOCKS WITHOUT P/E DATA ({len(df_without_pe)} stocks)")
        print(f"{'='*80}\n")
        print(df_without_pe[['Ticker', 'Company']].to_string(index=False))
    
    return df_with_pe


def save_to_csv(df: pd.DataFrame, filename: str = 'sp500_pe_sorted.csv'):
    """
    Save sorted data to CSV file
    
    Args:
        df: DataFrame to save
        filename: Output filename
    """
    try:
        df.to_csv(filename, index=False)
        print(f"\n{'='*80}")
        print(f"Data saved to: {filename}")
        print(f"{'='*80}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def main():
    """Main execution function"""
    print("S&P 500 P/E Ratio Analyzer")
    print("="*80)
    
    # Step 1: Get S&P 500 tickers
    tickers = get_sp500_tickers()
    
    if not tickers:
        print("Failed to fetch S&P 500 tickers. Exiting.")
        return
    
    # Step 2: Fetch P/E data for all stocks
    stock_data = get_stock_pe_data(tickers)
    
    # Step 3: Sort and display results
    sorted_df = sort_and_display_stocks(stock_data)
    
    # Step 4: Save to CSV
    save_to_csv(sorted_df)
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}")
    print(f"Lowest P/E Ratio: {sorted_df['P/E Ratio'].min():.2f} ({sorted_df.iloc[0]['Ticker']})")
    print(f"Highest P/E Ratio: {sorted_df['P/E Ratio'].max():.2f} ({sorted_df.iloc[-1]['Ticker']})")
    print(f"Average P/E Ratio: {sorted_df['P/E Ratio'].mean():.2f}")
    print(f"Median P/E Ratio: {sorted_df['P/E Ratio'].median():.2f}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()