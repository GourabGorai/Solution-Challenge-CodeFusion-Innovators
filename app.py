from flask import Flask, render_template, request, redirect, url_for, session
import random
import smtplib
import ssl
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pandas as pd
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import plotly.express as px
import plotly.io as pio
import numpy as np
from test import make_investment_decision
from test import fetch_stock_news
from test import chat_with_gemini
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['DEBUG'] = True
GOOGLE_NEWS_API_KEY = '93888de4c8d749d3ac4fc66b360b3c38'  # Define as a constant
API_KEY = 'LZIWKUHDC0XBETMU'
STOCK_BASE_URL = 'https://www.alphavantage.co/query'
HOLIDAY_API_KEY = '49339829-1b08-49a6-b341-72f937bb885f'
HOLIDAY_API_URL = 'https://holidayapi.com/v1/holidays'


def format_investment_decision(text):
    # Convert **text** to <h2>text</h2>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    
    # Convert * **text** to bullet points with bold text
    text = re.sub(r'\*\s\*\*([^*]+)\*\*', r'<li><b>\1</b></li>', text)
    
    # Convert sections with colons (e.g., "Positive:") into <h2> headers
    text = re.sub(r'(^|\n)([A-Za-z ]+):', r'\1<h2>\2</h2>', text)
    
    # Convert hyphen-based bullet points to proper HTML list format
    text = re.sub(r'(?m)^- (.*)', r'<li>\1</li>', text)
    
    # Wrap bullet points in <ul> tags
    text = re.sub(r'(<li>.*?</li>)+', lambda m: f"<ul>{m.group(0)}</ul>", text, flags=re.S)
    
    # Convert new lines to <br> for proper spacing in HTML
    text = text.replace("\n", "<br>")
    
    return text

def is_holiday(date, country='US'):
    params = {
        'key': HOLIDAY_API_KEY,
        'country': country,
        'year': date.year,
        'month': date.month,
        'day': date.day,
    }
    response = requests.get(HOLIDAY_API_URL, params=params)
    holidays = response.json().get('holidays', [])
    return len(holidays) > 0

def get_db_connection():
    conn = psycopg2.connect(
        "postgres://avnadmin:AVNS_HjYF1YDB0ilME5gCWBC@pg-2ff69ed5-gourabg30march-ae98.l.aivencloud.com:28031/defaultdb?sslmode=require"
    )
    return conn



def send_email(recipient_email, verification_code):
    sender_email = "gourabtest469@gmail.com"
    sender_password = "geslhgvynzwwqrsb"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Verification Code"
    message["From"] = sender_email
    message["To"] = recipient_email

    text = f"Your verification code is: {verification_code}"
    part = MIMEText(text, "plain")
    message.attach(part)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Verification code sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    df.loc[:, 'EMA_fast'] = df['Close'].ewm(span=fast_period, adjust=False).mean()
    df.loc[:, 'EMA_slow'] = df['Close'].ewm(span=slow_period, adjust=False).mean()
    df.loc[:, 'MACD'] = df['EMA_fast'] - df['EMA_slow']
    df.loc[:, 'MACD_signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
    return df

def add_technical_indicators(df):
    df.loc[:, 'MA_5'] = df['Close'].rolling(window=5).mean()
    df.loc[:, 'MA_10'] = df['Close'].rolling(window=10).mean()
    df.loc[:, 'MA_50'] = df['Close'].rolling(window=50).mean()
    df.loc[:, 'Volatility'] = df['High'] - df['Low']
    df.loc[:, 'RSI'] = calculate_rsi(df)
    df = calculate_macd(df)
    df.fillna(0, inplace=True)
    return df

def train_random_forest(df):
    df = add_technical_indicators(df)

    # Features and target variable
    X = df[['Close', 'MA_5', 'MA_10', 'MA_50', 'Volatility', 'RSI', 'MACD', 'MACD_signal']]
    y = df['Close'].shift(-1)  # Predict the next day's closing price

    # Remove the last row with NaN target
    X = X[:-1]
    y = y[:-1]

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model, scaler

def fetch_stock_data(symbol):
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'full',
        'apikey': API_KEY
    }

    response = requests.get(STOCK_BASE_URL, params=params)
    data = response.json()

    if 'Time Series (Daily)' in data:
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)

        return df

    return None

def plot_prices(dates, predicted_prices, actual_prices):
    fig = px.line(
        x=dates,
        y=[predicted_prices, actual_prices],
        labels={'x': 'Date', 'y': 'Price'}
    )
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        title='Stock Prices: Predicted vs Actual',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    fig.data[0].name = 'Predicted Prices'
    fig.data[1].name = 'Actual Prices'

    hover_template = "<b>Date:</b> %{x}<br><b>Price:</b> %{y}"
    for trace in fig.data:
        trace.hovertemplate = hover_template

    plot_filename = 'static/plot.html'
    pio.write_html(fig, file=plot_filename, auto_open=False)

    return plot_filename

def create_stockhistory_table_if_not_exists():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS stockhistory (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255),
            stock_symbol VARCHAR(10),
            prediction_date DATE,
            prediction_timestamp TIMESTAMP,
            predicted_value FLOAT
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

def add_timestamp_column_if_missing():
    create_stockhistory_table_if_not_exists()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stockhistory' AND column_name='prediction_timestamp';
    """)
    column_exists = cur.fetchone()

    if not column_exists:
        cur.execute("""
            ALTER TABLE stockhistory 
            ADD COLUMN prediction_timestamp TIMESTAMP;
        """)
        conn.commit()

    cur.close()
    conn.close()

def log_prediction_to_db(email, symbol, future_date, predicted_value):
    add_timestamp_column_if_missing()

    if isinstance(predicted_value, np.float64):
        predicted_value = float(predicted_value)

    current_timestamp = datetime.now()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO stockhistory (email, stock_symbol, prediction_date, prediction_timestamp, predicted_value)
        VALUES (%s, %s, %s, %s, %s)
    ''', (email, symbol, future_date, current_timestamp, predicted_value))

    conn.commit()
    cur.close()
    conn.close()

email=None

def ensure_user_table_exists():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create userdata2 table if it does not exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS userdata2 (
            email VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255)
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Ensure table exists before querying
    ensure_user_table_exists()

    session.clear()  # Clear the session at the start of the route

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # Get password from form

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM userdata2 WHERE email = %s', (email,))
        user = cur.fetchone()

        if user:
            # Email exists, proceed with email verification
            verification_code = random.randint(100000, 999999)
            send_email(email, verification_code)

            session['email'] = email
            session['verification_code'] = str(verification_code)

            cur.close()
            conn.close()

            return redirect(url_for('verify'))
        else:
            # Email does not exist, create new user after verification
            verification_code = random.randint(100000, 999999)
            send_email(email, verification_code)

            session['email'] = email
            session['password'] = password
            session['verification_code'] = str(verification_code)

            cur.close()
            conn.close()

            return redirect(url_for('verify'))

    return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_input_code = request.form['user_input_code']
        if user_input_code == session.get('verification_code'):
            email = session.get('email')
            password = session.get('password')

            # Check if user exists in the database
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM userdata2 WHERE email = %s', (email,))
            user = cur.fetchone()

            if not user and password:
                # If user doesn't exist, add to database after verification
                cur.execute('INSERT INTO userdata2 (email, password) VALUES (%s, %s)', (email, password))
                conn.commit()

            cur.close()
            conn.close()

            # Clear session after successful verification
            session.clear()

            # Store email in the session for the current visit
            session['email'] = email

            return redirect(url_for('index'))
        else:
            return "Verification failed. Please try again."
    return render_template('verify.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'email' not in session:
        return redirect(url_for('login'))

    predicted_prices = []
    actual_prices = []
    error_message = None
    future_dates = []
    future_prediction = None
    accuracy_score = None
    chatbot_response=None
    

    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        future_date_str = request.form.get('future_date', '')
        year_prv = datetime.now().year - 1

        # Fetch the stock data from Alpha Vantage
        df = fetch_stock_data(symbol)

        if df is not None:
            df = add_technical_indicators(df)
            df2 = df[df.index <= f'{year_prv}-12-29']

            # Train the model
            model, scaler = train_random_forest(df2)

            if future_date_str:
                future_date = pd.to_datetime(future_date_str)
                last_date = df.index[-1]

                if future_date <= last_date or is_holiday(future_date):
                    error_message = "No prediction available."
                    return render_template('index.html', predicted_prices=predicted_prices, actual_prices=actual_prices,
                                           future_dates=future_dates, error_message=error_message, future_prediction=future_prediction,
                                           accuracy_score=accuracy_score)

                # Simulate future data for the given future date
                future_df = df.copy()
                current_date = last_date

                while current_date < future_date:
                    next_row = future_df.iloc[-1][['Close', 'MA_5', 'MA_10', 'MA_50', 'Volatility', 'RSI', 'MACD', 'MACD_signal']]
                    next_row_df = pd.DataFrame([next_row])
                    next_row_scaled = scaler.transform(next_row_df)

                    predicted_price = model.predict(next_row_scaled)[0]

                    next_date = current_date + timedelta(days=1)
                    new_row = pd.Series({
                        'Open': predicted_price,
                        'High': predicted_price,
                        'Low': predicted_price,
                        'Close': predicted_price,
                        'Volume': 0,
                    }, name=next_date)

                    future_df = pd.concat([future_df, new_row.to_frame().T])
                    future_df = add_technical_indicators(future_df)
                    current_date = next_date

                future_prediction = round(predicted_price, 2)
                print(f"The prediction for {future_date_str} is {future_prediction}")
                log_prediction_to_db(session['email'], symbol, future_date, future_prediction)

            current_year = datetime.now().year

            start_date = datetime(current_year, 1, 1)
            end_date = datetime.now()
            date_range = pd.date_range(start=start_date, end=end_date)

            for date in date_range:
                if date in df.index:
                    last_row = df.loc[date][['Close', 'MA_5', 'MA_10', 'MA_50', 'Volatility', 'RSI', 'MACD', 'MACD_signal']]
                    last_row_df = pd.DataFrame([last_row])
                    last_row_scaled = scaler.transform(last_row_df)

                    predicted_price = model.predict(last_row_scaled)[0]
                    predicted_prices.append(predicted_price)
                    actual_prices.append(df.loc[date]['Close'])
                    future_dates.append(date)


            accuracy_score = round(r2_score(actual_prices, predicted_prices) * 100, 2)
            plot_filename = plot_prices(future_dates, predicted_prices, actual_prices)
            # Make investment decision
            investment_decision = make_investment_decision(
                future_prediction,
                symbol,
                GOOGLE_NEWS_API_KEY
            )

            investment_decision = format_investment_decision(investment_decision)
            session['investment_decision']=investment_decision
            # Fetch stock news
            stock_news = fetch_stock_news(symbol, GOOGLE_NEWS_API_KEY)
            if not stock_news:
                return "Unable to fetch stock news. Decision cannot be made."
            print("\nStock News Headlines:")
            for i, news in enumerate(stock_news, 1):
                print(f"{i}. {news}")
            
            
            return render_template('index.html', predicted_prices=predicted_prices, actual_prices=actual_prices,

                                   future_dates=future_dates, plot_url=plot_filename, future_prediction=future_prediction,
                                   accuracy_score=accuracy_score, investment_decision=investment_decision, stock_news=stock_news,chatbot_response=chatbot_response, show_chatbot=True)

        else:
            error_message = "Failed to fetch stock data.Try Again Later."
        
    elif request.method == 'GET':
        # Initialize chatbot interaction
        user_question = request.args.get('user_query')
        investment_decision2 = session.get('investment_decision', "Investment decision not available.")
    
        if user_question:
            query = f"As you have provided {session.get('investment_decision')}. Now my question is {user_question}. If the question is out of the context, only say 'out of context'."
            chatbot_response = format_investment_decision(chat_with_gemini(query))
            return render_template('index.html', chatbot_response=chatbot_response, investment_decision=investment_decision2)
        else:
            return render_template('index.html', predicted_prices=predicted_prices, actual_prices=actual_prices,
                           error_message="No response from chatbot, please try again.", future_prediction=future_prediction, accuracy_score=accuracy_score)   
        

    return render_template('index.html', predicted_prices=predicted_prices, actual_prices=actual_prices,
                           error_message=error_message, future_prediction=future_prediction, accuracy_score=accuracy_score)   

if __name__ == '__main__':
    app.run(debug=True)
