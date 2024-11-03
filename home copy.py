import streamlit as st
import pandas as pd
import yfinance as yf

def render_home(secteur, sectors):
    def get_financial_data(ticker):
        stock = yf.Ticker(ticker)
        info = stock.info
        one_month_return = ((info['currentPrice'] / info['twoHundredDayAverage']) - 1) * 100 if 'currentPrice' in info and 'twoHundredDayAverage' in info else None
        six_month_return = ((info['currentPrice'] / info['fiftyDayAverage']) - 1) * 100 if 'currentPrice' in info and 'fiftyDayAverage' in info else None
        one_year_return = ((info['currentPrice'] / info['regularMarketPreviousClose']) - 1) * 100 if 'currentPrice' in info and 'regularMarketPreviousClose' in info else None
        market_cap = info.get('marketCap', None)
        return one_month_return, six_month_return, one_year_return, market_cap

    st.title("Investment Analysis Dashboard")

    tickers = sectors[secteur]
    data = pd.DataFrame({'Ticker': tickers})
    data[['1-Month Return', '6-Month Return', '1-Year Return', 'Market Cap (CAD)']] = data['Ticker'].apply(lambda x: pd.Series(get_financial_data(x)))

    st.header(secteur)
    for index, row in data.iterrows():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**{row['Ticker']}**")
        with col2:
            arrow_1m = '⬆️' if row['1-Month Return'] and row['1-Month Return'] > 0 else '⬇️'
            color_1m = 'green' if row['1-Month Return'] and row['1-Month Return'] > 0 else 'red'
            st.markdown(f"<p style='color:{color_1m};'>{arrow_1m} 1-Month: {row['1-Month Return']:.2f}%</p>", unsafe_allow_html=True)
        with col3:
            arrow_6m = '⬆️' if row['6-Month Return'] and row['6-Month Return'] > 0 else '⬇️'
            color_6m = 'green' if row['6-Month Return'] and row['6-Month Return'] > 0 else 'red'
            st.markdown(f"<p style='color:{color_6m};'>{arrow_6m} 6-Month: {row['6-Month Return']:.2f}%</p>", unsafe_allow_html=True)
        with col4:
            arrow_1y = '⬆️' if row['1-Year Return'] and row['1-Year Return'] > 0 else '⬇️'
            color_1y = 'green' if row['1-Year Return'] and row['1-Year Return'] > 0 else 'red'
            st.markdown(f"<p style='color:{color_1y};'>{arrow_1y} 1-Year: {row['1-Year Return']:.2f}%</p>", unsafe_allow_html=True)
        st.write(f"Market Cap: {'CAD ' + str(row['Market Cap (CAD)'] / 1e9) + 'B' if row['Market Cap (CAD)'] else 'N/A'}")
    
    st.caption("Data sourced from Yahoo Finance.")