import streamlit as st 

# Configurer la page pour un affichage large
st.set_page_config(page_title="Analyse des valeurs", layout="wide")

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
    # Énergie
    {'nom': 'Suncor Energy', 'ticker': 'SU.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Enbridge', 'ticker': 'ENB.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'TC Energy', 'ticker': 'TRP.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Cenovus Energy', 'ticker': 'CVE.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Canadian Natural Resources', 'ticker': 'CNQ.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Pembina Pipeline', 'ticker': 'PPL.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'Gibson Energy', 'ticker': 'GEI.TO', 'domaine': 'Énergie', 'suivi': False},
    {'nom': 'AltaGas', 'ticker': 'ALA.TO', 'domaine': 'Énergie', 'suivi': False},
    # Services publics
    {'nom': 'Fortis', 'ticker': 'FTS.TO', 'domaine': 'Services publics', 'suivi': False},
    {'nom': 'Hydro One', 'ticker': 'H.TO', 'domaine': 'Services publics', 'suivi': False},
    # Télécommunications
    {'nom': 'Cogeco', 'ticker': 'CGO.TO', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Quebecor', 'ticker': 'QBR-B.TO', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Rogers', 'ticker': 'RCI-B.TO', 'domaine': 'Télécommunications', 'suivi': False},
    {'nom': 'Telus', 'ticker': 'T.TO', 'domaine': 'Télécommunications', 'suivi': False},
    # Technologie
    {'nom': 'Shopify', 'ticker': 'SHOP.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Constellation Software', 'ticker': 'CSU.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'BlackBerry', 'ticker': 'BB.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Lightspeed', 'ticker': 'LSPD.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Dye & Durham', 'ticker': 'DND.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Kinaxis', 'ticker': 'KXS.TO', 'domaine': 'Technologie', 'suivi': False},
    {'nom': 'Enghouse Systems', 'ticker': 'ENGH.TO', 'domaine': 'Technologie', 'suivi': False}
    ]

# Extraire les domaines et les entreprises correspondantes
sectors_from_db = {domaine: [entry['ticker'] for entry in database if entry['domaine'] == domaine] for domaine in set(entry['domaine'] for entry in database)}

# Navigation bar with fixed pages
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Pricer", "Sentiment", "Analyse financière globale au Canada", "Analyse fondamentale", "Analyse technique", "Board"])

# Passer les variables globales aux fonctions de rendu des pages
if page == "Home":
    from home import render_home
    render_home(database)

elif page == "Analyse de Sentiments":
    from sentiment import render_sentiment
    render_sentiment(database)
    
elif page == "Analyse financière globale au Canada":
    from analyse_glob import render_analyse_glob
    render_analyse_glob()

elif page == "Analyse fondamentale":
    from analyse_fond import render_analyse_fond
    render_analyse_fond(database)

elif page == "Analyse technique":
    from analyse_tech import render_analyse_tech
    render_analyse_tech(sectors_from_db) 

elif page == "Board":
    from board import render_board
    render_board()

elif page == "Pricer":
    from pricer import render_pricer
    render_pricer()