import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
from data import database

def display_kpis_inline(df, label):
    if df.empty:
        st.write(f"*Aucune donnée disponible pour {label}.")
    else:
        df_sorted = df.sort_values(by=df.columns[1], ascending=True)  # Trier par la colonne de valeur
        st.write(f"### {label}")
        columns = st.columns(len(df_sorted))
        for i, (index, row) in enumerate(df_sorted.iterrows()):
            with columns[i]:
                color = "green" if row[1] >= 0 else "red"  # Colorer en vert ou rouge
                value = f"<span style='color:{color}; font-size:24px; font-weight:bold;'>{row[1]:.2f}%</span>"  # Taille et poids augmentés
                st.markdown(f"<div style='text-align:center; font-size:20px; margin-bottom:10px;'>{row[0]}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;'>{value}</div>", unsafe_allow_html=True)


# Streamlit app
st.title("Optimisation du Portefeuille")

col1, col2, col3 = st.columns([1, 1, 5])
with col1:
    # Input: portefeuille initial
    budget = st.number_input("Entrez budget total (CAD):", min_value=100, step=100)
with col2:
    # Sélection du profil d'investisseur
    risk_profile = st.selectbox("Profil d'investisseur:", ["Risque", "Prudent", "Optimal"])
with col3:
    # Input: choix des entreprises
    options = [stock['nom'] for stock in database]
    selected_stocks = st.multiselect("Choisissez les entreprises dans lesquelles investir:", options)

if budget > 0 and selected_stocks:
    # Filtrer les tickers sélectionnés
    selected_tickers = [stock['ticker'] for stock in database if stock['nom'] in selected_stocks]

    # Télécharger les données historiques
    data = yf.download(selected_tickers, period="1y")['Adj Close']

    # Calcul des rendements quotidiens
    daily_returns = data.pct_change().dropna()

    # Calcul des rendements annuels et matrice de covariance
    annual_returns = daily_returns.mean() * 252
    cov_matrix = daily_returns.cov() * 252

    # Optimisation: Portfolio Weights
    num_assets = len(selected_tickers)
    num_portfolios = 10000
    results = np.zeros((4, num_portfolios))  # Ajout d'une ligne pour le risque total
    weights_record = []

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_return = np.dot(weights, annual_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility
        total_risk = np.dot(weights.T, np.dot(cov_matrix, weights))  # Risque total
        results[0, i] = portfolio_return
        results[1, i] = portfolio_volatility
        results[2, i] = sharpe_ratio
        results[3, i] = total_risk

    # Ajustement des poids en fonction du profil d'investisseur
    if risk_profile == "Risque":
        max_sharpe_idx = np.argmax(results[2])
    elif risk_profile == "Prudent":
        max_sharpe_idx = np.argmin(results[1])  # Minimiser la volatilité
    else:  # Optimal
        max_sharpe_idx = np.argmax(results[2])

    optimal_weights = weights_record[max_sharpe_idx]

    # Calcul de la valeur du portefeuille après 1 an
    portfolio_value_after = budget * (1 + results[0, max_sharpe_idx])

    # Valeur initiale du portefeuille
    portfolio_value_initial = budget

    # Comparaison des valeurs avant et après
    col1, col2, col3= st.columns([1, 1, 2])

    with col1:
        st.subheader("Performance attendue")
        st.metric("Rendement attendu", f"{results[0, max_sharpe_idx] * 100:.2f}%", "")
        st.metric("Risque (volatilité)", f"{results[1, max_sharpe_idx] * 100:.2f}%", "")
        st.metric("Ratio de Sharpe", f"{results[2, max_sharpe_idx]:.2f}", "")
    

    with col2:
        # Affichage de la comparaison du portefeuille
        st.subheader("Comparaison de la valeur du portefeuille")
        st.metric("Valeur du portefeuille après 1 an", f"{portfolio_value_after:.2f} CAD", f"{portfolio_value_after - portfolio_value_initial:.2f} CAD")
        
    with col3:
        # Afficher la répartition optimale sous forme de camembert
        df_weights = pd.DataFrame({
            'Stock': selected_tickers,
            'Allocation (%)': optimal_weights * 100
        })
        st.subheader("Répartition optimale")
        fig = px.pie(df_weights, names='Stock', values='Allocation (%)', height=300)
        st.plotly_chart(fig)
    
    # Calcul du rendement et de la volatilité du dernier mois pour chaque action
    last_month_returns = daily_returns.iloc[-21:]  # Prendre les 21 derniers jours
    last_month_performance = (last_month_returns + 1).prod() - 1  # Rendement cumulé
    
    # Calcul de la volatilité du dernier mois pour chaque action
    volatility_last_month = last_month_returns.std() * np.sqrt(21)  # Volatilité mensuelle

    last_month_performance_df = pd.DataFrame({
        'Stock': selected_tickers,
        'Rendement du dernier mois (%)': last_month_performance * 100,
        'Volatilité du dernier mois (%)': volatility_last_month * 100
    })

    # Affichage des rendements en ligne
    display_kpis_inline(last_month_performance_df[['Stock', 'Rendement du dernier mois (%)']], "Rendement du dernier mois")

    # Affichage de la volatilité en ligne
    display_kpis_inline(last_month_performance_df[['Stock', 'Volatilité du dernier mois (%)']], "Volatilité du dernier mois")


else:
    st.write("Veuillez entrer un budget et choisir des entreprises.")
