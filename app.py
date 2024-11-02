import streamlit as st

st.title('Application Basique avec Streamlit')
st.write('Bienvenue dans votre première application Streamlit déployée !')

# Ajoutez des éléments interactifs
name = st.text_input('Quel est votre nom ?')
if name:
    st.write(f'Bonjour, {name} !')
