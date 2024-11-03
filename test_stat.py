import pandas as pd
import stats_can
'''
# Specify the table ID you want to use
table_id = '36-10-0104-01'  # Example for GDP

# Load data
data = stats_can.table_to_df(table_id)

# Set display options to avoid truncation
pd.set_option('display.max_columns', None)  # Show all columns
#pd.set_option('display.max_rows', None)     # Show all rows (be careful with large DataFrames)
pd.set_option('display.width', None)        # Use the full width of the console

# Display the DataFrame
print(data.head())'''

# Import necessary libraries
import stats_can
import pandas as pd

# Dictionary to store tables with relevant economic indicators
table_ids = {
    'GDP': '36-10-0104-01',           # Real GDP by expenditure
    'Inflation': '18-10-0004-01',      # Consumer Price Index (CPI) for Canada
    'Interest Rate': '10-10-0122-01',  # Bank of Canada key interest rate
    'Consumer Spending': '36-10-0101-01'  # Household final consumption expenditure
}
'''
# Function to load data and save to CSV
def save_data_to_csv(table_id, filename):
    # Load data from stats_can
    df = stats_can.table_to_df(table_id)
    # Clean the data (optional, depending on your needs)
    df = df.tail()
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Iterate through the table_ids and save each to CSV
for indicator, table_id in table_ids.items():
    filename = f"{indicator.replace(' ', '_')}.csv"  # Create a filename based on the indicator
    save_data_to_csv(table_id, filename)'''
'''
# Import necessary libraries
import stats_can
import pandas as pd

# Dictionary to store tables with relevant economic indicators
table_ids = {
    'GDP': '36-10-0104-01',           # Real GDP by expenditure
    'Inflation': '18-10-0004-01',      # Consumer Price Index (CPI) for Canada
    'Interest Rate': '10-10-0122-01',  # Bank of Canada key interest rate
    'Consumer Spending': '36-10-0101-01'  # Household final consumption expenditure
}

# Function to load data and display unique values in categorical columns
def display_unique_values(table_id, indicator_name):
    # Load data from stats_can
    df = stats_can.table_to_df(table_id)
    # Drop any null values (optional, based on your needs)
    #df = df.dropna()
    
    print(f"\nUnique values in categorical columns for {indicator_name} ({table_id}):")
    
    # Loop through each column to check for categorical columns and display unique values
    for column in df.columns:
        # If the column's data type is object or category, it is likely categorical
        if df[column].dtype == 'object' or pd.api.types.is_categorical_dtype(df[column]):
            unique_values = df[column].unique()
            print(f"Column '{column}' has {len(unique_values)} unique values:")
            print(unique_values)

# Iterate through each table and display unique values for categorical columns
for indicator, table_id in table_ids.items():
    display_unique_values(table_id, indicator)
'''

import yfinance as yf

# Choisissez une entreprise pour l'exemple
ticker = "AAPL"  # Exemple avec Apple

# Récupérer les données de l'entreprise
stock = yf.Ticker(ticker)

# Récupérer les données trimestrielles de l'actif total et du revenu net
balance_sheet = stock.quarterly_balance_sheet  # Actifs totaux
income_statement = stock.quarterly_financials  # Revenu net

# Afficher le tableau des actifs totaux et du revenu net pour calculer le ROA
print("Actifs totaux trimestriels (Total Assets):")
print(balance_sheet.loc["Total Assets"])

print("\nRevenu net trimestriel (Net Income):")
print(income_statement.loc["Net Income"])

# Exemple de calcul pour le ROA
roa = (income_statement.loc["Net Income"] / balance_sheet.loc["Total Assets"]) * 100
print("\nROA trimestriel (%):")
print(roa)


