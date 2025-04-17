# Stock Financial Assistant

## Overview

Stock Financial Assistant is a web application designed to assist investors in making informed decisions by providing stock price predictions, technical analysis, financial suggestions, and real-time market news. The application leverages machine learning and external APIs to deliver accurate stock price forecasts and actionable insights.

## Key Features

- **Stock Price Prediction**: Utilizes Random Forest algorithm to predict future stock prices.
- **Technical Analysis**: Calculates indicators such as RSI, MACD, moving averages, and volatility.
- **Investment Suggestions**: Provides AI-generated financial suggestions using Google Gemini API.
- **Market News Integration**: Fetches and displays relevant stock news with translation to English.
- **Interactive Chatbot**: Gemini-powered chatbot for answering financial queries.
- **User Authentication**: Secure login with email verification.
- **Prediction History**: Stores user prediction history in a PostgreSQL database.
- **Interactive Visualizations**: Displays predicted vs. actual stock prices using Plotly.

## Technology Stack

### Backend
- **Python**: Core programming language for the application.
- **Flask**: Web framework for building the server-side application.
- **PostgreSQL**: Database for storing user data and prediction history.
- **Aiven**: Cloud platform for hosting PostgreSQL.
- **Psycopg2**: PostgreSQL adapter for Python.

### Machine Learning & Data
- **Scikit-learn**: Implements Random Forest regression for price predictions.
- **Pandas**: Handles data manipulation and analysis.
- **NumPy**: Supports numerical computations.
- **Alpha Vantage API**: Provides real-time stock market data.
- **Holiday API**: Checks for market holidays.

### AI & NLP
- **Google Gemini API**: Powers financial suggestions and chatbot functionality.
- **Google News API**: Fetches stock-related news.
- **Googletrans**: Translates news headlines to English.

### Frontend
- **HTML/CSS**: Provides basic structure and styling.
- **Plotly**: Enables interactive data visualizations.
- **JavaScript**: Supports interactive elements (implied by Plotly usage).

### Other Services
- **SMTP (Gmail)**: Sends email verification codes.
- **Threading**: Facilitates parallel processing for API calls.
