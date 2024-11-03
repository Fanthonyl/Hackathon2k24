import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import boto3
import json
import uuid  # For generating a unique session ID
import logging
import pprint
# setting logger
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Bedrock clients
bedrock_client = boto3.client('bedrock', region_name='us-west-2')
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')  # Runtime client
sts_client = boto3.client('sts', region_name='us-west-2')
iam_client = boto3.client('iam', region_name='us-west-2')
lambda_client = boto3.client('lambda', region_name='us-west-2')
bedrock_agent_client = boto3.client('bedrock-agent', region_name='us-west-2')

def get_financial_insights(tickers):
    # Prepare session details
    session_id = str(uuid.uuid1())  # Generate a unique session ID
    enable_trace = False
    end_session = False
    agent_id = 'ACVSW7ULXC'  # Your agent ID
    agent_alias_id = 'CMUYMTYKA7'  # If applicable, otherwise replace with the specific alias

    # Define the input text for insights
    input_text = f"Provide financial insights for the following companies: {', '.join(tickers)}."
    #input_text = f"Say Hello to me"
    #print(f"Input text: {input_text}")

    # Invoke the agent with the Bedrock runtime client
    response = bedrock_agent_runtime_client.invoke_agent(
        inputText=input_text,
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        enableTrace=enable_trace,
        endSession=end_session
    )
    logger.info(pprint.pprint(response))

    # Parse the response
    insights = response.get('message', 'No insights available.')
    return insights


def render_analyse_fond(tickers, period):
    st.title("Analyse Fondamentale des Entreprises")

    if len(tickers) == 0:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    # Initialisation d'un DataFrame pour stocker les données financières
    data = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        row = {
            "Ticker": ticker,
            "Current Price": info.get('currentPrice', 'N/A'),
            "EBITDA": info.get('ebitda', 'N/A'),
            "ROA": info.get('returnOnAssets', 'N/A'),
            "ROE": info.get('returnOnEquity', 'N/A'),
            "EPS (diluted)": info.get('trailingEps', 'N/A'),
            "Debt-to-Equity": info.get('debtToEquity', 'N/A'),
            "Net Profit Margin": f"{info.get('profitMargins', 0) * 100:.2f}%" if info.get('profitMargins') is not None else 'N/A',
            "P/E Ratio (trailing)": info.get('trailingPE', 'N/A'),
            "P/E Ratio (forward)": info.get('forwardPE', 'N/A'),
        }

        # Free Cash Flow
        cash_flow = stock.cashflow.loc["Free Cash Flow"] if "Free Cash Flow" in stock.cashflow.index else None
        row["Free Cash Flow"] = cash_flow.iloc[0] if cash_flow is not None and not cash_flow.empty else 'N/A'

        data.append(row)

    df = pd.DataFrame(data)

    # Display the comparison table
    st.subheader("Tableau Comparatif des Données Financières")
    st.write(df)

    # Historical data visualization
    st.subheader("Évolution des Stocks dans le Temps")
    historical_data_options = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    selected_columns = st.multiselect("Sélectionnez des éléments à afficher", options=historical_data_options)

    if len(selected_columns) == 0:
        st.warning("Veuillez sélectionner au moins un élément.")
        return

    stock_data_combined = pd.DataFrame()
    for ticker in tickers:
        stock_data = yf.download(ticker, period=period)
        for column in selected_columns:
            stock_data_combined[f"{ticker} - {column}"] = stock_data[column]

    fig = go.Figure()
    for column in selected_columns:
        for ticker in tickers:
            fig.add_trace(go.Scatter(x=stock_data_combined.index, 
                                     y=stock_data_combined[f"{ticker} - {column}"],
                                     mode='lines', 
                                     name=f"{ticker} - {column}"))

    fig.update_layout(
        title='Comparaison de l\'Évolution des Données',
        xaxis_title='Date',
        yaxis_title='Valeur',
        legend=dict(x=0, y=1, traceorder='normal', orientation='h')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Get financial insights from AWS Bedrock
    st.subheader("Insights Financiers")
    financial_insights = get_financial_insights(tickers)
    st.write(financial_insights)
