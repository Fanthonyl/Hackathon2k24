# Hackathon2k24

# Financial Analysis Dashboard

This project is a financial analysis dashboard built using Streamlit. It provides various financial analysis tools including global financial analysis, fundamental analysis, technical analysis, sentiment analysis, a board view, and a pricer tool.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Pages](#pages)
  - [Home](#home)
  - [Analyse financière globale](#analyse-financière-globale)
  - [Analyse fondamentale](#analyse-fondamentale)
  - [Analyse technique](#analyse-technique)
  - [Analyse de Sentiments](#analyse-de-sentiments)
  - [Board](#board)
  - [Pricer](#pricer)

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the application, use the following command:
```sh
streamlit run [app.py](http://_vscodecontentref_/1)
```

## Pages

### Home
The Home page provides an overview of the application and its functionalities.

 - File: home.py
 - Function: render_home(database)

### Analyse financière globale
This page provides a global financial analysis using various financial metrics and data.

 - File: analyse_glob.py
 - Function: render_analyse_glob()

### Analyse fondamentale
The fundamental analysis page offers insights into the fundamental aspects of financial data.

 - File: analyse_fond.py
 - Function: render_analyse_fond(database)

### Analyse technique
The technical analysis page provides tools for analyzing financial data using technical indicators.

 - File: analyse_tech.py
 - Function: render_analyse_tech(sectors_from_db)

### Analyse de Sentiments
This page analyzes the sentiment of financial news and data.

 - File: sentiment.py
 - Function: render_sentiment(database)

### Board
The board page offers a dashboard view of various financial metrics and data.

 - File: board.py
 - Function: render_board(database)

### Pricer
The pricer tool helps in pricing financial instruments based on various parameters.

 - File: pricer.py
 - Function: render_pricer(database)

### License
This project is licensed under the MIT License. See the LICENSE file for details.


This [README.md](http://_vscodecontentref_/2) provides a detailed overview of the application, its installation, usage, and the functionalities of each page.