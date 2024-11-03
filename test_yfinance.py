import yfinance as yf
import pandas as pd

# Créer un objet Ticker pour Microsoft
msft = yf.Ticker("MSFT")

# Informations générales
print("## Informations générales")
print(msft.info)