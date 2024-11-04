import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px

def render_pricer(database):
    # Streamlit app
    st.title("Optimisateur de Portefeuille")

    # Input: portefeuille initial
    budget = st.number_input("Entrez votre budget total (en CAD):", min_value=0.0, step=100.0)

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
        results = np.zeros((3, num_portfolios))
        weights_record = []

        for i in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            weights_record.append(weights)
            portfolio_return = np.dot(weights, annual_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / portfolio_volatility
            results[0, i] = portfolio_return
            results[1, i] = portfolio_volatility
            results[2, i] = sharpe_ratio

        # Trouver le portefeuille optimal
        max_sharpe_idx = np.argmax(results[2])
        optimal_weights = weights_record[max_sharpe_idx]

        col1, col2 = st.columns([2,1])
    
        with col1:
            # Afficher la répartition optimale sous forme de camembert
            df_weights = pd.DataFrame({
                'Stock': selected_tickers,
                'Allocation (%)': optimal_weights * 100
            })
            fig = px.pie(df_weights, names='Stock', values='Allocation (%)', title="Répartition optimale")
            st.plotly_chart(fig)

        with col2: 
            

            st.subheader("Performance attendue")
            st.write(f"Rendement attendu: {results[0, max_sharpe_idx] * 100:.2f}%")
            st.write(f"Risque (volatilité): {results[1, max_sharpe_idx] * 100:.2f}%")
            st.write(f"Ratio de Sharpe: {results[2, max_sharpe_idx]:.2f}")
    else:
        st.write("Veuillez entrer un budget et choisir des entreprises.")
