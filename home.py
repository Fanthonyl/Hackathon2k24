import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
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

def render_home(database):
   

    st.title("Analyse des valeurs moyennes des actions par secteur au Canada")

    col1, col2 = st.columns([10, 1])
    with col2:
        time_span = st.selectbox(
            "# Période:",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
            index=3
        )

    def get_data():
        data = {}
        for action in database:
            try:
                df = yf.download(action['ticker'], period=time_span)["Adj Close"]
                data[action['domaine']] = data.get(action['domaine'], []) + [df]
            except Exception as e:
                pass
        return data
    with col1:

        # Show a spinner while loading the data and generating the plot
        with st.spinner("Chargement des données et génération du graphique..."):
            data = get_data()
            sector_averages = {}
            for secteur, valeurs in data.items():
                combined_df = pd.concat(valeurs, axis=1).mean(axis=1)
                sector_averages[secteur] = combined_df

            df_plot = pd.DataFrame(sector_averages)
            df_plot.reset_index(inplace=True)
            df_plot.rename(columns={"index": "Date"}, inplace=True)

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            for col in df_plot.columns[1:]:
                if col != "Technologie":
                    fig.add_trace(
                        go.Scatter(x=df_plot['Date'], y=df_plot[col], name=col),
                        secondary_y=False
                    )
            fig.add_trace(
                go.Scatter(x=df_plot['Date'], y=df_plot['Technologie'], name='Technologie', line=dict(color='red')),
                secondary_y=True
            )

            fig.update_layout(
                title="Évolution moyenne des valeurs des actions par secteur au Canada",
                xaxis_title="Date",
                legend_title_text='Secteur'
            )
            fig.update_yaxes(title_text="Prix moyen ($CAD)", secondary_y=False)
            fig.update_yaxes(title_text="Prix moyen ($CAD) - Technologie", secondary_y=True)
            st.plotly_chart(fig)
            # Function to calculate percentage change for each sector

    def calculate_metrics(df):
        metrics = {}
        for col in df.columns[1:]:  # Skip the 'Date' column
            start_value = df[col].iloc[0]
            end_value = df[col].iloc[-1]
            if start_value != 0:
                change = ((end_value - start_value) / start_value) * 100
            else:
                change = 0  # Handle division by zero
            metrics[col] = change
        return metrics

    # Calculate metrics for each sector
    metrics = calculate_metrics(df_plot)

    # Display the metrics as columns
    st.subheader("Variation par secteur (en CAD)")
    metric_columns = st.columns(len(metrics))

    for i, (sector, change) in enumerate(metrics.items()):
        metric_columns[i].metric(
            label=sector,
            value=f"{df_plot[sector].iloc[-1]:.2f} $",
            delta=f"{change:.2f}%"
        )


    # Downsample data only for the LLM prompt
    def get_downsampled_prompt(df, max_points=30):
        downsampled_data = []
        for col in df.columns[1:]:
            series = df[['Date', col]].dropna()
            if len(series) > max_points:
                n = len(series) // max_points
                series = series.iloc[::n]  # Keep every nth row
            downsampled_data.append((col, series))
        return downsampled_data

    # Create prompt text with downsampled data
    prompt = "Analyse the following stock performance trends:\n\n"
    downsampled_data = get_downsampled_prompt(df_plot)
    for col, series in downsampled_data:
        trend_data = series.to_string(index=False)
        prompt += f"Secteur: {col}\n{trend_data}\n\n"

    session_id = str(uuid.uuid1())
    st.subheader("Financial Analysis Insights")
    
    # Show a spinner while waiting for the insights
    with st.spinner("Génération des insights financiers..."):
        try:
            insights = bedrock_wrapper.invoke_agent(agent_id, agent_alias_id, session_id, prompt)
            st.write(insights)
        except Exception as e:
            st.error("Erreur lors de l'obtention des insights financiers.")
            logger.error(f"Erreur: {e}")

