import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Binance API endpoints
BASE_URL = "https://fapi.binance.com"

# Functions to retrieve data
def get_perpetual_pairs():
    response = requests.get(f"{BASE_URL}/fapi/v1/exchangeInfo")
    symbols = response.json()['symbols']
    perp_symbols = [s['symbol'] for s in symbols if s['contractType'] == 'PERPETUAL']
    return perp_symbols

def get_funding_rate(symbol):
    url = f"{BASE_URL}/fapi/v1/fundingRate?symbol={symbol}&limit=1"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        return float(response.json()[0]['fundingRate'])
    return None

def get_open_interest(symbol):
    url = f"{BASE_URL}/futures/data/openInterestHist?symbol={symbol}&period=5m&limit=1"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        return float(response.json()[0]['sumOpenInterest'])
    return None

def get_volume(symbol):
    url = f"{BASE_URL}/fapi/v1/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        return float(response.json()['quoteVolume'])
    return None

def get_long_short_ratio(symbol):
    url = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=5m&limit=1"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        return float(response.json()[0]['longShortRatio'])
    return None

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📊 Crypto Futures Market Dashboard")
st.write("Live data for Perpetual Futures Contracts from Binance")

symbols = get_perpetual_pairs()
selected_symbols = st.multiselect("Select perpetual futures pairs:", options=symbols, default=['BTCUSDT', 'ETHUSDT'])

data = []
for symbol in selected_symbols:
    funding = get_funding_rate(symbol)
    interest = get_open_interest(symbol)
    volume = get_volume(symbol)
    lsr = get_long_short_ratio(symbol)
    data.append({
        'Symbol': symbol,
        'Funding Rate': funding,
        'Open Interest (USD)': interest,
        '24h Volume (USD)': volume,
        'Long/Short Ratio': lsr
    })

df = pd.DataFrame(data)
st.dataframe(df.sort_values(by='24h Volume (USD)', ascending=False), use_container_width=True)

# Plotting
col1, col2 = st.columns(2)
with col1:
    fig = px.bar(df, x='Symbol', y='Open Interest (USD)', title='Open Interest per Symbol')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.bar(df, x='Symbol', y='Funding Rate', title='Funding Rate per Symbol')
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.write("Data Source: Binance Futures API")
