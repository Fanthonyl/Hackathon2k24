import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import boto3
import plotly.graph_objects as go
import numpy as np
import math

# Extraire les secteurs et les entreprises correspondantes
def get_sectors_from_db(database):
    return {domaine: [(entry['ticker'], entry['nom']) for entry in database if entry['domaine'] == domaine] for domaine in set(entry['domaine'] for entry in database)}

comprehend = boto3.client('comprehend', region_name='us-west-2')

def classify_sentiment_comprehend(tweet):
    response = comprehend.detect_sentiment(Text=tweet, LanguageCode='en')
    return response['Sentiment']

def multi_colormap_semi(database, selected_company, other_companies):
    results = []
    all_companies = [selected_company] + other_companies

    for nom in all_companies:
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
                cursor_position = (positive_ratio + ((neutral_tweets + mixed_tweets) / total_tweets) / 2) * 100
            else:
                cursor_position = 0

            results.append((nom, cursor_position))

    # Trier les résultats par ordre décroissant de la valeur
    results.sort(key=lambda x: x[1], reverse=True)

    # Affichage de toutes les entreprises sur un même plot avec Plotly
    fig = go.Figure()

    noms = [nom for nom, _ in results]
    valeurs = [valeur for _, valeur in results]

    # Générer des couleurs avec un dégradé de violet
    #colors = [f'rgba(150, 0, {180 - i * 5}, 0.8)' for i in range(len(valeurs))]
    colors = [f'rgba(150, 0, {190 - i * 20}, 0.8)' for i in range(len(valeurs))]

    fig.add_trace(go.Bar(
        x=valeurs,
        y=noms,
        orientation='h',
        marker_color=colors,
        textposition='auto',
        width=0.2,
        marker=dict(line=dict(width=0))  # Suppression des contours des barres
    ))


    # Ajouter une ligne pointillée à 50%
    fig.add_shape(
        type="line",
        x0=50,
        x1=50,
        y0=-0.5,
        y1=len(noms) - 0.5,
        line=dict(
            color="#964aff",
            width=1,
            dash="dashdot",
        ),
    )

    fig.update_layout(
        height=150 + len(noms) * 50,
        title='Sentiment positif global des entreprises sélectionnées',
        xaxis_title='Pourcentage de sentiment positif global',
        xaxis=dict(range=[0, 100]),
        yaxis=dict(autorange='reversed'),
        barmode='group',
        bargap=0.1  # Réduction de l'espace entre les barres pour les rendre plus fines
    )
    st.plotly_chart(fig)

def render_sentiment(database):
    st.title("Sentiment")

    # Extraire les secteurs à partir de la base de données
    sectors_from_db = get_sectors_from_db(database)

    # Ajout de la sélection du secteur
    st.subheader("Sélection du secteur")
    selected_sector = st.selectbox(
        "Choisissez un secteur :",
        list(sectors_from_db.keys())
    )

    # Formater les entreprises comme "Nom (Ticker)"
    formatted_companies = [f"{nom} ({ticker})" for ticker, nom in sectors_from_db[selected_sector]]

    # Ajout de la sélection d'une entreprise spécifique
    st.subheader("Sélection d'une entreprise")
    selected_company = st.selectbox(
        "Choisissez une entreprise :",
        formatted_companies
    )

    # Ajout de la case à cocher pour sélectionner/désélectionner toutes les entreprises
    st.subheader("Sélection des autres entreprises")
    select_all = st.checkbox("Tout sélectionner / Tout désélectionner", value=False)

    checkboxes = {}
    for company in formatted_companies:
        # Ne pas afficher l'entreprise sélectionnée
        if company != selected_company:
            # Si "Tout sélectionner" est activé, cocher la case, sinon laisser décochée
            checkboxes[company] = st.checkbox(company, value=select_all)

    # Mettre à jour la liste des autres entreprises sélectionnées
    other_companies = [company.split(' (')[0] for company, checked in checkboxes.items() if checked]  # Extraire le nom sans le ticker

    if st.button("Lancer l'analyse"):
        # Appel à la fonction d'analyse
        try:
            # Extraire le nom sans le ticker pour l'entreprise sélectionnée
            company_name = selected_company.split(' (')[0]
            multi_colormap_semi(database, company_name, other_companies)
        except Exception as e:
            st.error(f"Une erreur est survenue lors de l'analyse: {str(e)}")
