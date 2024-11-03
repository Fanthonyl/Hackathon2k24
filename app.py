import streamlit as st

# Set up the dashboard layout for Streamlit
st.set_page_config(page_title="Analyse financière globale au Canada", layout="wide")

# Add a page selector
page = st.sidebar.selectbox("Select Page", ["Home", "Analyse financière globale au Canada","Analyse fondamentale","Analyse technique"])

if page == "Home":
    from home import render_home  # Importing the home page function
    render_home()  # Call the function to render the home page
    
elif page == "Analyse financière globale au Canada":
    from analyse_glob import render_analyse_glob  # Importing the financial analysis page function
    render_analyse_glob()  # Call the function to render the financial analysis page

elif page == "Analyse fondamentale":
    from analyse_fond import render_analyse_fond  # Importing the financial analysis page function
    render_analyse_fond()  # Call the function to render the financial analysis page

elif page == "Analyse technique":
    from analyse_tech import render_analyse_tech  # Importing the financial analysis page
    render_analyse_tech()  # Call the function to render the financial analysis page

    