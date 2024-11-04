import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal_line

def calculate_obv(data):
    obv = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()
    return obv

def calculate_bollinger_bands(data, window=20):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (2 * rolling_std)
    lower_band = rolling_mean - (2 * rolling_std)
    return rolling_mean, upper_band, lower_band

def render_analyse_tech(sectors_from_db):
    st.title('Analyse Technique des Actions')

    # Initialize session state if necessary
    if 'secteur' not in st.session_state:
        st.session_state['secteur'] = 'Agroalimentaire'
    if 'tickers' not in st.session_state:
        st.session_state['tickers'] = ['SAP.TO']
    if 'periode' not in st.session_state:
        st.session_state['periode'] = '1mo'

    secteur = st.selectbox(
        "Choisir un secteur canadien :",
        list(sectors_from_db.keys()),
        index=list(sectors_from_db.keys()).index(st.session_state['secteur']),
        on_change=lambda: st.session_state.update({'secteur': secteur})
    )

    tickers = st.multiselect(
        "Choisissez une ou plusieurs entreprises (sigles financiers)",
        sectors_from_db[secteur],
        default=[ticker for ticker in st.session_state['tickers'] if ticker in sectors_from_db[secteur]],
        on_change=lambda: st.session_state.update({'tickers': tickers})
    )

    periode = st.selectbox(
        "Sélectionnez la période",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        index=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"].index(st.session_state['periode']),
        on_change=lambda: st.session_state.update({'periode': periode})
    )

    if len(tickers) == 0:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    end_date = pd.to_datetime('today')
    start_date = end_date - pd.DateOffset(
        months=int(periode[:-1]) * 12 if 'y' in periode else int(periode[:-2]) if 'mo' in periode else 0
    )

    chart_type = st.selectbox('Sélectionnez le type de graphique à afficher :', ['RSI', 'MACD', 'OBV'])

    for i, ticker in enumerate(tickers):
        data = yf.download(ticker, start=start_date, end=end_date)

        if not data.empty:
            data['RSI'] = calculate_rsi(data)
            data['MACD'], data['Signal_Line'] = calculate_macd(data)
            data['OBV'] = calculate_obv(data)
            data['Rolling Mean'], data['Upper Band'], data['Lower Band'] = calculate_bollinger_bands(data)

            fig = go.Figure()
            if chart_type == 'RSI':
                fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
                fig.add_hline(y=30, line=dict(color='red', dash='dash'), annotation_text='Survendu', annotation_position='bottom right')
                fig.add_hline(y=70, line=dict(color='green', dash='dash'), annotation_text='Suracheté', annotation_position='top right')
                fig.update_layout(title=f'RSI pour {ticker}', xaxis_title='Date', yaxis_title='RSI')

            elif chart_type == 'MACD':
                fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=data.index, y=data['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='orange')))
                fig.update_layout(title=f'MACD pour {ticker}', xaxis_title='Date', yaxis_title='MACD')

            elif chart_type == 'OBV':
                fig.add_trace(go.Scatter(x=data.index, y=data['OBV'], mode='lines', name='OBV', line=dict(color='purple')))
                fig.update_layout(title=f'OBV pour {ticker}', xaxis_title='Date', yaxis_title='OBV')

            # Arrange graphs in two columns
            if i % 2 == 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                with col2:
                    st.plotly_chart(fig, use_container_width=True)

        else:
            st.error(f'Aucune donnée trouvée pour {ticker}.')