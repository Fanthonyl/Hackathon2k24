import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def render_home(database):

    # Affichage avec Streamlit
    st.title("Analyse des valeurs moyennes des actions par secteur au Canada")

    # Sélection de la période par l'utilisateur
    time_span = st.selectbox(
        "Sélectionnez la période pour l'analyse:",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        index=3  # Définit la période par défaut à "1y"
    )

    # Récupération des données
    #@st.cache_data
    def get_data():
        data = {}

        for action in database:
            try:
                # Utilisation de la période sélectionnée
                df = yf.download(action['ticker'], period=time_span)["Adj Close"]
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

    # Création de la figure avec deux axes Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Ajout des courbes pour chaque secteur sauf Technologie
    for col in df_plot.columns[1:]:
        if col != "Technologie":
            fig.add_trace(
                go.Scatter(x=df_plot['Date'], y=df_plot[col], name=col),
                secondary_y=False
            )

    # Ajout de la courbe pour le secteur Technologie avec le deuxième axe Y
    fig.add_trace(
        go.Scatter(x=df_plot['Date'], y=df_plot['Technologie'], name='Technologie', line=dict(color='red')),
        secondary_y=True
    )

    # Mise à jour des titres et des axes
    fig.update_layout(
        title="Évolution moyenne des valeurs des actions par secteur au Canada",
        xaxis_title="Date",
        legend_title_text='Secteur',
        autosize=False,
        width=1600,  # Agrandissement de la taille pour un graph plus large
        height=600,  # Ajustement de la hauteur pour plus de clarté
        margin=dict(l=50, r=50, t=80, b=50),  # Espacement pour éviter la superposition avec la légende
        legend=dict(
            x=-0.1,  # Placement de la légende à gauche, en dehors du graphique
            y=1,  # Alignement en haut
            xanchor='left',  # Ancrage à gauche
            orientation="v"  # Orientation verticale de la légende
        )
    )
    fig.update_yaxes(title_text="Prix moyen ($CAD)", secondary_y=False)
    fig.update_yaxes(title_text="Prix moyen ($CAD) - Technologie", secondary_y=True)
    st.plotly_chart(fig)