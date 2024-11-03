import streamlit as st 

database = [ 
    # Agroalimentaire
    {'nom': 'Saputo', 'ticker': 'SAP.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Alimentation Couche-Tard', 'ticker': 'ATD.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Loblaw', 'ticker': 'L.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Maple Leaf Foods', 'ticker': 'MFI.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Empire Company', 'ticker': 'EMP-A.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'Premium Brands', 'ticker': 'PBH.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    {'nom': 'North West Company', 'ticker': 'NWC.TO', 'domaine': 'Agroalimentaire', 'suivi': False},
    # Transport
    {'nom': 'Canadian National Railway', 'ticker': 'CNR.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Canadian Pacific Kansas City', 'ticker': 'CP.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'TFI International', 'ticker': 'TFII.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Westshore Terminals', 'ticker': 'WTE.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'CAE Inc.', 'ticker': 'CAE.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Air Canada', 'ticker': 'AC.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'Student Transportation', 'ticker': 'STB.TO', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'CPKC', 'ticker': 'N/A', 'domaine': 'Transport', 'suivi': False},
    {'nom': 'CN', 'ticker': 'N/A', 'domaine': 'Transport', 'suivi': False},
    # Énergie
    {'nom': 'Suncor Energy', 'ticker': 'SU.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Enbridge', 'ticker': 'ENB.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'TC Energy', 'ticker': 'TRP.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Cenovus Energy', 'ticker': 'CVE.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Canadian Natural Resources', 'ticker': 'CNQ.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Pembina Pipeline', 'ticker': 'PPL.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Gibson Energy', 'ticker': 'GEI.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'AltaGas', 'ticker': 'N/A', 'domaine': 'Énergie', 'suivi': False},
    # Services publics
    {'nom': 'Fortis', 'ticker': 'N/A', 'domaine': 'Services publics', 'suivi': False},
    {'nom': 'Hydro One', 'ticker': 'N/A', 'domaine': 'Services publics', 'suivi': False},
    # Télécommunications
    {'nom': 'Cogeco', 'ticker': 'N/A', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Quebecor', 'ticker': 'N/A', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Rogers', 'ticker': 'N/A', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Telus', 'ticker': 'N/A', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Bell Canada', 'ticker': 'N/A', 'domaine': 'Télécommunications', 'suivi': False}
]

# Extraire les domaines et les entreprises correspondantes
sectors_from_db = {domaine: [entry['ticker'] for entry in database if entry['domaine'] == domaine] for domaine in set(entry['domaine'] for entry in database)}

# Sélection du secteur et des entreprises
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Home", "Analyse financière globale au Canada", "Analyse fondamentale", "Analyse technique"])

# Liste des pages où certains widgets doivent être désactivés
pages_disabled_tickers_periode = ["Home", "Analyse financière globale au Canada"]
pages_disabled_secteur = ["Analyse financière globale au Canada"]

# Vérifier si la page actuelle est dans la liste des pages désactivées
disabled_tickers_periode = page in pages_disabled_tickers_periode
disabled_secteur = page in pages_disabled_secteur

# Initialiser les valeurs par défaut dans st.session_state
if 'secteur' not in st.session_state:
    st.session_state['secteur'] = list(sectors_from_db.keys())[0]  # Valeur par défaut du secteur
if 'tickers' not in st.session_state:
    st.session_state['tickers'] = [sectors_from_db[st.session_state['secteur']][0]]  # Par défaut, la première entreprise
if 'periode' not in st.session_state:
    st.session_state['periode'] = "1mo"  # Période par défaut

# Choix du secteur
secteur = st.sidebar.selectbox(
    "Choisir un secteur canadien :",
    list(sectors_from_db.keys()),
    index=list(sectors_from_db.keys()).index(st.session_state['secteur']),
    disabled=disabled_secteur,  # Utiliser la condition spécifique pour la désactivation
    on_change=lambda: st.session_state.update({'secteur': secteur})
)

# Ajuster la liste par défaut pour s'assurer qu'elle est incluse dans les options disponibles
defaut_tickers = [ticker for ticker in st.session_state['tickers'] if ticker in sectors_from_db[secteur]]
if not defaut_tickers:  # Si aucun ticker par défaut ne correspond
    defaut_tickers = [sectors_from_db[secteur][0]]  # Sélectionner le premier ticker disponible

# Affichage dynamique des entreprises en fonction du secteur sélectionné
tickers = st.sidebar.multiselect(
    "Choisissez de 1 à 3 entreprises (sigles financiers)",
    sectors_from_db[secteur],
    default=defaut_tickers,
    max_selections=3,
    disabled=disabled_tickers_periode,  # Utiliser la condition pour les autres widgets
    on_change=lambda: st.session_state.update({'tickers': tickers})
)

# Sélection de la période
periode = st.sidebar.selectbox(
    "Sélectionnez la période",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
    index=["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"].index(st.session_state['periode']),
    disabled=disabled_tickers_periode,  # Utiliser la condition pour les autres widgets
    on_change=lambda: st.session_state.update({'periode': periode})
)

# Mettre à jour les valeurs de st.session_state après chaque sélection
st.session_state['secteur'] = secteur
st.session_state['tickers'] = tickers

# Passer les variables globales aux fonctions de rendu des pages
if page == "Home":
    from home import render_home
    render_home(database)

elif page == "Analyse financière globale au Canada":
    from analyse_glob import render_analyse_glob
    render_analyse_glob()

elif page == "Analyse fondamentale":
    from analyse_fond import render_analyse_fond
    render_analyse_fond(tickers, periode)

elif page == "Analyse technique":
    from analyse_tech import render_analyse_tech
    render_analyse_tech(tickers, periode)