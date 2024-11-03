import streamlit as st
import pandas as pd
import yfinance as yf

def render_home():
    

    # Function to get financial data from Yahoo Finance
    def get_financial_data(ticker):
        stock = yf.Ticker(ticker)
        info = stock.info
        one_month_return = ((info['currentPrice'] / info['twoHundredDayAverage']) - 1) * 100 if 'currentPrice' in info and 'twoHundredDayAverage' in info else None
        six_month_return = ((info['currentPrice'] / info['fiftyDayAverage']) - 1) * 100 if 'currentPrice' in info and 'fiftyDayAverage' in info else None
        one_year_return = ((info['currentPrice'] / info['regularMarketPreviousClose']) - 1) * 100 if 'currentPrice' in info and 'regularMarketPreviousClose' in info else None
        market_cap = info.get('marketCap', None)
        return one_month_return, six_month_return, one_year_return, market_cap

    # Expanded list of companies and their sectors
    data = pd.DataFrame({
        'Company': [
            'BCE Inc.', 'TELUS Corporation', 'Rogers Communications', 'Canadian National Railway',
            'Saputo Inc.', 'Nutrien Ltd.', 'Enbridge Inc.', 'Suncor Energy Inc.',
            'Barrick Gold Corp.', 'Canadian Pacific Kansas City', 'Brookfield Asset Management',
            'TC Energy Corp.', 'Manulife Financial', 'Thomson Reuters Corp.', 'Loblaw Companies Ltd.',
            'Shopify Inc.', 'Power Corporation of Canada', 'Bank of Montreal', 'Royal Bank of Canada',
            'Toronto-Dominion Bank', 'Scotiabank', 'Canadian Imperial Bank of Commerce',
            'National Bank of Canada', 'Alimentation Couche-Tard', 'Magna International',
            'Cameco Corporation', 'Bombardier Inc.', 'Kinross Gold Corp.', 'CGI Inc.',
            'Verizon Communications', 'AT&T Inc.', 'Union Pacific', 'Nestlé', 'Cargill',
            'Exxon Mobil', 'Chevron', 'Newmont Corporation', 'Deutsche Bahn', 'Goldman Sachs'
        ],
        'Sector': [
            'Telecom Services', 'Telecom Services', 'Telecom Services', 'Transportation',
            'Agro-Food', 'Agro-Food', 'Energy', 'Energy',
            'Mining', 'Transportation', 'Financials',
            'Energy', 'Financials', 'Media & Information Services', 'Retail',
            'Technology', 'Financials', 'Financials', 'Financials',
            'Financials', 'Financials', 'Financials',
            'Financials', 'Retail', 'Automotive',
            'Mining', 'Aerospace', 'Mining', 'Technology',
            'Telecom Services', 'Telecom Services', 'Transportation', 'Agro-Food', 'Agro-Food',
            'Energy', 'Energy', 'Mining', 'Transportation', 'Financials'
        ],
        'Ticker': [
            'BCE.TO', 'T.TO', 'RCI-B.TO', 'CNR.TO',
            'SAP.TO', 'NTR.TO', 'ENB.TO', 'SU.TO',
            'ABX.TO', 'CP.TO', 'BAM-A.TO',
            'TRP.TO', 'MFC.TO', 'TRI.TO', 'L.TO',
            'SHOP.TO', 'POW.TO', 'BMO.TO', 'RY.TO',
            'TD.TO', 'BNS.TO', 'CM.TO',
            'NA.TO', 'ATD-B.TO', 'MG.TO',
            'CCO.TO', 'BBD-B.TO', 'K.TO', 'GIB-A.TO',
            'VZ', 'T', 'UNP', 'NSRGY', 'Private',
            'XOM', 'CVX', 'NEM', 'DB', 'GS'
        ]
    })

    # Extract returns and Market Cap for each company
    data[['1-Month Return', '6-Month Return', '1-Year Return', 'Market Cap (CAD)']] = data['Ticker'].apply(
        lambda x: pd.Series(get_financial_data(x))
    )

    # Streamlit app layout
    st.title("Investment Analysis Dashboard: Global Sectors")
    st.subheader("Discover top companies in each sector using key performance indicators")

    # Create a dropdown list for selecting a sector
    selected_sector = st.selectbox("Select a sector to view data:", data['Sector'].unique())

    # Filter data based on the selected sector
    sector_data = data[data['Sector'] == selected_sector]

    # Display data for the selected sector
    st.header(f"Sector: {selected_sector}")

    for index, row in sector_data.iterrows():
        col2, col3, col4, col5 = st.columns([4, 4, 4, 4])

        with col2:
            st.write(f"**{row['Company']}**")

        with col3:
            arrow_1m = '⬆️' if row['1-Month Return'] and row['1-Month Return'] > 0 else '⬇️'
            color_1m = 'green' if row['1-Month Return'] and row['1-Month Return'] > 0 else 'red'
            st.markdown(f"<p style='color:{color_1m};'>{arrow_1m} 1-Month Return: {row['1-Month Return']:.2f}%</p>", unsafe_allow_html=True)

        with col4:
            arrow_6m = '⬆️' if row['6-Month Return'] and row['6-Month Return'] > 0 else '⬇️'
            color_6m = 'green' if row['6-Month Return'] and row['6-Month Return'] > 0 else 'red'
            st.markdown(f"<p style='color:{color_6m};'>{arrow_6m} 6-Month Return: {row['6-Month Return']:.2f}%</p>", unsafe_allow_html=True)

        with col5:
            arrow_1y = '⬆️' if row['1-Year Return'] and row['1-Year Return'] > 0 else '⬇️'
            color_1y = 'green' if row['1-Year Return'] and row['1-Year Return'] > 0 else 'red'
            st.markdown(f"<p style='color:{color_1y};'>{arrow_1y} 1-Year Return: {row['1-Year Return']:.2f}%</p>", unsafe_allow_html=True)

        with col5:
            market_cap_display = f"CAD {row['Market Cap (CAD)'] / 1e9:.2f}B" if row['Market Cap (CAD)'] else 'N/A'
            st.write(f"Market Cap: {market_cap_display}")

    st.caption("Data sourced from Yahoo Finance and public financial databases.")
