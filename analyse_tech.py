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

def render_analyse_tech(tickers, periode):
    st.title('Analyse Technique des Actions')

    if len(tickers) == 0:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    # Définir les dates de début et de fin en fonction de la période choisie
    end_date = pd.to_datetime('today')
    start_date = pd.to_datetime('today') - pd.DateOffset(
        months=int(periode[:-1]) * 12 if 'y' in periode else int(periode[:-2]) * 30 if 'mo' in periode else 0
    )

    # Sélection du type de graphique
    chart_type = st.selectbox('Sélectionnez le type de graphique à afficher :', ['RSI', 'MACD', 'OBV'])

    # Récupérer et afficher les données pour chaque entreprise sélectionnée
    for ticker in tickers:
        st.subheader(f'Analyse pour {ticker}')
        data = yf.download(ticker, start=start_date, end=end_date)

        if not data.empty:
            # Calcul des indicateurs
            data['RSI'] = calculate_rsi(data)
            data['MACD'], data['Signal_Line'] = calculate_macd(data)
            data['OBV'] = calculate_obv(data)
            data['Rolling Mean'], data['Upper Band'], data['Lower Band'] = calculate_bollinger_bands(data)

            # Afficher le graphique sélectionné
            if chart_type == 'RSI':
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
                fig_rsi.add_hline(y=30, line=dict(color='red', dash='dash'), annotation_text='Survendu', annotation_position='bottom right')
                fig_rsi.add_hline(y=70, line=dict(color='green', dash='dash'), annotation_text='Suracheté', annotation_position='top right')
                fig_rsi.update_layout(title=f'RSI pour {ticker}', xaxis_title='Date', yaxis_title='RSI', height=400, width=600)
                st.plotly_chart(fig_rsi)

            elif chart_type == 'MACD':
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
                fig_macd.add_trace(go.Scatter(x=data.index, y=data['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='orange')))
                fig_macd.update_layout(title=f'MACD pour {ticker}', xaxis_title='Date', yaxis_title='MACD', height=400, width=600)
                st.plotly_chart(fig_macd)

            elif chart_type == 'OBV':
                fig_obv = go.Figure()
                fig_obv.add_trace(go.Scatter(x=data.index, y=data['OBV'], mode='lines', name='OBV', line=dict(color='purple')))
                fig_obv.update_layout(title=f'OBV pour {ticker}', xaxis_title='Date', yaxis_title='OBV', height=400, width=600)
                st.plotly_chart(fig_obv)

        else:
            st.error(f'Aucune donnée trouvée pour {ticker}.')