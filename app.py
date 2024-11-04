import streamlit as st 


# Configurer les pages pour la navigation
pages = {
    "Home": [st.Page("home.py", title="Home")],
    "Analyse": [
        st.Page("analyse_glob.py", title="Analyse financière globale au Canada"),
        st.Page("analyse_fond.py", title="Analyse fondamentale"),
        st.Page("analyse_tech.py", title="Analyse technique"),
        st.Page("sentiment.py", title="Analyse de Sentiments")
    ],
    "Board": [st.Page("board.py", title="Board")],
    "Pricer": [st.Page("pricer.py", title="Pricer")]
}


pg = st.navigation(pages)

# Configurer la page pour un affichage large
st.set_page_config(page_title="Analyse des valeurs", page_icon= "alexia2.png", layout="wide")

# Navigation bar with fixed pages
#Logo dans la sidebar
st.sidebar.image('alexia.png', use_column_width=True)
#le titre de la sidebar, centré
st.sidebar.markdown(
    """
    <style>
    .sidebar-title {
        text-align: center;
        color: white;
        font-size: 20px !important; /* Ensures the font size is applied */
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


pg.run()
