#!/usr/bin/env python3
"""
Backtesting Framework
Simple backtesting tool to evaluate strategy performance
"""

import pandas as pd
import yfinance as yf
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time


def load_master_rankings() -> pd.DataFrame:
    """Load the master investment rankings"""
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


def fetch_historical_returns(tickers: list, months: int = 12) -> dict:
    """
    Fetch historical returns for a list of tickers
    
    Args:
        tickers: List of stock tickers
        months: Number of months to look back
        
    Returns:
        Dictionary mapping ticker to return percentage
    """
    print(f"\nFetching {months}-month returns for {len(tickers)} stocks...")
    
    returns = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 31)
    
    for i, ticker in enumerate(tickers):
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{len(tickers)} stocks")
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            
            if not hist.empty and len(hist) >= 2:
                start_price = hist['Close'].iloc[0]
                end_price = hist['Close'].iloc[-1]
                ret = ((end_price - start_price) / start_price) * 100
                returns[ticker] = ret
            else:
                returns[ticker] = None
                
        except Exception as e:
            returns[ticker] = None
        
        time.sleep(0.05)  # Rate limiting
    
    print(f"[SUCCESS] Fetched returns for {len([r for r in returns.values() if r is not None])} stocks")
    return returns


def backtest_strategy(df: pd.DataFrame, strategy_name: str, 
                     selection_criteria: dict, months: int = 12) -> dict:
    """
    Backtest a strategy
    
    Args:
        df: Master rankings DataFrame
        strategy_name: Name of the strategy
        selection_criteria: Dict with 'max_rank', 'min_grade', 'portfolio_size'
        months: Backtest period in months
        
    Returns:
        Dictionary with backtest results
    """
    print(f"\n{'='*140}")
    print(f"BACKTESTING: {strategy_name}")
    print(f"{'='*140}")
    
    # Select stocks based on criteria
    filtered = df.copy()
    
    if 'max_rank' in selection_criteria:
        filtered = filtered[filtered['Composite_Score'] <= selection_criteria['max_rank']]
    
    if 'min_grade' in selection_criteria:
        grade_order = {'F': 0, 'D': 1, 'C': 2, 'B': 3, 'B+': 4, 'A': 5, 'A+': 6}
        min_grade_value = grade_order.get(selection_criteria['min_grade'], 0)
        filtered = filtered[filtered['Investment_Grade'].map(grade_order) >= min_grade_value]
    
    # Get top N stocks
    portfolio_size = selection_criteria.get('portfolio_size', 20)
    portfolio = filtered.nsmallest(portfolio_size, 'Composite_Score')
    
    print(f"\nStrategy Parameters:")
    print(f"  - Max Rank: {selection_criteria.get('max_rank', 'None')}")
    print(f"  - Min Grade: {selection_criteria.get('min_grade', 'None')}")
    print(f"  - Portfolio Size: {portfolio_size}")
    print(f"  - Backtest Period: {months} months")
    
    print(f"\nSelected {len(portfolio)} stocks for portfolio")
    
    # Fetch returns
    tickers = portfolio['Ticker'].tolist()
    returns = fetch_historical_returns(tickers, months)
    
    # Calculate portfolio performance
    valid_returns = [r for r in returns.values() if r is not None]
    
    if not valid_returns:
        print("\n[ERROR] No valid returns data available")
        return None
    
    # Equal-weight portfolio return
    portfolio_return = sum(valid_returns) / len(valid_returns)
    
    # Calculate statistics
    positive_returns = len([r for r in valid_returns if r > 0])
    negative_returns = len([r for r in valid_returns if r < 0])
    
    best_stock = max(returns.items(), key=lambda x: x[1] if x[1] is not None else float('-inf'))
    worst_stock = min(returns.items(), key=lambda x: x[1] if x[1] is not None else float('inf'))
    
    results = {
        'strategy_name': strategy_name,
        'portfolio_size': len(portfolio),
        'valid_returns': len(valid_returns),
        'portfolio_return': portfolio_return,
        'positive_stocks': positive_returns,
        'negative_stocks': negative_returns,
        'win_rate': (positive_returns / len(valid_returns)) * 100,
        'best_stock': best_stock,
        'worst_stock': worst_stock,
        'returns': returns
    }
    
    return results


def display_backtest_results(results: dict) -> None:
    """Display backtest results"""
    if results is None:
        return
    
    print(f"\n{'='*140}")
    print("BACKTEST RESULTS")
    print(f"{'='*140}\n")
    
    print(f"Portfolio Performance:")
    print(f"  - Portfolio Return: {results['portfolio_return']:.2f}%")
    print(f"  - Annualized Return: {results['portfolio_return']:.2f}% (12-month period)")
    print(f"  - Win Rate: {results['win_rate']:.1f}% ({results['positive_stocks']}/{results['valid_returns']} stocks)")
    
    print(f"\nBest Performer:")
    print(f"  - {results['best_stock'][0]}: {results['best_stock'][1]:.2f}%")
    
    print(f"\nWorst Performer:")
    print(f"  - {results['worst_stock'][0]}: {results['worst_stock'][1]:.2f}%")
    
    print(f"\nPortfolio Statistics:")
    print(f"  - Total Stocks: {results['portfolio_size']}")
    print(f"  - Valid Returns: {results['valid_returns']}")
    print(f"  - Positive Returns: {results['positive_stocks']}")
    print(f"  - Negative Returns: {results['negative_stocks']}")


def save_backtest_results(all_results: list, filename: str) -> None:
    """Save backtest results to Excel"""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = []
        for result in all_results:
            if result:
                summary_data.append({
                    'Strategy': result['strategy_name'],
                    'Portfolio_Size': result['portfolio_size'],
                    'Valid_Returns': result['valid_returns'],
                    'Portfolio_Return_%': round(result['portfolio_return'], 2),
                    'Win_Rate_%': round(result['win_rate'], 1),
                    'Positive_Stocks': result['positive_stocks'],
                    'Negative_Stocks': result['negative_stocks'],
                    'Best_Stock': result['best_stock'][0],
                    'Best_Return_%': round(result['best_stock'][1], 2),
                    'Worst_Stock': result['worst_stock'][0],
                    'Worst_Return_%': round(result['worst_stock'][1], 2)
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Individual strategy sheets
        for result in all_results:
            if result:
                returns_data = []
                for ticker, ret in result['returns'].items():
                    returns_data.append({
                        'Ticker': ticker,
                        'Return_%': round(ret, 2) if ret is not None else None
                    })
                
                returns_df = pd.DataFrame(returns_data)
                returns_df = returns_df.sort_values('Return_%', ascending=False, na_position='last')
                
                sheet_name = result['strategy_name'][:31]  # Excel sheet name limit
                returns_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\n[SUCCESS] Backtest results saved to: {filename}")


def main():
    """Main execution function"""
    print("="*140)
    print("BACKTESTING FRAMEWORK")
    print("="*140)
    print("\nSimple backtesting tool to evaluate strategy performance")
    print("Tests how top-ranked stocks performed over the past 12 months\n")
    
    # Load rankings
    df = load_master_rankings()
    
    # Define strategies to backtest
    strategies = [
        {
            'name': 'Conservative (Top 50, Grade A+)',
            'criteria': {'max_rank': 50, 'min_grade': 'A+', 'portfolio_size': 20}
        },
        {
            'name': 'Balanced (Top 100, Grade A)',
            'criteria': {'max_rank': 100, 'min_grade': 'A', 'portfolio_size': 25}
        },
        {
            'name': 'Aggressive (Top 150, Grade B+)',
            'criteria': {'max_rank': 150, 'min_grade': 'B+', 'portfolio_size': 30}
        }
    ]
    
    # Run backtests
    all_results = []
    
    for strategy in strategies:
        result = backtest_strategy(df, strategy['name'], strategy['criteria'], months=12)
        if result:
            display_backtest_results(result)
            all_results.append(result)
        print()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'backtest_results_{timestamp}.xlsx'
    save_backtest_results(all_results, filename)
    
    print("\n" + "="*140)
    print("BACKTESTING COMPLETE")
    print("="*140)
    print(f"\nTested {len(all_results)} strategies over 12-month period")
    print(f"Results saved to: {filename}")
    print("\nIMPORTANT: Past performance does not guarantee future results")
    print("="*140)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution cancelled by user.")
        sys.exit(1)
