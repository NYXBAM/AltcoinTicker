import pandas as pd
import time
from flask import Flask, jsonify, render_template
import threading
import json
import os
import requests

from tvDatafeed import TvDatafeed, Interval
import talib
import numpy as np

def calculate_rsi(prices, period=14):
    """
    Рассчитывает RSI для заданных цен.
    """
    return talib.RSI(np.array(prices), timeperiod=period)

def calculate_macd(prices, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    Рассчитывает MACD и сигнальную линию.
    """
    macd, signal, hist = talib.MACD(np.array(prices), fastperiod, slowperiod, signalperiod)
    return macd, signal

def calculate_sma(prices, period=50):
    """
    Рассчитывает Simple Moving Average (SMA).
    """
    return talib.SMA(np.array(prices), timeperiod=period)

app = Flask(__name__)

# Глобальные переменные для хранения данных
data = {
    "btc_dominance": None,
    "btc_price": None,
    "dominance_trend": None,
    "price_trend": None,
    "alts_movement": None,
    "alts_color": None,  # Цвет прогноза для отображения на странице
    "history": []  # Для хранения истории данных
}

DATA_FILE = "btc_data.json"

def save_data_to_file():
    """
    Сохраняет текущие данные в файл.
    """
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

def load_data_from_file():
    """
    Загружает данные из файла, если файл существует.
    """
    global data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                loaded_data = json.load(file)
            data.update(loaded_data)
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")

# Загрузка данных при запуске
load_data_from_file()

def get_btc_price():
    """
    Получение текущей цены BTC через Binance API.
    """
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        btc_price = float(response.json()["price"])
        return btc_price
    except Exception as e:
        print(f"Ошибка получения цены BTC: {e}")
        return None

def get_btc_dominance():
    """
    Получение доминации BTC через TradingView API.
    """
    try:
        tv = TvDatafeed()
        symbol = "CRYPTOCAP:BTC.D"  # Используем тикер для Bitcoin Dominance
        data = tv.get_hist(symbol, interval=Interval.in_1_minute, n_bars=30)  # Получаем последние 30 данных

        # Возвращаем данные по ценам закрытия
        return data['close'].values
    except Exception as e:
        print(f"Ошибка получения доминации BTC: {e}")
        return None

def analyze_trend(current_value, previous_value, threshold=0.0095):
    """
    Анализ тренда изменения значения: UP, DOWN или STABLE.
    """
    if current_value > previous_value * (1 + threshold / 100):
        return "UP"
    elif current_value < previous_value * (1 - threshold / 100):
        return "DOWN"
    else:
        return "STABLE"

def predict_alts_movement(btc_dominance_trend, btc_price_trend):
    """
    Прогноз движения альткоинов на основании трендов доминации и цены BTC.
    """
    mapping = {
        ("UP", "UP"): "DOWN",
        ("UP", "DOWN"): "DUMP",
        ("UP", "STABLE"): "STABLE",
        ("STABLE", "UP"): "UP",
        ("STABLE", "STABLE"): "STABLE",
        ("STABLE", "DOWN"): "DOWN",
        ("DOWN", "UP"): "Altseason",
        ("DOWN", "DOWN"): "STABLE",
        ("DOWN", "STABLE"): "UP",
    }
    result = mapping.get((btc_dominance_trend, btc_price_trend), "UNKNOWN")
    colors = {
        "UP": "green",
        "DOWN": "red",
        "STABLE": "yellow",
        "DUMP": "red",
        "Altseason": "purple",
    }
    return result, colors.get(result, "white")

def update_btc_price():
    """
    Фоновая задача для обновления цены BTC каждую секунду.
    """
    previous_price = get_btc_price()
    price_history = [previous_price]

    while True:
        time.sleep(1)
        current_price = get_btc_price()

        if current_price is None:
            continue

        price_history.append(current_price)
        if len(price_history) > 100:
            price_history.pop(0)

        rsi = calculate_rsi(price_history)
        macd, macd_signal = calculate_macd(price_history)
        sma = calculate_sma(price_history)

        rsi_trend = "BUY" if rsi[-1] < 30 else ("SELL" if rsi[-1] > 70 else "STABLE")
        macd_trend = "BUY" if macd[-1] > macd_signal[-1] else "SELL"
        sma_trend = "BUY" if current_price > sma[-1] else "SELL"

        if rsi_trend == "BUY" and macd_trend == "BUY" and sma_trend == "BUY":
            altcoins_movement = "Altseason"
            altcoins_color = "green"
        elif rsi_trend == "SELL" and macd_trend == "SELL" and sma_trend == "SELL":
            altcoins_movement = "DUMP"
            altcoins_color = "red"
        else:
            altcoins_movement = "STABLE"
            altcoins_color = "yellow"

        price_trend = analyze_trend(current_price, previous_price)

        data.update({
            "btc_price": current_price,
            "price_trend": price_trend,
            "alts_movement": altcoins_movement,
            "alts_color": altcoins_color,
        })

        data["history"].append({
            "timestamp": time.time(),
            "btc_price": current_price,
            "btc_dominance": data["btc_dominance"],
            "alts_movement": data["alts_movement"]
        })

        if len(data["history"]) > 1000:
            data["history"].pop(0)

        previous_price = current_price
        save_data_to_file()

def update_btc_dominance():
    """
    Фоновая задача для обновления доминации BTC раз в 5 минут.
    """
    previous_dominance = get_btc_dominance()

    while True:
        time.sleep(1)
        current_dominance = get_btc_dominance()
        print(current_dominance[-1])

        if current_dominance is None:
            continue

        dominance_trend = analyze_trend(current_dominance[-1], previous_dominance[-1])
        prediction, color = predict_alts_movement(dominance_trend, data["price_trend"])

        data.update({
            "btc_dominance": current_dominance[-1],
            "dominance_trend": dominance_trend,
            "alts_movement": prediction,
            "alts_color": color,
        })

        previous_dominance = current_dominance
        save_data_to_file()

@app.route("/api/data")
def api_data():
    """
    API для получения текущих данных.
    """
    return jsonify(data)

@app.route("/")
def index():
    """
    Главная страница с графиком.
    """
    return render_template("index.html", history=data["history"])

if __name__ == "__main__":
    threading.Thread(target=update_btc_price, daemon=True).start()
    threading.Thread(target=update_btc_dominance, daemon=True).start()
    app.run(debug=True)