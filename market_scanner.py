
import time

import yfinance as yf
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import smtplib
from email.message import EmailMessage
import argparse

import os

MY_PORTFOLIO = ["AAPL", "AMZN", "EA", "GOOGL", "JNJ", "META", "MSFT", "NVDA", "PM", "UBER", "UL", "MU", "INTC", "AMD", "TSLA", "QCOM", "DIS", "VZ", "AVGO", "CSCO", "SNDK", "STX"]
SUBSCRIBER_EMAILS = ["saadehmd@gmail.com", "hmza.ehmad@gmail.com"]
SENDER_EMAIL = "saadehmd@gmail.com"

# TODO: Create Generic alert dispatcher class that can take be attached to multiple alert hooks
# and can notify for multiple alert types.
def send_email_alert(subject: str, body: str, recipient_emails: list, attachements = []):
    """
    Sends an email alert with the specified subject and body to the given email address.
    
    Parameters:
    subject (str): The subject of the email.
    body (str): The body content of the email.
    recipient_emails (list): List of recipient email addresses.
    attachements (list): List of file paths to attach to the email.
    """

    for recipient_email in recipient_emails:
        msg = EmailMessage()
        msg.set_content(body)
        for attachment in attachements:
            with open(attachment, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(attachment)
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        s.send_message(msg)
        s.quit()

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

def alert_price_drop(stocks_list = [], period = "1wk", interval = "1d", show_plot=True, total_drop_required = 0.1) -> pd.DataFrame:
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

    # TODO: Closing and opening prices from single interval can be too volatile. Consider using median or mean 
    # over 1 - 5% of the opening and closing intervals of the total input period.
    total_price_change = (closing_prices - opening_prices) / opening_prices
    alert = total_price_change[total_price_change <= -total_drop_required]

    # TODO: Plot rolling means of this change rate. Raw changes rates can be noisy. 
    alerted_stocks_last_day_data = fetch_periodic_prices(alert.index.tolist(), period="2d", interval="30m") if not alert.empty else pd.DataFrame()

    if not alert.empty:

        alert_str = f"Alert: The following stocks have dropped more than {total_drop_required*100:.2f}% over the period of {period}:\n\n{alert.to_string()}"
        print(alert_str)

        # If a stock is in alert, pull data from last 2 days.
        price_change_rates = alerted_stocks_last_day_data["Close"].pct_change().dropna()
        plt.figure(figsize=(10, 6))
        for stock in alert.index:
            if stock in price_change_rates.columns:
                plt.plot(price_change_rates.index, price_change_rates[stock], "-o", label=stock)
        #Plot red line at zero for ease of visualization
        plt.axhline(0, color="red", linestyle="--", label="Steady Price Line")
        plt.title(f"Price Change Rates for Alerted Stocks Over the Last Day")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%m, %H:00"))
        plt.gcf().autofmt_xdate()
        plt.xlabel("Time")
        plt.ylabel("Price Change Rate")
        plt.legend()
        plt.grid()
        plt.savefig("price_change_rates.png")
        if show_plot:
            plt.show()

        send_email_alert(
            subject=f"Stock Price Drop Alert: {len(alert)} stocks dropped more than {total_drop_required*100:.2f}%",
            body=alert_str,
            recipient_emails=SUBSCRIBER_EMAILS,
            attachements=["price_change_rates.png"]
        )



    else:
        print(f"No stocks have dropped more than {total_drop_required*100:.2f}% over the period of {period} with interval {interval}.") 

def run_price_drop_checks():

    plotting = False
    alert_price_drop(MY_PORTFOLIO, period="5d", interval="1d", total_drop_required=0.08, show_plot=plotting)
    alert_price_drop(MY_PORTFOLIO, period="10d", interval="1d", total_drop_required=0.08, show_plot=plotting)
    alert_price_drop(MY_PORTFOLIO, period="20d", interval="1d", total_drop_required=0.08, show_plot=plotting)
    alert_price_drop(MY_PORTFOLIO, period="1mo", interval="1d", total_drop_required=0.1, show_plot=plotting)

if __name__ == "__main__":
    # Example usage

    parser = argparse.ArgumentParser(description="Stock Price Drop Alert System")
    parser.add_argument("-pf", type=str, default="", help="Path to the file containing the Google App Password for sending email alerts.")
    parser.add_argument("--period", type=int, default=None, help="The period in hours over which to run all the alert checks")
    args = parser.parse_args()

    if not args.pf:
        print("Google App Password file not provided. Email alerts will not be sent.")
    else:
        with open(args.pf, "r") as f:
            SENDER_APP_PASSWORD = f.read().strip()

    if args.period is not None and SENDER_APP_PASSWORD is not None:

        try:
            while True:
                print(f"Running price drop checks every {args.period} hours...")
                run_price_drop_checks()
                time.sleep(args.period * 3600)
        except KeyboardInterrupt:
            print("\nPrice drop alert system stopped by user.")
        
    else:
        # Example Useage without periodic checks
        run_price_drop_checks()
        
    
    print("Terminating the price drop alert system.")
    

