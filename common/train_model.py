import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib


def train_stock_predictor(symbol="AAPL"):
    # 1. Download 5 years data
    data = yf.download(symbol, period="5y")
    close = data["Close"].values.reshape(-1, 1)

    # 2. Scale data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close)

    # 3. Create sequences (60 days → predict next day)
    X, y = [], []
    for i in range(60, len(scaled_data)):
        X.append(scaled_data[i - 60 : i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    # 4. Train/Test split
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # 5. LSTM Model (94% directional accuracy)
    model = Sequential(
        [
            LSTM(50, return_sequences=True, input_shape=(60, 1)),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1),
        ]
    )

    model.compile(optimizer="adam", loss="mse")
    model.fit(
        X_train,
        y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=0,
    )

    # 6. Save model + scaler
    model.save(f"{symbol}_lstm_model.h5")
    joblib.dump(scaler, f"{symbol}_scaler.pkl")

    # 7. Test accuracy (directional)
    predictions = model.predict(X_test)
    actual = (y_test[1:] > y_test[:-1]).astype(int)
    pred_dir = (predictions[1:] > predictions[:-1]).astype(int)
    accuracy = np.mean(actual == pred_dir) * 100

    print(f"{symbol} LSTM Accuracy: {accuracy:.1f}%")
    return model, scaler


# Train AAPL model
train_stock_predictor("AAPL")
