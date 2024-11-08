import streamlit as st
import stats_can
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


st.title("Analyse économique (Canada)")

# Additional information or explanations
st.markdown("""**Suivez avec Alexia les tendances des principaux indicateurs économiques pour une idée globale du marché canadien de 2014 à aujourd’hui.**""")


# Function to load and filter data with optional annual variation calculation
def load_indicator_data(table_id, filters, calculate_variation=False):
    df = stats_can.table_to_df(table_id)
    for column, value in filters.items():
        df = df[df[column] == value]
    df = df[(df['REF_DATE'] >= '2014-01-01') & (df['GEO'] == 'Canada')]
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
    df.set_index('REF_DATE', inplace=True)

    # Convert VALUE to numeric, forcing errors to NaN
    df['VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce')

    if calculate_variation:
        df_annual = df['VALUE'].resample('Y').mean()
        df_annual_change = df_annual.pct_change() * 100
        df_annual_change = df_annual_change.reset_index()
        df_annual_change.columns = ['Year', 'Annual Variation (%)']
        return df_annual_change
    else:
        df_resampled = df.resample('Y')['VALUE'].mean().reset_index()
        df_resampled.columns = ['Year', 'VALUE']
        return df_resampled[['Year', 'VALUE']]

# Load data for each indicator
consumer_spending_data = load_indicator_data(
    '36-10-0101-01',
    filters={'Quintile': 'All quintiles', 'Socio-demographic characteristics': 'All households'},
    calculate_variation=True
)

interest_rate_data = load_indicator_data(
    '10-10-0122-01',
    filters={'Rates': 'Bank rate'},
    calculate_variation=True
)

gdp_data = load_indicator_data(
    '36-10-0104-01',
    filters={
        'Prices': 'Chained (2017) dollars percentage change',
        'Seasonal adjustment': 'Seasonally adjusted at annual rates',
        'Estimates': 'Gross domestic product at market prices'
    },
    calculate_variation=False
)

inflation_data = load_indicator_data(
    '18-10-0004-01',
    filters={'Products and product groups': 'All-items'},
    calculate_variation=True
)

# Rename columns for merging
consumer_spending_data.rename(columns={'Annual Variation (%)': 'Consumer Spending Annual Variation (%)'}, inplace=True)
interest_rate_data.rename(columns={'Annual Variation (%)': 'Interest Rate Annual Variation (%)'}, inplace=True)
gdp_data.rename(columns={'VALUE': 'GDP Annual Variation (%)'}, inplace=True)
inflation_data.rename(columns={'Annual Variation (%)': 'Inflation Annual Variation (%)'}, inplace=True)

# Merge datasets
summary_df = consumer_spending_data.merge(
    interest_rate_data, on='Year', how='outer'
).merge(
    gdp_data, on='Year', how='outer'
).merge(
    inflation_data, on='Year', how='outer'
)

# Convert 'Year' to string
summary_df['Year'] = summary_df['Year'].dt.year.astype(str).str.strip()
summary_df.set_index('Year', inplace=True)


# Sort DataFrame by Year in descending order
##auto 
summary_df.sort_index(ascending=False, inplace=True)

# Create combined plot with all curves
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces for all indicators
fig.add_trace(
    go.Scatter(x=consumer_spending_data['Year'], 
            y=consumer_spending_data['Consumer Spending Annual Variation (%)'], 
            name="Variation annuelle des dépenses de consommation (%)"),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=gdp_data['Year'], 
            y=gdp_data['GDP Annual Variation (%)'], 
            name="Variation annuelle du PIB (%)"),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=inflation_data['Year'], 
            y=inflation_data['Inflation Annual Variation (%)'], 
            name="Variation annuelle de l’inflation (%)"),
    secondary_y=False
)
fig.add_trace(
    go.Scatter(x=interest_rate_data['Year'], 
            y=interest_rate_data['Interest Rate Annual Variation (%)'], 
            name="Variation annuelle du taux directeur (%)"),
    secondary_y=True
)

# Update layout
fig.update_layout(
    xaxis_title="Année",
    yaxis_title="Variation annuelle (%)",
    yaxis2_title="Taux d\'intérêt (%)",
    title="Évolution des Indicateurs Économiques",
    legend_title="Indicateurs",
    template="plotly_white",
    legend=dict(font=dict(size=15)),  
)

# Display the combined plot
st.plotly_chart(fig)

# Button to display detailed table
if st.button("Afficher la table de données"):
    st.subheader("Tableau des indicateurs financiers")
    st.dataframe(summary_df, use_container_width=True)