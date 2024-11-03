# analyse_fond.py
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def render_analyse_fond():
    st.title("Analyse Fondamentale des Entreprises Canadiennes")

    # Input pour le symbole boursier de l'entreprise
    ticker = st.text_input("Entrez le symbole boursier de l'entreprise (ex: TD pour Toronto-Dominion Bank) :", "TD")

    if ticker:
        # Récupérer les données de l'entreprise
        stock_data = yf.Ticker(ticker)

        # Récupérer les états financiers
        try:
            balance_sheet = stock_data.balance_sheet
            income_statement = stock_data.financials
            cash_flow = stock_data.cashflow

            # Calcul des KPI
            net_income = income_statement.loc['Net Income'][0]
            total_assets = balance_sheet.loc['Total Assets'][0]
            total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'][0]
            total_equity = balance_sheet.loc['Total Equity Gross Minority Interest'][0]
            cash_flow_value = cash_flow.loc['Total Cash From Operating Activities'][0]

            # Calculs des ratios
            return_on_assets = net_income / total_assets * 100
            debt_to_equity_ratio = total_liabilities / total_equity

            # Afficher les résultats
            st.subheader("Ratios Financiers")
            st.write(f"Return on Assets (ROA): {return_on_assets:.2f}%")
            st.write(f"Bénéfice Net: {net_income:.2f} CAD")
            st.write(f"Cash Flow: {cash_flow_value:.2f} CAD")
            st.write(f"Debt-to-Equity Ratio: {debt_to_equity_ratio:.2f}")

            # Graphiques
            st.subheader("Graphiques")
            fig, ax = plt.subplots(2, 2, figsize=(10, 10))

            # Graphique de Return on Assets
            ax[0, 0].bar([ticker], [return_on_assets], color='blue')
            ax[0, 0].set_title('Return on Assets')
            ax[0, 0].set_ylabel('ROA (%)')

            # Graphique du Bénéfice Net
            ax[0, 1].bar([ticker], [net_income], color='green')
            ax[0, 1].set_title('Bénéfice Net')
            ax[0, 1].set_ylabel('Bénéfice Net (CAD)')

            # Graphique du Cash Flow
            ax[1, 0].bar([ticker], [cash_flow_value], color='orange')
            ax[1, 0].set_title('Cash Flow')
            ax[1, 0].set_ylabel('Cash Flow (CAD)')

            # Graphique du Debt-to-Equity Ratio
            ax[1, 1].bar([ticker], [debt_to_equity_ratio], color='red')
            ax[1, 1].set_title('Debt-to-Equity Ratio')
            ax[1, 1].set_ylabel('Debt-to-Equity Ratio')

            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")

