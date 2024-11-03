import streamlit as st 

# Dictionnaire des secteurs et entreprises correspondantes
sectors = {
    'Agroalimentaire': ['SAP.TO', 'ATD.TO', 'L.TO', 'MFI.TO', 'EMP-A.TO', 'PBH.TO', 'NWC.TO'],
    'Transport': ['CNR.TO', 'CP.TO', 'TFII.TO', 'WTE.TO', 'CAE.TO', 'AC.TO', 'STB.TO'],
    'Finance': ['RY.TO', 'TD.TO', 'BNS.TO', 'BMO.TO', 'CM.TO', 'NA.TO', 'MFC.TO'],
    'Technologie': ['SHOP.TO', 'CSU.TO', 'BB.TO', 'LSPD.TO', 'DND.TO', 'KXS.TO', 'ENGH.TO'],
    'Énergie': ['SU.TO', 'ENB.TO', 'TRP.TO', 'CVE.TO', 'CNQ.TO', 'PPL.TO', 'GEI.TO'],
    'Santé': ['GUD.TO', 'CXR.TO', 'NHC.TO', 'PFE.TO', 'ABBV.TO', 'MRK.TO'],
    'Immobilier': ['REI-UN.TO', 'CAR-UN.TO', 'HR-UN.TO', 'AP-UN.TO', 'DIR-UN.TO']
}

# Sélection du secteur et des entreprises
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Home", "Analyse financière globale au Canada", "Analyse fondamentale", "Analyse technique"])

# Liste des pages où les widgets doivent être désactivés
pages_disabled = ["Home", "Analyse financière globale au Canada"]

# Vérifier si la page actuelle est dans la liste des pages désactivées
disabled = page in pages_disabled

# Initialiser les valeurs par défaut dans st.session_state
if 'secteur' not in st.session_state:
    st.session_state['secteur'] = list(sectors.keys())[0]  # Valeur par défaut du secteur
if 'tickers' not in st.session_state:
    st.session_state['tickers'] = [sectors[st.session_state['secteur']][0]]  # Par défaut, la première entreprise
if 'periode' not in st.session_state:
    st.session_state['periode'] = "1mo"  # Période par défaut

# Choix du secteur
secteur = st.sidebar.selectbox(
    "Choisir un secteur canadien :",
    list(sectors.keys()),
    index=list(sectors.keys()).index(st.session_state['secteur']),
    disabled=disabled,
    on_change=lambda: st.session_state.update({'secteur': secteur})
)

# Ajuster la liste par défaut pour s'assurer qu'elle est incluse dans les options disponibles
defaut_tickers = [ticker for ticker in st.session_state['tickers'] if ticker in sectors[secteur]]
if not defaut_tickers:  # Si aucun ticker par défaut ne correspond
    defaut_tickers = [sectors[secteur][0]]  # Sélectionner le premier ticker disponible

# Affichage dynamique des entreprises en fonction du secteur sélectionné
tickers = st.sidebar.multiselect(
    "Choisissez de 1 à 3 entreprises (sigles financiers)",
    sectors[secteur],
    default=defaut_tickers,
    max_selections=3,
    disabled=disabled,
    on_change=lambda: st.session_state.update({'tickers': tickers})
)

# Sélection de la période
periode = st.sidebar.selectbox(
    "Sélectionnez la période",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    index=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"].index(st.session_state['periode']),
    disabled=disabled,
    on_change=lambda: st.session_state.update({'periode': periode})
)

# Mettre à jour les valeurs de st.session_state après chaque sélection
st.session_state['secteur'] = secteur
st.session_state['tickers'] = tickers

# Passer les variables globales aux fonctions de rendu des pages
if page == "Home":
    from home import render_home
    render_home()

elif page == "Analyse financière globale au Canada":
    from analyse_glob import render_analyse_glob
    render_analyse_glob()

elif page == "Analyse fondamentale":
    from analyse_fond import render_analyse_fond
    render_analyse_fond(tickers, periode)

elif page == "Analyse technique":
    from analyse_tech import render_analyse_tech
    render_analyse_tech(tickers, periode)
