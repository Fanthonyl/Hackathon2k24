import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import boto3
import json
import logging
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import uuid
from data import database

# Extraire les domaines et les entreprises correspondantes
sectors_from_db = {domaine: [entry['ticker'] for entry in database if entry['domaine'] == domaine] for domaine in set(entry['domaine'] for entry in database)}


# Setting up logging
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockAgentRuntimeWrapper:
    """Encapsulates Amazon Bedrock Agents Runtime actions."""

    def __init__(self, runtime_client):
        self.agents_runtime_client = runtime_client

    def invoke_agent(self, agent_id, agent_alias_id, session_id, prompt):
        """
        Sends a prompt for the agent to process and respond to.
        """
        try:
            response = self.agents_runtime_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=prompt,
            )

            completion = ""
            for event in response.get("completion"):
                chunk = event["chunk"]
                completion += chunk["bytes"].decode() + "\n"

            return completion

        except ClientError as e:
            logger.error(f"Couldn't invoke agent. {e}")
            raise

# Initialize Bedrock clients and the wrapper
bedrock_client = boto3.client('bedrock', region_name='us-west-2')
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
bedrock_wrapper = BedrockAgentRuntimeWrapper(bedrock_agent_runtime_client)

def get_financial_insights(tickers_list):
    session_id = str(uuid.uuid1())
    agent_id = 'ACVSW7ULXC'
    agent_alias_id = 'FGVZUPEISZ'
    
    # Prepare the prompt for Bedrock input
    input_text = (
        f"Analyze the following json: {json.dumps(tickers_list)}.\n"
        f"As you can see it contains the variations of financial indicators.\n"
        f"Please provide insights those.\n"
        f"Speak in French\n"
    )

    # Invoke the agent via the BedrockAgentRuntimeWrapper
    logger.info(f"Invoking agent with prompt:\n{input_text}")
    insights = bedrock_wrapper.invoke_agent(agent_id, agent_alias_id, session_id, input_text)

    # Log the response for debugging
    logger.info("Financial insights received:")
    logger.info(insights)
    
    return insights or 'No insights available.'

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


st.title('Analyse Technique')
st.markdown("Alexia vous aide à suivre les tendances des principaux KPIs techniques par secteur ou entreprise, pour une évaluation approfondie de la performance.")

# Initialize session state if necessary
if 'secteur' not in st.session_state:
    st.session_state['secteur'] = 'Agroalimentaire'
if 'tickers' not in st.session_state:
    st.session_state['tickers'] = ['SAP.TO','L.TO']
if 'periode' not in st.session_state:
    st.session_state['periode'] = '1y'

col1, col2 = st.columns(2)
with col1:

    secteur = st.selectbox(
        "Choisir un secteur canadien :",
        list(sectors_from_db.keys()),
        index=list(sectors_from_db.keys()).index(st.session_state['secteur']),
        on_change=lambda: st.session_state.update({'secteur': secteur})
    )

with col2:
    tickers = st.multiselect(
        "Choisissez une ou plusieurs entreprises (sigles financiers)",
        sectors_from_db[secteur],
        default=[ticker for ticker in st.session_state['tickers'] if ticker in sectors_from_db[secteur]],
        on_change=lambda: st.session_state.update({'tickers': tickers})
    )

col1, col2 = st.columns(2)
with col1:
    periode = st.selectbox(
        "Sélectionnez la période",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        index=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"].index(st.session_state['periode']),
        on_change=lambda: st.session_state.update({'periode': periode})
    )

    if len(tickers) == 0:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        st.stop()
    
end_date = pd.to_datetime('today')
start_date = end_date - pd.DateOffset(
    months=int(periode[:-1]) * 12 if 'y' in periode else int(periode[:-2]) if 'mo' in periode else 0
)

with col2:
    chart_type = st.selectbox('Sélectionnez le type de graphique à afficher :', ['RSI', 'MACD', 'OBV'])

kpi_values = []

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

        # Collect KPI values for the agent
        kpi_values.append({
            "ticker": ticker,
            "RSI": data['RSI'].iloc[-1],
            "MACD": data['MACD'].iloc[-1],
            "OBV": data['OBV'].iloc[-1],
            # Add more KPIs if needed
        })

    else:
        st.error(f'Aucune donnée trouvée pour {ticker}.')

# Add Analyser button
if st.button("Analyser"):
    try:
        with st.spinner("AlexIA est en pleine analyse..."):
            # Prepare the prompt
            insights = get_financial_insights(kpi_values)
            st.subheader("Insights sur les actions sélectionnées :")
            st.markdown(insights)
    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {str(e)}")
