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
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go  # Importer Plotly


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


def display_kpis_inline(df, label):
    if df.empty:
        st.write(f"*Aucune donnée disponible pour {label}.")
    else:
        df_sorted = df.sort_values(by=df.columns[1], ascending=True)  # Trier par la colonne de valeur
        st.write(f"##### {label}")
        columns = st.columns(len(df_sorted))
        for i, (index, row) in enumerate(df_sorted.iterrows()):
            with columns[i]:
                st.metric(label=row[0], value=f"{row[1]:.3f}")

def get_financial_kpi(symbol, kpi):
    kpi_list = [
        'returnOnAssets', 'returnOnEquity', 'Net Profit Margin',
        'debtToEquity', 'trailingPE',
        'ebitda', 'freeCashflow',
        'trailingEps'
    ]

    if kpi not in kpi_list:
        raise ValueError(f"Le KPI '{kpi}' n'est pas pris en charge. Veuillez choisir parmi {kpi_list}.")

    company = yf.Ticker(symbol)
    info = company.info

    if kpi == 'returnOnAssets':
        return info.get('returnOnAssets')
    elif kpi == 'returnOnEquity':
        return info.get('returnOnEquity')
    elif kpi == 'Net Profit Margin':
        return info.get('netProfitMargin')
    elif kpi == 'debtToEquity':
        return info.get('debtToEquity')
    elif kpi == 'trailingPE':
        return info.get('trailingPE')
    elif kpi == 'ebitda':
        return info.get('ebitda')
    elif kpi == 'freeCashflow':
        return info.get('freeCashflow')
    elif kpi == 'trailingEps':
        return info.get('trailingEps')

    return None

def render_analyse_fond(database):
    st.title("Analyse fondamentale")

    col1, col2 = st.columns([3, 1])

    with col1:
        entreprises = [item['nom'] for item in database]
        entreprise_selectionnee = st.selectbox("Choisissez une entreprise", entreprises)
        entreprise_info = next((item for item in database if item['nom'] == entreprise_selectionnee), None)
        ticker_selectionne = entreprise_info['ticker'] if entreprise_info else None
        domaine_selectionne = entreprise_info['domaine'] if entreprise_info else None

    with col2:
        groupes = {
            "Groupe 1": ['returnOnAssets', 'returnOnEquity'], #'Net Profit Margin'
            "Groupe 2": ['debtToEquity', 'trailingPE'],
            "Groupe 3": [], #freeCashflow', 'ebitda'
            "Groupe 4": ['trailingEps']
        }
        tous_les_kpis = [kpi for kpis in groupes.values() for kpi in kpis]
        kpi_selectionne = st.selectbox("Sélectionnez un Indicateurs financiers", options=tous_les_kpis)

    entreprises_meme_secteur = [item for item in database if item['domaine'] == domaine_selectionne]

    if entreprises_meme_secteur:
        data_kpi = []
        for entreprise in entreprises_meme_secteur:
            kpi_valeur = get_financial_kpi(entreprise['ticker'], kpi_selectionne)
            data_kpi.append({'Entreprise': entreprise['nom'], 'Valeur KPI': kpi_valeur})
        
        df_kpi = pd.DataFrame(data_kpi)
        df_kpi_original = df_kpi.copy()
        df_kpi = df_kpi[df_kpi['Entreprise'] != entreprise_selectionnee]

        col1, col2 = st.columns([3, 1])

        with col1:
            if ticker_selectionne:
                data = yf.Ticker(ticker_selectionne).history(period="1y")

                # Créer un graphique interactif avec Plotly
                fig = go.Figure()

                # Ajouter les traces pour Open, Low, High, Close, Adj Close
                fig.add_trace(go.Scatter(x=data.index,y=data['Open'], mode='lines', name='Open',line=dict(color='orange')))
                fig.add_trace(go.Scatter(x=data.index, y=data['High'],mode='lines', name='High',line=dict(color='green')))
                fig.add_trace(go.Scatter(x=data.index, y=data['Low'], mode='lines',name='Low',line=dict(color='red')))
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close',line=dict(color='blue')))
                fig.update_layout(xaxis_title="Date", yaxis_title="Valeur (EUR)", template="plotly_white")

                st.plotly_chart(fig, use_container_width=True)        
        with col2:
            st.subheader("")
            resultat = get_financial_kpi(ticker_selectionne, kpi_selectionne)
            st.markdown(f"<div style='text-align: center;'><h3>{ticker_selectionne}</h3></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'><h2>{resultat}</h2></div>", unsafe_allow_html=True)

            moyenne_secteur = df_kpi_original['Valeur KPI'].mean()
            st.markdown(f"<div style='text-align: center;'><h3>{domaine_selectionne}</h3></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'><h2>{moyenne_secteur:.3f}</h2></div>", unsafe_allow_html=True)


        if not df_kpi.empty:
            display_kpis_inline(df_kpi, f"{kpi_selectionne} pour les autres entreprises dans le secteur {domaine_selectionne}")
        else:
            st.write("Aucune donnée à afficher pour les entreprises dans le même secteur.")

        secteurs_distincts = set(item['domaine'] for item in database if item['domaine'] != domaine_selectionne)
        moyennes_par_secteur = []
        for secteur in secteurs_distincts:
            entreprises_autre_secteur = [item for item in database if item['domaine'] == secteur]
            data_kpi_secteur = []
            
            for entreprise in entreprises_autre_secteur:
                kpi_valeur = get_financial_kpi(entreprise['ticker'], kpi_selectionne)
                if kpi_valeur is not None:
                    data_kpi_secteur.append(kpi_valeur)
            
            if len(data_kpi_secteur) > 0:
                moyenne_secteur = np.mean(data_kpi_secteur)
                moyennes_par_secteur.append({'Secteur': secteur, 'Valeur moyenne du KPI': moyenne_secteur})
        
        df_moyennes_secteurs = pd.DataFrame(moyennes_par_secteur)
        if not df_moyennes_secteurs.empty:
            display_kpis_inline(df_moyennes_secteurs, f"{kpi_selectionne} pour les autres secteurs")
        else:
            st.write("Aucune donnée à afficher pour les autres secteurs.")
    
    # Get financial insights from AWS Bedrock
    st.subheader("Insights Financiers")
    financial_insights = get_financial_insights(ticker_selectionne)
    st.write(financial_insights)
