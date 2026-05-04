
import time
from typing import List

import yfinance as yf
import pandas as pd


MY_PORTFOLIO = ["AAPL", "AMZN", "EA", "GOOGL", "JNJ", "META", "MSFT", "NVDA", "PM", "UBER", "UL"]

def fetch_periodic_prices(stocks_list = [], period = "1wk", interval = "1d"):
    """
    Fetches historical price data for a list of stocks over a specified period and interval.
    
    Parameters:
    stocks_list (list): List of stock tickers to fetch data for.
    period (str): The period over which to fetch data (e.g., '1d', '5d', '1mo').
    interval (str): The interval at which to fetch data (e.g., '1m', '5m', '1h').
    
    Returns:
    pd.DataFrame: A DataFrame containing the historical price data for the specified stocks.
    """
    if not stocks_list:
        raise ValueError("Stock list cannot be empty.")
    
    time.sleep(1)  # To avoid hitting rate limits
    return yf.download(stocks_list, period=period, interval=interval)

def alert_price_drop(stocks_list = [], period = "1wk", interval = "1d", total_drop_required = 0.1) -> pd.DataFrame:
    """
    Identifies stocks that have experienced a price drop greater than the specified threshold.
    
    Parameters:
    stock_prices (pd.DataFrame): DataFrame containing historical price data for stocks.
    total_drop_required (float): The total percentage drop required to trigger an alert.
    
    Returns:
    pd.DataFrame: A DataFrame containing stocks that have experienced a price drop greater than the threshold.
    """
    
    stock_prices = fetch_periodic_prices(stocks_list, period, interval)
    opening_prices = stock_prices.iloc[0]["Open"]
    closing_prices = stock_prices.iloc[-1]["Close"]
    total_price_change = (closing_prices - opening_prices) / opening_prices
    alert = total_price_change[total_price_change <= -total_drop_required]

    if not alert.empty:
        print(f"Alert: The following stocks have dropped more than {total_drop_required*100:.2f}% over the period of {period} with interval {interval}:")
        print(alert)
    else:
        print(f"No stocks have dropped more than {total_drop_required*100:.2f}% over the period of {period} with interval {interval}.") 



if __name__ == "__main__":
    # Example usage
    alert_price_drop(MY_PORTFOLIO, period="10d", interval="1d", total_drop_required=0.08)
    alert_price_drop(MY_PORTFOLIO, period="20d", interval="1d", total_drop_required=0.12)
    alert_price_drop(MY_PORTFOLIO, period="1mo", interval="1d", total_drop_required=0.15)

    # Todo: Create alert dispatcher that can run multiple alert threads in background and 
    # send email or SMS alerts when a stock drops more than the specified threshold
    

