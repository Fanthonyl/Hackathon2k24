import streamlit as st
import stats_can
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import boto3
import uuid
import logging
from botocore.exceptions import ClientError

# Initialize Bedrock client and agent wrapper
logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockAgentRuntimeWrapper:
    """Encapsulates Amazon Bedrock Agents Runtime actions."""

    def __init__(self, runtime_client):
        self.agents_runtime_client = runtime_client

    def invoke_agent(self, agent_id, agent_alias_id, session_id, prompt):
        try:
            response = self.agents_runtime_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=prompt,
            )
            completion = ""
            for event in response.get("completion"):
                chunk = event["chunk"]
                completion += chunk["bytes"].decode() + "\n"
            return completion
        except ClientError as e:
            logger.error(f"Couldn't invoke agent. {e}")
            raise

# Bedrock client and wrapper instance
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
bedrock_wrapper = BedrockAgentRuntimeWrapper(bedrock_agent_runtime_client)
agent_id = 'ACVSW7ULXC'
agent_alias_id = 'FGVZUPEISZ'

def render_analyse_glob():
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
            df_annual = df['VALUE'].resample('YE').mean()
            df_annual_change = df_annual.pct_change() * 100
            df_annual_change = df_annual_change.reset_index()
            df_annual_change.columns = ['Year', 'Annual Variation (%)']
            return df_annual_change
        else:
            df_resampled = df.resample('YE')['VALUE'].mean().reset_index()
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
    summary_df.sort_index(ascending=False, inplace=True)

    # Create combined plot with all curves
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces for all indicators
    fig.add_trace(
        go.Scatter(x=consumer_spending_data['Year'], 
                y=consumer_spending_data['Consumer Spending Annual Variation (%)'], 
                name="Consumer Spending Annual Variation (%)"),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=gdp_data['Year'], 
                y=gdp_data['GDP Annual Variation (%)'], 
                name="GDP Annual Variation (%)"),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=inflation_data['Year'], 
                y=inflation_data['Inflation Annual Variation (%)'], 
                name="Inflation Annual Variation (%)"),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=interest_rate_data['Year'], 
                y=interest_rate_data['Interest Rate Annual Variation (%)'], 
                name="Interest Rate Annual Variation (%)"),
        secondary_y=True
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Année",
        yaxis_title="Variation annuelle (%)",
        yaxis2_title="Taux d\'intérêt (%)",
        legend_title="Indicateurs",
        template="plotly_white"
    )

    st.title("Analyse sectorielle des actions au Canada")
    st.markdown("""
    Visualisez avec Alexia les principaux indicateurs financiers pour le Canada de 2014 à aujourd’hui, en termes de variations annuelles.
    """)
    
    # Display the combined plot
    st.plotly_chart(fig)

    # Generate and display summary using AWS agent
    session_id = str(uuid.uuid1())
    prompt = f"Analyser les variations des indicateurs financiers pour le Canada de 2014 à aujourd'hui."
    prompt += f"\n\n{summary_df.to_markdown()}"

    # Button to display detailed table
    if st.button("Afficher la table de données"):
        st.subheader("Tableau des indicateurs financiers")
        st.dataframe(summary_df)

    with st.spinner("AlexIA réfléchit profondément..."):
        try:
            summary_text = bedrock_wrapper.invoke_agent(agent_id, agent_alias_id, session_id, prompt)
            st.subheader("Résumé des variations des indicateurs")
            st.markdown(summary_text)
        except Exception as e:
            st.error("Erreur lors de l'obtention de l'analyse.")
            logger.error(f"Erreur: {e}")


