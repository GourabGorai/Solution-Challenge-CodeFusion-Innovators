# Stock Financial Assistant

## Overview

Stock Financial Assistant is a comprehensive web application designed to help investors make informed decisions by providing stock price predictions, financial analysis, and market news. The application combines machine learning models with real-time financial data to deliver accurate predictions and actionable insights.

## Key Features

- **Stock Price Prediction**: Uses Random Forest algorithm to forecast future stock prices
- **Technical Analysis**: Calculates various indicators like RSI, MACD, and moving averages
- **Investment Decision Support**: Provides AI-generated investment recommendations
- **Market News Integration**: Fetches and displays relevant stock news
- **Interactive Chatbot**: Gemini-powered assistant for financial queries
- **User Authentication**: Secure login with email verification
- **Prediction History**: Stores user prediction history in database

## Technology Stack

### Backend
- **Python**: Primary programming language
- **Flask**: Web framework for building the application
- **PostgreSQL**: Database for storing user data and prediction history
- **Aiven**: Cloud platform for PostgreSQL hosting
- **Psycopg2**: PostgreSQL adapter for Python

### Machine Learning & Data
- **Scikit-learn**: For Random Forest regression model
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Alpha Vantage API**: For fetching stock market data
- **Holiday API**: For checking market holidays

### AI & NLP
- **Google Gemini API**: For generating investment recommendations and chatbot functionality
- **Google News API**: For fetching relevant stock news
- **Googletrans**: For translating news headlines

### Frontend
- **HTML/CSS**: Basic structure and styling
- **Plotly**: Interactive data visualization
- **JavaScript**: For interactive elements (implied by Plotly usage)

### Other Services
- **SMTP (Gmail)**: For sending verification emails
- **Threading**: For parallel processing of API calls

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/stock-financial-assistant.git
   cd stock-financial-assistant
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with the following variables:
   ```
   FLASK_SECRET_KEY=your_secret_key_here
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
   GOOGLE_NEWS_API_KEY=your_google_news_key
   HOLIDAY_API_KEY=your_holiday_api_key
   GEMINI_API_KEY=your_gemini_key
   DATABASE_URL=your_postgres_connection_string
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_email_password
   ```

5. **Initialize database**
   Run the Flask application once to create necessary tables.

6. **Run the application**
   ```bash
   python app.py
   ```

## Usage

1. **Login/Register**: Users can register with email and password, with email verification
2. **Stock Analysis**: Enter a stock symbol to view predictions and technical indicators
3. **Future Prediction**: Select a future date to get price prediction
4. **Investment Decision**: View AI-generated investment recommendations
5. **Market News**: Read latest news about the selected stock
6. **Chatbot**: Ask financial questions related to your stock analysis

## API Keys Required

- Alpha Vantage API (for stock data)
- Google News API (for market news)
- Holiday API (for market holiday information)
- Google Gemini API (for AI recommendations and chatbot)

## Disclaimer

This application provides financial information and suggestions for educational purposes only. It should not be considered as financial advice. Users should consult with a qualified financial advisor before making any investment decisions.

## Future Enhancements

- Portfolio tracking functionality
- More advanced machine learning models
- Additional technical indicators
- Sentiment analysis of news articles
- Mobile application version

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any improvements or bug fixes.