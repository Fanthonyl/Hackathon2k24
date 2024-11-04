import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import boto3
import plotly.graph_objects as go
import numpy as np

from data import database

comprehend = boto3.client('comprehend', region_name='us-west-2')

# Extraire les secteurs et les entreprises correspondantes
def get_sectors_from_db(database):
    return {domaine: [(entry['ticker'], entry['nom']) for entry in database if entry['domaine'] == domaine] for domaine in set(entry['domaine'] for entry in database)}

def classify_sentiment_comprehend(tweet):
    response = comprehend.detect_sentiment(Text=tweet, LanguageCode='en')
    return response['Sentiment']

def multi_colormap_semi(database, selected_company, other_companies):
    results = []
    all_companies = [selected_company] + other_companies

    for nom in all_companies:
        with st.spinner(f"Analyse des tendances utilisateurs en temps réel pour pour {nom}..."):
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

    # Générer des couleurs avec un dégradé violet
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



    fig.update_layout(
        height=150 + len(noms) * 50,
        title='Analyse en temps réel de la popularité des entreprises du marché',
        xaxis_title='Pourcentage d\'opinions positives au sein du grand public',
        xaxis=dict(range=[0, 100]),
        yaxis=dict(autorange='reversed'),
        barmode='group',
        bargap=0.1  # Réduction de l'espace entre les barres pour les rendre plus fines
    )


    st.session_state['fig_multi_colormap'] = fig  # Stocker dans l'état après la création
    #st.plotly_chart(fig, key="multi_colormap")  # Afficher avec une clé unique






if 'fig_multi_colormap' not in st.session_state:
    st.session_state['fig_multi_colormap'] = None

if 'fig_entreprise_vs_clients' not in st.session_state:
    st.session_state['fig_entreprise_vs_clients'] = None


st.title("Analyse de Sentiments")

st.image("alexia.png", caption="Description de l'image")

# Extraire les secteurs à partir de la base de données
sectors_from_db = get_sectors_from_db(database)

st.write("Découvrez l'analyse détaillée des sentiments des utilisateurs envers les entreprises et les secteurs spécifiques. Identifiez les opinions positives, négatives, et neutres à travers des données collectées sur les réseaux sociaux.")


# Ajout de la sélection du secteur
st.subheader("Sélection d'une entreprise à analyser")

selected_sector = st.selectbox(
    "Sélectionnez un secteur industriel pour explorer les entreprises qui y sont associées :",
    list(sectors_from_db.keys())
)

# Formater les entreprises comme "Nom (Ticker)"
formatted_companies = [f"{nom} ({ticker})" for ticker, nom in sectors_from_db[selected_sector]]

# Ajout de la sélection d'une entreprise spécifique
selected_company = st.selectbox(
    "Sélectionnez l'entreprise que vous souhaitez analyser et comparer au reste du marché :",
    formatted_companies
)

# Ajout du bouton pour exécuter l'analyse de l'entreprise vs clients
if st.button("Exécuter l'analyse Entreprise vs Clients"):
    entreprise_vs_clients(selected_company.split(' (')[0])

# Afficher la figure existante `entreprise_vs_clients` si elle est déjà générée
if st.session_state['fig_entreprise_vs_clients'] is not None:
    st.plotly_chart(st.session_state['fig_entreprise_vs_clients'], key="entreprise_vs_clients_reloaded")

# Ajout de la case à cocher pour sélectionner/désélectionner toutes les entreprises
st.subheader("Analyse comparative avec les autres entreprises du marché")

st.write("Sélectionnez les entreprises que vous souhaitez inclure dans l'analyse comparative des sentiments. Cette option permet de visualiser les opinions sur plusieurs entreprises afin de voir comment elles se comparent entre elles.")

select_all = st.checkbox("Tout sélectionner / Tout désélectionner", value=False)

checkboxes = {}
for company in formatted_companies:
    if company != selected_company:
        checkboxes[company] = st.checkbox(company, value=select_all)

# Mettre à jour la liste des autres entreprises sélectionnées
other_companies = [company.split(' (')[0] for company, checked in checkboxes.items() if checked]

if st.button("Lancer l'analyse"):
    try:
        company_name = selected_company.split(' (')[0]
        multi_colormap_semi(database, company_name, other_companies)

    except Exception as e:
        st.error(f"Une erreur est survenue lors de l'analyse: {str(e)}")


# Afficher la figure existante `multi_colormap_semi` si elle est déjà générée
if st.session_state['fig_multi_colormap'] is not None:
    st.plotly_chart(st.session_state['fig_multi_colormap'], key="multi_colormap_reloaded")









def entreprise_vs_clients(nom):
    # Définir les couleurs pour le thème violet
    nom_original = nom
    colors = ['#800080', '#9370DB']  # Couleurs pour les barres
    nom = nom.replace(" ", "-").lower()
    cursor_positions = []
    labels = ["clients", nom]

    for type in labels:
        positive_tweets = 0
        negative_tweets = 0
        neutral_tweets = 0
        mixed_tweets = 0

        if type == nom:
            URL = f"https://twstalker.com/{nom}"
        else:
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
            neutral_ratio = neutral_tweets / total_tweets
            mixed_ratio = mixed_tweets / total_tweets

            if positive_tweets+negative_tweets == 0:
                cursor_position = 0.5
            else:
                if positive_ratio > negative_ratio:
                    cursor_position = 0.5 + positive_ratio/2
                else:
                    cursor_position = 0.5 - negative_ratio/2
            cursor_positions.append(cursor_position)
            
        else:
            cursor_positions.append(0.5)  # Si aucun tweet, position neutre
            st.write(f"Aucun tweet trouvé pour {type}.")

    fig = go.Figure(data=[
        go.Bar(
            y=["Opinion publique", nom_original],
            x=cursor_positions,
            orientation='h',
            marker_color=colors,
            text=[f"{pos:.2f}%" for pos in cursor_positions],
            textposition='auto',
            width=0.2,
        )
    ])


    fig.update_layout(
        height=250,
        title=f"Analyse en temps réel des taux de sentiments positifs pour {nom_original}, en fonction de leurs communiqués et de l'opinion publique",
        xaxis_title=f"Taux de sentiments positifs pour {nom_original} selon des utilisateurs",
        yaxis_title="",
        template='plotly_dark',
        xaxis=dict(
            range=[0, 1]
        )
    )

    st.session_state['fig_entreprise_vs_clients'] = fig  # Stocker dans l'état après la création
    #st.plotly_chart(fig, key="entreprise_vs_clients")  # Afficher avec une clé unique
