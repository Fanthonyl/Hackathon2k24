import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

def render_home(database):
    # Récupération des données
    @st.cache_data
    def get_data():
        data = {}
        end_date = datetime.today()
        start_date = end_date.replace(year=end_date.year - 1)

        for action in database:
            try:
                df = yf.download(action['ticker'], start=start_date, end=end_date)["Adj Close"]
                data[action['domaine']] = data.get(action['domaine'], []) + [df]
            except Exception as e:
                st.write(f"Erreur lors du téléchargement pour {action['nom']}: {e}")

        return data

    # Calcul des moyennes par secteur
    data = get_data()
    sector_averages = {}
    for secteur, valeurs in data.items():
        combined_df = pd.concat(valeurs, axis=1).mean(axis=1)
        sector_averages[secteur] = combined_df

    # Création du DataFrame pour la visualisation
    df_plot = pd.DataFrame(sector_averages)
    df_plot.reset_index(inplace=True)
    df_plot.rename(columns={"index": "Date"}, inplace=True)

    # Affichage avec Plotly
    fig = px.line(df_plot, x='Date', y=df_plot.columns[1:], title="Évolution moyenne des valeurs des actions par secteur au Canada (1 an)", labels={"value": "Prix moyen ($CAD)", "variable": "Secteur"})
    fig.update_layout(legend_title_text='Secteur')

    # Affichage avec Streamlit
    st.title("Analyse des valeurs moyennes des actions par secteur au Canada")
    st.plotly_chart(fig)
