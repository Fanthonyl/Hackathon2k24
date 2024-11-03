import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def get_board_risk(ticker):
    stock = yf.Ticker(ticker)
    board_risk = stock.info.get('boardRisk', 'Non disponible')
    return board_risk

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
        
        # Récupération des revenus
        compensation = exec.get('totalAnnualCompensation', 'Non disponible')

        if not age:
            age = get_age_from_web(name, company_name)
        
        data.append({
            'Nom': name,
            'Âge': age,
            'Position': title,
            'Compensation Annuelle': compensation
        })
    
    return pd.DataFrame(data), board_risk

def render_board():
    st.title("Informations des dirigeants d'entreprise")

    ticker = st.text_input("Entrez le symbole boursier de l'entreprise (par exemple, AAPL pour Apple) :")

    if ticker:
        st.subheader(f"Tableau de bord des dirigeants de {ticker}")
    
        try:
            df , board_risk = get_executive_info(ticker)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.subheader("Risque du conseil d'administration")
                st.info(f"Risque du conseil d'administration : {board_risk}")
            else:
                st.warning("Aucune information sur les dirigeants n'a été trouvée pour cette entreprise.")
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
    else:
        st.info("Veuillez entrer un symbole boursier pour afficher les informations des dirigeants.")

    st.markdown("---")
    st.caption("Les données sont fournies par Yahoo Finance et complétées par des recherches web.")

if __name__ == "__main__":
    render_board()