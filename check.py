import pandas as pd 
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import cross_val_score, learning_curve
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree
import requests
import datetime

# Fetch stock data
def fetch_stock_data(symbol, api_key):
    STOCK_BASE_URL = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'full',
        'apikey': api_key
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

# Calculate RSI
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Calculate MACD
def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    df['EMA_fast'] = df['Close'].ewm(span=fast_period, adjust=False).mean()
    df['EMA_slow'] = df['Close'].ewm(span=slow_period, adjust=False).mean()
    df['MACD'] = df['EMA_fast'] - df['EMA_slow']
    df['MACD_signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
    return df

# Add technical indicators
def add_technical_indicators(df):
    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['MA_10'] = df['Close'].rolling(window=10).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['Volatility'] = df['High'] - df['Low']
    df['RSI'] = calculate_rsi(df)
    df = calculate_macd(df)
    df.fillna(0, inplace=True)
    return df

# Plot learning curve
def plot_learning_curve(estimator, X, y, cv=5, scoring='r2'):
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, scoring=scoring, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10)
    )

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.figure()
    plt.title("Learning Curve")
    plt.xlabel("Training examples")
    plt.ylabel(scoring)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt

# Evaluate model
def evaluate_model(model, X_train, y_train, X_test, y_test):
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    train_rmse = mean_squared_error(y_train, y_train_pred, squared=False)
    test_rmse = mean_squared_error(y_test, y_test_pred, squared=False)

    print("Training R2 Score:", train_r2)
    print("Testing R2 Score:", test_r2)
    print("Training RMSE:", train_rmse)
    print("Testing RMSE:", test_rmse)

    if train_r2 > test_r2:
        print("Model is overfitting")
    else:
        print("Model is not overfitting")

# Plot actual vs predicted
def plot_actual_vs_predicted(y_test, y_test_pred, test_dates):
    plt.figure(figsize=(14, 7))
    plt.plot(test_dates, y_test, label='Actual Test', color='red')
    plt.plot(test_dates, y_test_pred, label='Predicted Test', color='orange')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title('Actual vs Predicted Stock Prices (Test Data)')
    plt.legend()
    plt.show()

# Visualize the first tree in the random forest
def visualize_random_forest(model, feature_names):
    if isinstance(model, RandomForestRegressor):
        estimator = model.estimators_[0]
        plt.figure(figsize=(200, 100))
        plot_tree(estimator, feature_names=feature_names, filled=True, rounded=True)
        plt.title("First Decision Tree in the Random Forest")
        plt.show()
    else:
        print("The provided model is not a RandomForestRegressor.")

# Visualize first three layers of the first tree in the RandomForest model
def visualize_first_three_layers_of_random_forest(model, feature_names):
    if isinstance(model, RandomForestRegressor):
        estimator = model.estimators_[0]
        plt.figure(figsize=(30, 15), dpi=200)  # Set high resolution for zoomed-in details
        plot_tree(estimator, feature_names=feature_names, filled=True, rounded=True, max_depth=3)
        plt.title("First Three Layers of the First Decision Tree in the Random Forest")
        plt.show()
    else:
        print("The provided model is not a RandomForestRegressor.")

# Main function
def main():
    symbol = 'AAPL'
    api_key = 'FVOEWU64HKN1C9U2'

    df = fetch_stock_data(symbol, api_key)
    df = add_technical_indicators(df)

    # Define the training and testing period
    today = datetime.datetime.today()
    current_year = today.year
    last_year = current_year - 1

    train_end_date = f"{last_year}-12-31"
    test_start_date = f"{current_year}-01-01"

    # Split data into training and testing sets based on date
    train_df = df[:train_end_date]
    test_df = df[test_start_date:]

    X_train = train_df[['Close', 'MA_5', 'MA_10', 'MA_50', 'Volatility', 'RSI', 'MACD', 'MACD_signal']]
    y_train = train_df['Close'].shift(-1).dropna()  # Predict the next day's closing price
    X_train = X_train[:-1]  # Remove the last row with NaN target

    X_test = test_df[['Close', 'MA_5', 'MA_10', 'MA_50', 'Volatility', 'RSI', 'MACD', 'MACD_signal']]
    y_test = test_df['Close'].shift(-1).dropna()  # Predict the next day's closing price
    X_test = X_test[:-1]  # Remove the last row with NaN target

    train_dates = train_df.index[:-1]
    test_dates = test_df.index[:-1]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    evaluate_model(model, X_train, y_train, X_test, y_test)

    X = np.concatenate((X_train, X_test), axis=0)
    y = np.concatenate((y_train, y_test), axis=0)
    print("Cross-validation scores:", cross_val_score(model, X, y, cv=5))

    plot = plot_learning_curve(model, X, y)
    plot.show()

    # Plot actual vs predicted values
    plot_actual_vs_predicted(y_test, y_test_pred, test_dates)

    # Visualize the first tree in the random forest
    feature_names = ['Close', 'MA_5', 'MA_10', 'MA_50', 'Volatility', 'RSI', 'MACD', 'MACD_signal']
    visualize_random_forest(model, feature_names)

    # Visualize the first three layers of the first tree in the random forest
    visualize_first_three_layers_of_random_forest(model, feature_names)

if __name__ == '__main__':
    main()
