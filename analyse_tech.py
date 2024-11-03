import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta


def render_analyse_tech():
    # Titre principal
    st.title("Sélecteur de KPI avec groupes")

    # Groupes et leurs éléments
    groupes = {
        "Groupe 1": ["KPI 1", "KPI 2"],
        "Groupe 2": ["KPI 3"]
    }

    # Initialisation des choix sélectionnés
    choix_selectionnes = {}

    # Boucle pour afficher chaque groupe et ses KPI
    for groupe, kpis in groupes.items():
        st.subheader(groupe)  # Titre de groupe
        for kpi in kpis:
            choix_selectionnes[kpi] = st.checkbox(kpi)

    # Affichage des choix sélectionnés
    st.write("Choix sélectionnés :")
    for kpi, est_selectionne in choix_selectionnes.items():
        if est_selectionne:
            st.write(f"- {kpi}")
