# S&P 500 P/E Ratio Sorter

A Python script that fetches all S&P 500 stocks and sorts them by their P/E (Price-to-Earnings) ratio from lowest to highest.

## Features

- Automatically fetches the current list of S&P 500 companies from Wikipedia
- Retrieves real-time P/E ratio data using Yahoo Finance API
- Sorts stocks by P/E ratio (lowest to highest)
- Displays company name, ticker, current price, and P/E ratio
- Exports results to CSV file
- Shows summary statistics (min, max, average, median P/E ratios)

## Requirements

- Python 3.7 or higher
- Internet connection

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install requests beautifulsoup4 pandas yfinance lxml
```

## Usage

Run the script:

```bash
python sp500_pe_sorter.py
```

The script will:
1. Fetch the list of S&P 500 companies (~500 stocks)
2. Retrieve P/E ratio data for each stock (this may take a few minutes)
3. Display the sorted results in the terminal
4. Save the results to `sp500_pe_sorted.csv`

## Output

The script provides:

- **Console output**: Formatted table showing all stocks sorted by P/E ratio
- **CSV file**: `sp500_pe_sorted.csv` containing the sorted data
- **Summary statistics**: Min, max, average, and median P/E ratios

### Sample Output

```
================================================================================
S&P 500 STOCKS SORTED BY P/E RATIO (LOWEST TO HIGHEST)
================================================================================

Stocks with P/E data: 485
Stocks without P/E data: 15

================================================================================

Ticker  Company                          Price    P/E Ratio
------  -------------------------------  -------  ----------
XYZ     Example Corp                     45.23    5.67
ABC     Another Company                  123.45   8.92
...
```

## Notes

- Some stocks may not have P/E ratio data (e.g., companies with negative earnings)
- The script includes a small delay between API calls to avoid rate limiting
- P/E ratios are trailing P/E (based on last 12 months of earnings)
- Data is fetched in real-time and reflects current market conditions

## Troubleshooting

If you encounter rate limiting issues:
- Increase the `time.sleep()` value in the script
- Run the script during off-peak hours

If Wikipedia structure changes:
- The script may need updates to the web scraping logic

## License

This script is provided as-is for educational and informational purposes.