import streamlit as st 

# Configurer la page pour un affichage large
st.set_page_config(page_title="AlexIA", page_icon="alexia2.png", layout="wide")

# Configurer les pages pour la navigation
pages = {
    "Home": [st.Page("home.py", title="Home")],
    "Outils d'Analyse": [
        st.Page("analyse_glob.py", title="Analyse financière globale (Canada)"),
        st.Page("analyse_fond.py", title="Analyse fondamentale"),
        st.Page("analyse_tech.py", title="Analyse technique"),
        st.Page("sentiment.py", title="Analyse de Sentiments")
    ],
    "Board": [st.Page("board.py", title="Board")],
    "Gestionnaire de portefeuille": [st.Page("pricer.py", title="Optimisation du portefeuille")]
}

pg = st.navigation(pages)

# Logo dans la sidebar
st.sidebar.image('alexia.png', use_column_width=True)

# Le titre de la sidebar, centré
st.sidebar.markdown(
    """
    <style>
    .sidebar-title {
        text-align: center;
        color: white;
        font-size: 15px !important; /* Assure que la taille de la police est appliquée */
        margin: 0;
        padding: 0;
        width: 100%;
    }
    </style>
    <h1 class='sidebar-title'>La voix des marchés financiers</h1>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("\n\n")
st.sidebar.markdown("\n\n")

# Lancer la navigation
pg.run()
