import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go  # Importer Plotly

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
