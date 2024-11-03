import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta


def render_board():
    # Titre principal
    st.title("Sélecteur de KPI avec groupes")