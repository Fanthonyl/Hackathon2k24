import streamlit as st
import talib
import yfinance as yf
import matplotlib.pyplot as plt

# Configuration de Streamlit
st.set_page_config(page_title='Analyse Technique des Indicateurs', layout='wide')
st.title('Analyse Technique des Indicateurs avec TA-Lib')

# Entrée de l'utilisateur pour sélectionner un actif
symbol = st.text_input('Entrez le symbole de l\'actif (ex: AAPL)', 'AAPL')

# Télécharger les données historiques
if symbol:
    data = yf.download(symbol, start='2023-01-01', end='2024-01-01')
    
    if not data.empty:
        # Calcul du RSI (Relative Strength Index)
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

        # Calcul du MACD (Moving Average Convergence Divergence)
        data['MACD'], data['MACD_signal'], data['MACD_hist'] = talib.MACD(
            data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

        # Calcul de l'OBV (On-Balance Volume)
        data['OBV'] = talib.OBV(data['Close'], data['Volume'])

        # Calcul des Bandes de Bollinger
        upper_band, middle_band, lower_band = talib.BBANDS(
            data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        data['Upper_Band'] = upper_band
        data['Middle_Band'] = middle_band
        data['Lower_Band'] = lower_band

        # Affichage des graphiques avec Matplotlib
        st.subheader('Graphiques des Indicateurs Techniques')
        fig, axs = plt.subplots(3, 1, figsize=(14, 10))
        
        # Graphique des prix et des bandes de Bollinger
        axs[0].plot(data['Close'], label='Prix de clôture', color='blue')
        axs[0].plot(data['Upper_Band'], label='Bande supérieure', linestyle='--', color='red')
        axs[0].plot(data['Middle_Band'], label='Moyenne mobile', linestyle='-', color='green')
        axs[0].plot(data['Lower_Band'], label='Bande inférieure', linestyle='--', color='red')
        axs[0].fill_between(data.index, data['Lower_Band'], data['Upper_Band'], color='lightgray', alpha=0.3)
        axs[0].set_title('Bandes de Bollinger et Prix de clôture')
        axs[0].legend()

        # Graphique du MACD
        axs[1].plot(data['MACD'], label='MACD', color='purple')
        axs[1].plot(data['MACD_signal'], label='Signal', color='orange')
        axs[1].bar(data.index, data['MACD_hist'], label='Histogramme MACD', color='grey', alpha=0.5)
        axs[1].set_title('MACD')
        axs[1].legend()

        # Graphique du RSI
        axs[2].plot(data['RSI'], label='RSI', color='green')
        axs[2].axhline(70, color='red', linestyle='--', label='Surachat')
        axs[2].axhline(30, color='blue', linestyle='--', label='Survente')
        axs[2].set_title('RSI (Relative Strength Index)')
        axs[2].legend()

        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.error('Données non disponibles pour le symbole spécifié. Veuillez vérifier le symbole et réessayer.')
