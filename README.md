# Stock Analysis Project (Binance Style)

This project is a stock market analysis platform built with Python, FastAPI, and Streamlit. It features real-time data visualization, technical analysis, AI-based news sentiment analysis, and an investment simulation portfolio.

## Features
- **Real-time Data:** Fetch US and KR stock data using `yfinance` and `FinanceDataReader`.
- **Technical Indicators:** SMA, RSI, MACD, and Bollinger Bands.
- **AI Sentiment Analysis:** News headlines analyzed with `vaderSentiment`.
- **Investment Simulation:** Buy/Sell stocks in a simulated portfolio saved in SQLite.
- **Binance Style UI:** Dark mode with the iconic Binance Yellow accent.
- **High Performance:** Multi-layered caching for stock data.

## How to Run on Termux

1. **Install Build Tools (First time only):**
   ```bash
   pkg install rust binutils clang make
   ```

2. **Setup Virtual Environment:**
   ```bash
   python -m venv --system-site-packages venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the App:**
   ```bash
   streamlit run app/ui.py
   ```

## Folder Structure
- `app/core/`: Data fetching and technical indicators.
- `app/models/`: Database schema and portfolio logic.
- `app/utils/`: Sentiment analysis and utility functions.
- `app/ui.py`: Main Streamlit interface.
- `data/`: Database and cache files.
