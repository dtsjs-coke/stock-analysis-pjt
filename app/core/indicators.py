import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class IndicatorCalculator:
    @staticmethod
    def add_indicators(df):
        """
        Adds technical indicators using pure pandas for performance on Termux.
        No heavy dependencies like numba required.
        """
        if df is None or df.empty:
            return df
            
        try:
            df = df.copy()
            
            # 1. Moving Averages (SMA)
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA60'] = df['Close'].rolling(window=60).mean()
            df['MA120'] = df['Close'].rolling(window=120).mean()
            
            # 2. RSI (Relative Strength Index)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 3. MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
            
            # 4. Bollinger Bands
            df['BB_Middle'] = df['MA20']
            std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (std * 2)
            
            return df
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df

indicators = IndicatorCalculator()
