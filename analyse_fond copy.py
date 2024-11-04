import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import boto3
import json
import uuid  # For generating a unique session ID
import logging
import pprint
from botocore.exceptions import ClientError

# setting logger
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

def get_financial_insights(tickers):
    session_id = str(uuid.uuid1())
    agent_id = 'ACVSW7ULXC'
    agent_alias_id = 'FGVZUPEISZ'
    
    # Prepare company data from yfinance
    company_data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        company_details = {
            "ticker": ticker,
            "industry": info.get("industry"),
            "business_summary": info.get("longBusinessSummary"),
            "full_time_employees": info.get("fullTimeEmployees"),
            "company_officers": [
                {
                    "name": officer.get("name"),
                    "age": officer.get("age"),
                    "title": officer.get("title"),
                    "total_pay": officer.get("totalPay")
                }
                for officer in info.get("companyOfficers", []) if officer
            ],
            "audit_risk": info.get("auditRisk"),
            "board_risk": info.get("boardRisk"),
            "compensation_risk": info.get("compensationRisk"),
            "shareholder_rights_risk": info.get("shareHolderRightsRisk"),
            "overall_risk": info.get("overallRisk"),
            "held_percent_insiders": info.get("heldPercentInsiders"),
            "held_percent_institutions": info.get("heldPercentInstitutions"),
        }
        company_data.append(company_details)
    
    # Create prompt for Bedrock input
    input_text = "Provide summary of the following information. Be brief and concise. I want you to also analyse the gender equity, salaries and age of the board. Work with bullet points and line breaks. \n"
    for data in company_data:
        input_text += (
            f"\nCompany: {data['ticker']}\n"
            f"- Industry: {data['industry']}\n"
            f"- Business Summary: {data['business_summary']}\n"
            f"- Full-Time Employees: {data['full_time_employees']}\n"
            "- Key Officers:\n"
        )
        for officer in data["company_officers"]:
            input_text += (
                f"  - Name: {officer['name']}, Age: {officer['age']}, Title: {officer['title']}, "
                f"Total Pay: {officer['total_pay']}\n"
            )
        input_text += (
            f"- Audit Risk: {data['audit_risk']}\n"
            f"- Board Risk: {data['board_risk']}\n"
            f"- Compensation Risk: {data['compensation_risk']}\n"
            f"- Shareholder Rights Risk: {data['shareholder_rights_risk']}\n"
            f"- Overall Risk: {data['overall_risk']}\n"
            f"- Held by Insiders: {data['held_percent_insiders']}\n"
            f"- Held by Institutions: {data['held_percent_institutions']}\n"
        )
    
    if len(tickers) > 1:
        input_text += "\nConclude with an overall comparison of the companies listed."

    # Invoke the agent via the BedrockAgentRuntimeWrapper
    logger.info(f"Invoking agent with prompt:\n{input_text}")
    insights = bedrock_wrapper.invoke_agent(agent_id, agent_alias_id, session_id, input_text)

    # Log the response for debugging
    logger.info("Financial insights received:")
    logger.info(insights)
    
    return insights or 'No insights available.'

def render_analyse_fond(tickers, period):
    st.title("Analyse Fondamentale des Entreprises")

    if len(tickers) == 0:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    # Initialize DataFrame for financial data
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
        cash_flow = stock.cashflow.loc["Free Cash Flow"] if "Free Cash Flow" in stock.cashflow.index else None
        row["Free Cash Flow"] = cash_flow.iloc[0] if cash_flow is not None and not cash_flow.empty else 'N/A'
        data.append(row)

    df = pd.DataFrame(data)
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
    financial_insights = get_financial_insights(ticke)
    st.write(financial_insights)
