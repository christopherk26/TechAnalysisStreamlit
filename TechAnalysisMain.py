
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(layout="wide")
st.title("Technical analysis of any stock, with MA and BB's")
st.subheader("change ticker symbol and click fetch data")
st.sidebar.header("inputs")

# Input for stock ticker and date range
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL):", "AAPL")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
today = str(date.today())
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(today))
if st.sidebar.button("Fetch Data"):
    st.session_state["stock_data"] = yf.download(ticker, start=start_date, end=end_date)
    st.success("Success in data load")
# Add input fields for X, Y, and Z variables
st.sidebar.subheader("Indicator Parameters")
x_days = st.sidebar.number_input("X-Day SMA Period:", min_value=1, max_value=200, value=20)
y_days = st.sidebar.number_input("Y-Day EMA Period:", min_value=1, max_value=200, value=20)
z_days = st.sidebar.number_input("Z-Day Bollinger Bands Period:", min_value=1, max_value=200, value=20)



if "stock_data" in st.session_state:
    data = st.session_state["stock_data"]

    # Plot candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candlestick"
        )
    ])

    # Sidebar: Select technical indicators
    st.sidebar.subheader("Technical Indicators")
    indicators = st.sidebar.multiselect(
        "Select Indicators:",
        [f"{x_days}-Day SMA",
         f"{y_days}-Day EMA",
         f"{z_days}-Day Bollinger Bands",
         "VWAP"],
        default=[f"{x_days}-Day SMA"]
    )

    # Helper function to add indicators to the chart
    def add_indicator(indicator):
        if f"{x_days}-Day SMA" in indicator:
            sma = data['Close'].rolling(window=x_days).mean()
            fig.add_trace(go.Scatter(x=data.index, y=sma, mode='lines', name=f'SMA ({x_days})'))
        elif f"{y_days}-Day EMA" in indicator:
            ema = data['Close'].ewm(span=y_days).mean()
            fig.add_trace(go.Scatter(x=data.index, y=ema, mode='lines', name=f'EMA ({y_days})'))
        elif f"{z_days}-Day Bollinger Bands" in indicator:
            sma = data['Close'].rolling(window=z_days).mean()
            std = data['Close'].rolling(window=z_days).std()
            bb_upper = sma + 2 * std
            bb_lower = sma - 2 * std
            fig.add_trace(go.Scatter(x=data.index, y=bb_upper, mode='lines', name=f'BB Upper ({z_days})'))
            fig.add_trace(go.Scatter(x=data.index, y=bb_lower, mode='lines', name=f'BB Lower ({z_days})'))
        elif indicator == "VWAP":
            data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
            fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], mode='lines', name='VWAP'))

    # Add selected indicators to the chart
    for indicator in indicators:
        add_indicator(indicator)

    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)
