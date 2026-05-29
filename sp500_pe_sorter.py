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
    Fetch comprehensive stock data for given tickers using yfinance
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        List of dictionaries containing stock data
    """
    stock_data = []
    total = len(tickers)
    
    print(f"\nFetching stock data for {total} stocks...")
    
    for idx, ticker in enumerate(tickers, 1):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get comprehensive stock information
            company_name = info.get('longName', ticker)
            current_price = info.get('currentPrice', info.get('regularMarketPrice', None))
            
            # Valuation metrics
            pe_ratio = info.get('trailingPE', None)
            forward_pe = info.get('forwardPE', None)
            peg_ratio = info.get('pegRatio', None)
            price_to_book = info.get('priceToBook', None)
            price_to_sales = info.get('priceToSalesTrailing12Months', None)
            
            # Market metrics
            market_cap = info.get('marketCap', None)
            enterprise_value = info.get('enterpriseValue', None)
            
            # Profitability metrics
            profit_margin = info.get('profitMargins', None)
            operating_margin = info.get('operatingMargins', None)
            roe = info.get('returnOnEquity', None)
            roa = info.get('returnOnAssets', None)
            
            # Growth metrics
            revenue_growth = info.get('revenueGrowth', None)
            earnings_growth = info.get('earningsGrowth', None)
            
            # Dividend metrics
            dividend_yield = info.get('dividendYield', None)
            payout_ratio = info.get('payoutRatio', None)
            
            # Debt metrics
            debt_to_equity = info.get('debtToEquity', None)
            current_ratio = info.get('currentRatio', None)
            
            # Trading metrics
            beta = info.get('beta', None)
            fifty_two_week_high = info.get('fiftyTwoWeekHigh', None)
            fifty_two_week_low = info.get('fiftyTwoWeekLow', None)
            avg_volume = info.get('averageVolume', None)
            
            # Sector and Industry
            sector = info.get('sector', None)
            industry = info.get('industry', None)
            
            stock_data.append({
                'Ticker': ticker,
                'Company': company_name,
                'Sector': sector,
                'Industry': industry,
                'Price': current_price,
                'Market Cap': market_cap,
                'P/E Ratio': pe_ratio,
                'Forward P/E': forward_pe,
                'PEG Ratio': peg_ratio,
                'Price/Book': price_to_book,
                'Price/Sales': price_to_sales,
                'Dividend Yield': dividend_yield,
                'Payout Ratio': payout_ratio,
                'Profit Margin': profit_margin,
                'Operating Margin': operating_margin,
                'ROE': roe,
                'ROA': roa,
                'Revenue Growth': revenue_growth,
                'Earnings Growth': earnings_growth,
                'Debt/Equity': debt_to_equity,
                'Current Ratio': current_ratio,
                'Beta': beta,
                '52W High': fifty_two_week_high,
                '52W Low': fifty_two_week_low,
                'Avg Volume': avg_volume,
                'Enterprise Value': enterprise_value
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
                'Sector': None,
                'Industry': None,
                'Price': None,
                'Market Cap': None,
                'P/E Ratio': None,
                'Forward P/E': None,
                'PEG Ratio': None,
                'Price/Book': None,
                'Price/Sales': None,
                'Dividend Yield': None,
                'Payout Ratio': None,
                'Profit Margin': None,
                'Operating Margin': None,
                'ROE': None,
                'ROA': None,
                'Revenue Growth': None,
                'Earnings Growth': None,
                'Debt/Equity': None,
                'Current Ratio': None,
                'Beta': None,
                '52W High': None,
                '52W Low': None,
                'Avg Volume': None,
                'Enterprise Value': None
            })
    
    return stock_data


def sort_and_display_stocks(stock_data: List[Dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Sort stocks by P/E ratio and display results
    
    Args:
        stock_data: List of stock data dictionaries
        
    Returns:
        Tuple of (DataFrame with P/E data, DataFrame without P/E data)
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
    
    # Display stocks with P/E ratios (show key columns)
    display_columns = ['Ticker', 'Company', 'Sector', 'Price', 'Market Cap', 'P/E Ratio',
                      'Forward P/E', 'Dividend Yield', 'ROE', 'Debt/Equity']
    print(df_with_pe[display_columns].to_string(index=False))
    
    # Optionally show stocks without P/E data
    if len(df_without_pe) > 0:
        print(f"\n{'='*80}")
        print(f"STOCKS WITHOUT P/E DATA ({len(df_without_pe)} stocks)")
        print(f"{'='*80}\n")
        print(df_without_pe[['Ticker', 'Company']].to_string(index=False))
    
    return df_with_pe, df_without_pe


def save_to_excel(df: pd.DataFrame, df_without_pe: pd.DataFrame, filename: str = 'sp500_pe_sorted.xlsx'):
    """
    Save sorted data to Excel file with multiple sheets
    
    Args:
        df: DataFrame with P/E data to save
        df_without_pe: DataFrame without P/E data
        filename: Output filename
    """
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write stocks with P/E data to first sheet
            df.to_excel(writer, sheet_name='Stocks with PE', index=False)
            
            # Write stocks without P/E data to second sheet
            if len(df_without_pe) > 0:
                df_without_pe[['Ticker', 'Company', 'Price']].to_excel(
                    writer, sheet_name='Stocks without PE', index=False
                )
            
            # Create summary statistics sheet
            summary_data = {
                'Metric': ['Lowest P/E Ratio', 'Highest P/E Ratio', 'Average P/E Ratio', 'Median P/E Ratio',
                          'Total Stocks with P/E', 'Total Stocks without P/E'],
                'Value': [
                    f"{df['P/E Ratio'].min():.2f} ({df.iloc[0]['Ticker']})",
                    f"{df['P/E Ratio'].max():.2f} ({df.iloc[-1]['Ticker']})",
                    f"{df['P/E Ratio'].mean():.2f}",
                    f"{df['P/E Ratio'].median():.2f}",
                    len(df),
                    len(df_without_pe)
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"\n{'='*80}")
        print(f"Data saved to Excel file: {filename}")
        print(f"  - Sheet 1: Stocks with PE (sorted)")
        print(f"  - Sheet 2: Stocks without PE")
        print(f"  - Sheet 3: Summary Statistics")
        print(f"{'='*80}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


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
    sorted_df, df_without_pe = sort_and_display_stocks(stock_data)
    
    # Step 4: Save to Excel
    save_to_excel(sorted_df, df_without_pe)
    
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