import streamlit as st
import stats_can
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
            df_annual = df['VALUE'].resample('Y').mean()
            df_annual_change = df_annual.pct_change() * 100
            df_annual_change = df_annual_change.reset_index()
            df_annual_change.columns = ['Year', 'Annual Variation (%)']
            return df_annual_change
        else:
            # Ensure 'VALUE' is numeric before resampling
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

    # Rename REF_DATE to Year before merging
    consumer_spending_data.rename(columns={'Annual Variation (%)': 'Consumer Spending Annual Variation (%)'}, inplace=True)
    interest_rate_data.rename(columns={'Annual Variation (%)': 'Interest Rate Annual Variation (%)'}, inplace=True)
    gdp_data.rename(columns={'VALUE': 'GDP Annual Variation (%)'}, inplace=True)
    inflation_data.rename(columns={'Annual Variation (%)': 'Inflation Annual Variation (%)'}, inplace=True)

    # Merge datasets into a single summarized table
    summary_df = consumer_spending_data.merge(
        interest_rate_data, on='Year', how='outer'
    ).merge(
        gdp_data, on='Year', how='outer'
    ).merge(
        inflation_data, on='Year', how='outer'
    )

    # Convert 'Year' from datetime to just the year as a string
    summary_df['Year'] = summary_df['Year'].dt.year.astype(str).str.strip()
    summary_df.set_index('Year', inplace=True)

    # Display the summarized table below the graphs
    st.subheader("Summary of Annual Variations")
    st.write(summary_df)

    # Create subplots for Consumer Spending, GDP, Inflation and Interest Rate with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add Consumer Spending Annual Variation
    fig.add_trace(
        go.Scatter(x=consumer_spending_data['Year'], 
                   y=consumer_spending_data['Consumer Spending Annual Variation (%)'], 
                   name="Consumer Spending Annual Variation (%)"),
        secondary_y=False
    )

    # Add GDP Annual Variation
    fig.add_trace(
        go.Scatter(x=gdp_data['Year'], 
                   y=gdp_data['GDP Annual Variation (%)'], 
                   name="GDP Annual Variation (%)"),
        secondary_y=False
    )

    # Add Inflation Annual Variation
    fig.add_trace(
        go.Scatter(x=inflation_data['Year'], 
                   y=inflation_data['Inflation Annual Variation (%)'], 
                   name="Inflation Annual Variation (%)"),
        secondary_y=False
    )

    # Add Interest Rate Annual Variation to secondary y-axis
    fig.add_trace(
        go.Scatter(x=interest_rate_data['Year'], 
                   y=interest_rate_data['Interest Rate Annual Variation (%)'], 
                   name="Interest Rate Annual Variation (%)"),
        secondary_y=True
    )

    # Update layout for better visuals
    fig.update_layout(
        title="Annual Variations for Key Indicators",
        xaxis_title="Year",
        yaxis_title="Annual Variation (%)",
        yaxis2_title="Interest Rate (%)",
        legend_title="Indicators",
        template="plotly_white"
    )

    # Show the combined plot with separate y-axes
    st.plotly_chart(fig)

    # Set up a two-column layout
    col1, col2 = st.columns(2)

    # Display Consumer Spending Annual Variation
    with col1:
        fig1 = px.line(
            consumer_spending_data, 
            x='Year', 
            y='Consumer Spending Annual Variation (%)', 
            title="Annual Variation in Consumer Spending",
            labels={"Year": "Year"}  # Rename x-axis to "Year"
        )
        st.plotly_chart(fig1)

    # Display Interest Rate Annual Variation (this can be removed if you already show it in the summary)
    with col2:
        fig2 = px.line(
            interest_rate_data, 
            x='Year', 
            y='Interest Rate Annual Variation (%)', 
            title="Annual Variation in Bank Rate",
            labels={"Year": "Year"}  # Rename x-axis to "Year"
        )
        st.plotly_chart(fig2)

    # New row for GDP and Inflation
    col3, col4 = st.columns(2)

    # Display GDP with renamed y-axis label and x-axis label
    with col3:
        fig3 = px.line(
            gdp_data, 
            x='Year', 
            y='GDP Annual Variation (%)', 
            title="Annual Variation in GDP at Market Prices",
            labels={"Year": "Year", "GDP Annual Variation (%)": "Annual Variation (%)"}  # Rename both axes
        )
        st.plotly_chart(fig3)

    # Display Inflation Annual Variation
    with col4:
        fig4 = px.line(
            inflation_data, 
            x='Year', 
            y='Inflation Annual Variation (%)', 
            title="Annual Variation in Inflation",
            labels={"Year": "Year"}  # Rename x-axis to "Year"
        )
        st.plotly_chart(fig4)

    # Additional information or explanations for the dashboard
    st.markdown("""
    This dashboard presents key financial indicators for Canada from 2014 to the present, with selected filters applied.
    The annual variations in Consumer Spending, Interest Rate, and Inflation provide insights into year-over-year changes, 
    while the GDP plot presents absolute values. 
    """)

