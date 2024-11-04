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
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


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

def get_financial_insights(ticker):
    session_id = str(uuid.uuid1())
    agent_id = 'ACVSW7ULXC'
    agent_alias_id = 'FGVZUPEISZ'
    
    # Prepare company data from yfinance
    company_data = []
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
    input_text = "Provide a french summary of the following information. Be brief and concise. I want you to also analyse the gender equity, salaries and age of the board. Work with bullet points and line breaks. \n"
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

    # Invoke the agent via the BedrockAgentRuntimeWrapper
    logger.info(f"Invoking agent with prompt:\n{input_text}")
    insights = bedrock_wrapper.invoke_agent(agent_id, agent_alias_id, session_id, input_text)

    # Log the response for debugging
    logger.info("Financial insights received:")
    logger.info(insights)
    
    return insights or 'No insights available.'

def get_board_risk(ticker):
    stock = yf.Ticker(ticker)
    board_risk = stock.info.get('boardRisk', 'Non disponible')
    return board_risk



def get_age_from_web(name, company):
    search_query = f"{name} {company} age"
    url = f"https://www.google.com/search?q={search_query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Cette partie est très basique et peut nécessiter des ajustements
    age_text = soup.find(text=lambda t: t and 'age' in t.lower())
    if age_text:
        age = ''.join(filter(str.isdigit, age_text))
        return age if age else "Non trouvé"
    return "Non trouvé"

def get_executive_info(ticker):
    stock = yf.Ticker(ticker)
    company_name = stock.info.get('longName', '')
    executives = stock.info.get('companyOfficers', [])
    board_risk = get_board_risk(ticker)
    
    data = []
    for exec in executives:
        name = exec.get('name', '')
        age = exec.get('age', '')
        title = exec.get('title', '')
        
        # Récupération des revenus (modifié ici)
        compensation = exec.get('totalPay', 'Non disponible')

        if not age:
            age = get_age_from_web(name, company_name)
        
        data.append({
            'Nom': name,
            'Âge': age,
            'Position': title,
            'Paye annuelle': compensation
        })
    
    return pd.DataFrame(data), board_risk

def render_board(database):
    st.title("Informations des dirigeants d'entreprise")
    st.markdown("""Explorez avec Alexia les caractéristiques du board afin de prévoir les futures décisions.""")

    entreprises = [item['nom'] for item in database]
    entreprise_selectionnee = st.selectbox("Choisissez une entreprise", entreprises)
    ticker = next((item['ticker'] for item in database if item['nom'] == entreprise_selectionnee), None)

    if ticker:
        st.subheader(f"Tableau de bord des dirigeants de {ticker}")
    
        try:
            df , board_risk = get_executive_info(ticker)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.subheader("Risque du conseil d'administration")
                # Affichage de la jauge de risque
                if board_risk != 'Non disponible':
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=board_risk,
                        title={'text': "Risque du Conseil d'Administration"},
                        gauge={
                            'axis': {'range': [1, 10]},
                            'bar': {'color': 'red' if board_risk >= 7 else 'orange' if board_risk >= 4 else 'green'},
                            'steps': [
                                {'range': [1, 4], 'color': 'lightgreen'},
                                {'range': [4, 7], 'color': 'yellow'},
                                {'range': [7, 10], 'color': 'lightcoral'}    
                                ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'value': board_risk
                            }
                        }
                    ))
                    st.plotly_chart(fig)
                else:
                    st.info("Le risque du conseil d'administration est : Non disponible")
            else:
                st.warning("Aucune information sur les dirigeants n'a été trouvée pour cette entreprise.")
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
    else:
        st.info("Veuillez entrer un symbole boursier pour afficher les informations des dirigeants.")

    # Get financial insights from AWS Bedrock
    st.subheader("Insights sur le board")
    with st.spinner("AlexIA réfléchit profondément..."):
        try:
            financial_insights = get_financial_insights(ticker)
            st.write(financial_insights)
        except Exception as e:
            st.error("Erreur lors de l'obtention de l'analyse.")
            logger.error(f"Erreur: {e}")


    st.markdown("---")
    st.caption("Les données sont fournies par Yahoo Finance et complétées par des recherches web.")