import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import boto3
import plotly.graph_objects as go
import numpy as np
import math

# Dictionnaire des secteurs et entreprises correspondantes (ticker et nom)
sectors = {
    'Technologie': [('SHOP.TO', 'Shopify'), ('CSU.TO', 'Constellation Software'), ('BB.TO', 'BlackBerry'), ('LSPD.TO', 'Lightspeed'), ('DND.TO', 'Dye & Durham')],
    'Finance': [('RY.TO', 'Royal Bank of Canada'), ('TD.TO', 'Toronto-Dominion Bank'), ('BNS.TO', 'Bank of Nova Scotia'), ('BMO.TO', 'Bank of Montreal'), ('CM.TO', 'Canadian Imperial Bank of Commerce')],
    'Santé': [('GUD.TO', 'Knight Therapeutics'), ('CXR.TO', 'Concordia International'), ('NHC.TO', 'Northwest Healthcare'), ('PFE.TO', 'Pfizer'), ('ABBV.TO', 'AbbVie')],
    'Transport': [('CNR.TO', 'Canadian National Railway'), ('CP.TO', 'Canadian Pacific Railway'), ('TFII.TO', 'TFI International'), ('WTE.TO', 'WestJet'), ('CAE.TO', 'CAE Inc.')],
    'Énergie': [('SU.TO', 'Suncor Energy'), ('ENB.TO', 'Enbridge'), ('TRP.TO', 'TC Energy'), ('CVE.TO', 'Cenovus Energy'), ('CNQ.TO', 'Canadian Natural Resources')]
}

comprehend = boto3.client('comprehend', region_name='us-west-2')

def classify_sentiment_comprehend(tweet):
    response = comprehend.detect_sentiment(Text=tweet, LanguageCode='en')
    return response['Sentiment']

def multi_colormap_semi(liste_nom):
    results = []

    for idx, nom in enumerate(liste_nom):
        with st.spinner(f"Analyse des avis utilisateurs pour {nom}..."):
            URL = f"https://twstalker.com/search/{nom}"
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")
            tweets = []
            job_elements = soup.find_all("p")
            nb_tweets = 30

            for i, job_element in enumerate(job_elements[:nb_tweets]):
                element = job_element.text
                tweets.append(element)

            tweets = tweets[1:]  # Supprimer le premier élément qui cause un bug

            positive_tweets = 0
            negative_tweets = 0
            neutral_tweets = 0
            mixed_tweets = 0

            for tweet in tweets:
                sentiment = classify_sentiment_comprehend(tweet)
                if sentiment == 'POSITIVE':
                    positive_tweets += 1
                elif sentiment == 'NEGATIVE':
                    negative_tweets += 1
                elif sentiment == 'NEUTRAL':
                    neutral_tweets += 1
                elif sentiment == 'MIXED':
                    mixed_tweets += 1

            total_tweets = len(tweets)
            if total_tweets > 0:
                positive_ratio = positive_tweets / total_tweets
                negative_ratio = negative_tweets / total_tweets
                neutral_mixed_ratio = (neutral_tweets + mixed_tweets) / total_tweets
            else:
                positive_ratio = negative_ratio = neutral_mixed_ratio = 0

            cursor_position = (positive_ratio + (neutral_mixed_ratio / 2)) * 100

            results.append((nom, cursor_position))

    # Trier les résultats par ordre décroissant de la valeur
    results.sort(key=lambda x: x[1], reverse=True)

    # Affichage de toutes les entreprises sur un même plot avec Plotly
    fig = go.Figure()

    noms = [nom for nom, _ in results]
    valeurs = [valeur for _, valeur in results]

    # Générer des couleurs dans une teinte de violet plus prononcée pour chaque barre
    colors = [f'rgba(102, 0, {100 + i * 25}, 0.8)' for i in range(len(valeurs))]

    fig.add_trace(go.Bar(
        x=valeurs,
        y=noms,
        orientation='h',
        marker_color=colors,
        text=valeurs,
        textposition='auto',
        width=0.1,
        marker=dict(line=dict(width=0))  # Réduction de la largeur des lignes des barres
    ))

    # Ajouter une ligne pointillée à 50%
    fig.add_shape(
        type="line",
        x0=50,
        x1=50,
        y0=-0.5,
        y1=len(noms) - 0.5,
        line=dict(
            color="purple",
            width=1,
            dash="dashdot",
        ),
    )

    fig.update_layout(
        title='Sentiment positif global des entreprises sélectionnées',
        xaxis_title='Pourcentage de sentiment positif global',
        xaxis=dict(range=[0, 100]),
        yaxis=dict(autorange='reversed'),
        barmode='group',
        bargap=0.02  # Réduction de l'espace entre les barres pour les rendre plus fines
    )
    st.plotly_chart(fig)

def render_sentiment():
    st.title("Sentiment")

    # Ajout de la sélection du secteur
    st.subheader("Sélection du secteur")
    selected_sector = st.selectbox(
        "Choisissez un secteur :",
        list(sectors.keys())
    )

    # Formater les entreprises comme "Nom (Ticker)"
    formatted_companies = [f"{name} ({ticker})" for ticker, name in sectors[selected_sector]]

    # Ajout de la sélection des entreprises en fonction du secteur choisi
    st.subheader("Sélection des entreprises")
    selected_companies = []
    checkboxes = {}
    for company in formatted_companies:
        checkboxes[company] = st.checkbox(company)

    for company, checked in checkboxes.items():
        if checked:
            with st.spinner(f"En attente de l'analyse pour {company}..."):
                selected_companies.append(company)

    if selected_companies:

        # Extraire les noms des entreprises sans les tickers
        company_names = [entry.split(' (')[0] for entry in selected_companies]
        if st.button("Lancer l'analyse"):
            multi_colormap_semi(company_names)
    else:
        st.write("### Aucune entreprise sélectionnée")