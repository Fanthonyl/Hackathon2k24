import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

def render_analyse_fond():
    st.title("Analyse Fondamentale des Entreprises")

    # Sélection des entreprises
    tickers = st.multiselect(
        "Choisissez de 1 à 3 entreprises (sigles financiers)",
        ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "FB"],
        default=["AAPL"],
        max_selections=3
    )

    if len(tickers) == 0:
        st.warning("Veuillez sélectionner au moins une entreprise.")
        return

    # Initialisation d'un DataFrame pour stocker les données financières
    data = []

    # Récupérer les informations pour chaque ticker sélectionné
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Récupérer les données financières et ajouter au tableau
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

        # Calcul du Free Cash Flow - on prend la valeur la plus récente
        cash_flow = stock.cashflow.loc["Free Cash Flow"] if "Free Cash Flow" in stock.cashflow.index else None
        if cash_flow is not None and not cash_flow.empty:
            row["Free Cash Flow"] = cash_flow.iloc[0]  # Prend la première valeur, qui est la plus récente
        else:
            row["Free Cash Flow"] = 'N/A'

        data.append(row)

    # Convertir la liste de données en DataFrame
    df = pd.DataFrame(data)

    # Afficher le tableau comparatif
    st.subheader("Tableau Comparatif des Données Financières")
    st.write(df)

    # Sélection des colonnes à tracer (historical data)
    st.subheader("Évolution des Stocks dans le Temps")
    historical_data_options = [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume"
    ]
    
    selected_columns = st.multiselect(
        "Sélectionnez des éléments à afficher",
        options=historical_data_options,
    )

    # Validate selection
    if len(selected_columns) == 0:
        st.warning("Veuillez sélectionner au moins un élément.")
        return

    # Sélection de la période
    period = st.selectbox("Sélectionnez la période", ["1mo", "3mo", "6mo", "1y","2y", "5y", "10y", "ytd", "max"])

    # Initialisation d'un DataFrame pour stocker les données de stock pour le graphique
    stock_data_combined = pd.DataFrame()

    # Boucle sur les tickers pour récupérer les données de stock
    for ticker in tickers:
        stock_data = yf.download(ticker, period=period)

        for column in selected_columns:
            stock_data_combined[f"{ticker} - {column}"] = stock_data[column]

    # Créer une figure avec Plotly
    fig = go.Figure()

    # Ajouter les traces pour chaque colonne sélectionnée
    for column in selected_columns:
        for ticker in tickers:
            fig.add_trace(go.Scatter(x=stock_data_combined.index, 
                                     y=stock_data_combined[f"{ticker} - {column}"],
                                     mode='lines', 
                                     name=f"{ticker} - {column}"))

    # Mettre à jour la mise en page
    fig.update_layout(
        title='Comparaison de l\'Évolution des Données',
        xaxis_title='Date',
        yaxis_title='Valeur',
        legend=dict(x=0, y=1, traceorder='normal', orientation='h')
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)

