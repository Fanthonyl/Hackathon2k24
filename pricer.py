import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# Database of available stocks
database = [
    {'nom': 'Saputo', 'ticker': 'SAP.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Alimentation Couche-Tard', 'ticker': 'ATD.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Loblaw', 'ticker': 'L.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Maple Leaf Foods', 'ticker': 'MFI.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Empire Company', 'ticker': 'EMP-A.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Premium Brands', 'ticker': 'PBH.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'North West Company', 'ticker': 'NWC.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Canadian National Railway', 'ticker': 'CNR.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Canadian Pacific Kansas City', 'ticker': 'CP.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'TFI International', 'ticker': 'TFII.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Westshore Terminals', 'ticker': 'WTE.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'CAE Inc.', 'ticker': 'CAE.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Air Canada', 'ticker': 'AC.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Student Transportation', 'ticker': 'STB.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Suncor Energy', 'ticker': 'SU.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Enbridge', 'ticker': 'ENB.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'TC Energy', 'ticker': 'TRP.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Cenovus Energy', 'ticker': 'CVE.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Canadian Natural Resources', 'ticker': 'CNQ.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Pembina Pipeline', 'ticker': 'PPL.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Gibson Energy', 'ticker': 'GEI.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'AltaGas', 'ticker': 'ALA.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Fortis', 'ticker': 'FTS.TO', 'domaine': 'Services publics', 'suivi': False},
    {'nom': 'Hydro One', 'ticker': 'H.TO', 'domaine': 'Services publics', 'suivi': False},
    {'nom': 'Cogeco', 'ticker': 'CGO.TO', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Quebecor', 'ticker': 'QBR-B.TO', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Rogers', 'ticker': 'RCI-B.TO', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Telus', 'ticker': 'T.TO', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Bell Canada', 'ticker': 'N/A', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Shopify', 'ticker': 'SHOP.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Constellation Software', 'ticker': 'CSU.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'BlackBerry', 'ticker': 'BB.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Lightspeed', 'ticker': 'LSPD.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Dye & Durham', 'ticker': 'DND.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Kinaxis', 'ticker': 'KXS.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Enghouse Systems', 'ticker': 'ENGH.TO', 'domaine': 'Technologie', 'suivi': False}
]
def render_pricer():
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

        # Résultats
        st.subheader("Répartition optimale")
        for i, stock in enumerate(selected_tickers):
            st.write(f"{stock}: {optimal_weights[i] * 100:.2f}%")

        st.subheader("Performance attendue")
        st.write(f"Rendement attendu: {results[0, max_sharpe_idx] * 100:.2f}%")
        st.write(f"Risque (volatilité): {results[1, max_sharpe_idx] * 100:.2f}%")
        st.write(f"Ratio de Sharpe: {results[2, max_sharpe_idx]:.2f}")
    else:
        st.write("Veuillez entrer un budget et choisir des entreprises.")
