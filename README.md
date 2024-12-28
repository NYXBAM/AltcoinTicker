Bitcoin Analysis and Altcoin Prediction Dashboard
This project is a Flask-based application for real-time Bitcoin price and dominance tracking, as well as predictive analysis of altcoin movements. It utilizes technical indicators like RSI, MACD, and SMA to provide actionable insights for cryptocurrency trading.

Features
Real-Time Bitcoin Price Tracking: Fetches live Bitcoin prices using the Binance API.
Bitcoin Dominance Analysis: Tracks Bitcoin dominance trends using TradingView data.
Technical Indicators:
RSI (Relative Strength Index)
MACD (Moving Average Convergence Divergence)
SMA (Simple Moving Average)
Altcoin Movement Prediction: Predicts altcoin behavior (e.g., "Altseason", "DUMP") based on Bitcoin dominance and price trends.
Historical Data Storage: Maintains a history of Bitcoin prices and dominance for trend visualization.
REST API: Exposes data through a /api/data endpoint for integration.
Responsive Web Interface: Displays price trends, dominance trends, and predictions in a clean, user-friendly format.
How It Works
Data Sources:
Fetches Bitcoin price data from Binance.
Retrieves Bitcoin dominance data from TradingView.
Trend Analysis:
Uses predefined thresholds to determine "UP", "DOWN", or "STABLE" trends.
Combines price and dominance trends to forecast altcoin movements.
Background Tasks:
Runs periodic updates for price and dominance data using multithreading.
Saves data to a local JSON file for persistence.
Technologies Used
Backend: Flask
Frontend: HTML/CSS (with Jinja2 templating)
APIs:
Binance API for price data
TradingView API for dominance data
Libraries:
talib for technical analysis indicators
tvDatafeed for TradingView integration
pandas and numpy for data manipulation
requests for API interactions
Multithreading: Background tasks for continuous updates.


TO DO:
soon...

































License
This project is licensed under the MIT License.

