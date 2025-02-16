import panel as pn
import pandas as pd
import yfinance as yf
import datetime
import hvplot.pandas 

pn.extension()

# setting the time range   
start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2024, 1, 1)

# for interactive
ticker_input = pn.widgets.TextInput(name="Stock Ticker", value="AAPL", placeholder="Enter stock symbol")
date_picker = pn.widgets.DateRangeSlider(name="Date Range", start=start_date, end=end_date, value=(start_date, end_date))
update_button = pn.widgets.Button(name="Update Data", button_type="primary")

# input range
stock_price_plot = pn.pane.HoloViews()
moving_avg_plot = pn.pane.HoloViews()
momentum_plot = pn.pane.HoloViews()

class StockDataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)

    def get_historical_data(self, start, end):
        """ getting the historical stock data """
        return self.stock.history(period="1y", start=start, end=end)

    def get_fundamental_data(self):
        """ get the tickers foundemntals """
        data = {
            "Sector": self.stock.info.get("sector", "N/A"),
            "Market Cap": self.stock.info.get("marketCap", "N/A"),
            "P/E Ratio": self.stock.info.get("trailingPE", "N/A"),
            "ROE": self.stock.info.get("returnOnEquity", "N/A"),
            "Dividend Yield": self.stock.info.get("dividendYield", "N/A")
        }
        return pd.DataFrame(data.items(), columns=["Metric", "Value"])

    def get_technical_indicators(self, df):
        """ Calculating moving average and momentum, I'll design strategy for improving the performance """
        df["MA50"] = df["Close"].rolling(window=50).mean()
        
        df["MA200"] = df["Close"].rolling(window=200).mean()
        df["Momentum"] = (df["Close"] / df["Close"].shift(20)) - 1  # here use the 20 days factor
        return df.dropna()

# visualization
class DashboardPlots:
    @staticmethod
    def plot_stock_price(df):
        """ price trend """
        return df.hvplot.line(y="Close", title="Stock Price")

    @staticmethod
    def plot_moving_averages(df):
        """ moving average """
        return df.hvplot.line(y=["Close", "MA50", "MA200"], title="Moving Averages")

    @staticmethod
    def plot_momentum(df):
        """ momentum factor trend """
        return df.hvplot.line(y="Momentum", title="Momentum Factor")

# call back function -- interactive
def update_dashboard(event):
    ticker = ticker_input.value
    start_date, end_date = date_picker.value  # user choose the data range
    stock_fetcher = StockDataFetcher(ticker)

    # get the dataset
    stock_data = stock_fetcher.get_historical_data(start=start_date, end=end_date)
    stock_data = stock_fetcher.get_technical_indicators(stock_data)

    # renew the data visualization 
    stock_price_plot.object = DashboardPlots.plot_stock_price(stock_data)
    moving_avg_plot.object = DashboardPlots.plot_moving_averages(stock_data)
    momentum_plot.object = DashboardPlots.plot_momentum(stock_data)


# update the event
update_button.on_click(update_dashboard)

# layout
dashboard = pn.Column(
    pn.Row(ticker_input, date_picker, update_button),
    pn.Row(stock_price_plot, moving_avg_plot),
    pn.Row(momentum_plot)
)

# initiate Dashboard
dashboard.show()
