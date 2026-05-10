import os
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import functools
import logging
import re

logger = logging.getLogger(__name__)
os.environ['PYTZ_TZDATADIR'] = os.path.join(os.path.dirname(pd.__file__), '..', 'pytz', 'zoneinfo')

CACHE_DIR = "data/cache"
if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)

class StockDataFetcher:
    def __init__(self):
        self._unified_listings = None
        self._search_options = []
        self._load_all_listings()

    def _load_all_listings(self):
        cache_path = os.path.join(CACHE_DIR, "unified_listings_v3.pkl")
        try:
            if os.path.exists(cache_path):
                self._unified_listings = pd.read_pickle(cache_path)
            else:
                kr = fdr.StockListing('KRX')
                if 'Code' in kr.columns: kr = kr.rename(columns={'Code': 'Symbol'})
                kr = kr[['Symbol', 'Name']]
                kr['Market'] = 'KR'
                try:
                    us_nasdaq = fdr.StockListing('NASDAQ')[['Symbol', 'Name']]
                    us_nyse = fdr.StockListing('NYSE')[['Symbol', 'Name']]
                    us = pd.concat([us_nasdaq, us_nyse]).drop_duplicates('Symbol')
                    us['Market'] = 'US'
                except:
                    us = pd.DataFrame([{'Symbol': 'AAPL', 'Name': 'Apple Inc.', 'Market': 'US'}])
                self._unified_listings = pd.concat([kr, us], ignore_index=True)
                self._unified_listings['Name'] = self._unified_listings['Name'].fillna(self._unified_listings['Symbol'])
                self._unified_listings.to_pickle(cache_path)
            
            self._unified_listings = self._unified_listings.sort_values(by=['Market', 'Symbol'])
            self._search_options = [f"{row['Symbol']} | {row['Name']} ({row['Market']})" for _, row in self._unified_listings.iterrows()]
        except Exception as e:
            logger.error(f"통합 리스트 로드 실패: {e}")
            self._unified_listings = pd.DataFrame(columns=['Symbol', 'Name', 'Market'])

    def get_all_search_options(self): return self._search_options

    def get_stock_by_label(self, label):
        try:
            parts = label.split(" | ")
            symbol = parts[0].strip()
            name = parts[1].split(" (")[0].strip()
            market = parts[1].split(" (")[1].replace(")", "").strip()
            return {'symbol': symbol, 'name': name, 'market': market}
        except: return None

    def get_search_suggestions(self, query):
        query = str(query).strip().upper()
        if not query: return []
        df = self._unified_listings
        mask = (df['Symbol'].str.contains(query, na=False)) | (df['Name'].str.upper().str.contains(query, na=False))
        results = df[mask].copy()
        
        suggestions = []
        if not results.empty:
            results['exact_match'] = (results['Symbol'] == query)
            results = results.sort_values(by=['exact_match'], ascending=False).head(10)
            for _, row in results.iterrows():
                suggestions.append({'symbol': row['Symbol'], 'name': row['Name'], 'market': row['Market']})
        return suggestions

    @functools.lru_cache(maxsize=32)
    def get_ohlcv(self, ticker_symbol, market='KR', period="1y"):
        try:
            if market == 'KR':
                # 한국 주식은 기간 필터링 적용
                start_date = (datetime.now() - timedelta(days=730 if period=="2y" else 365 if period=="1y" else 180 if period=="6mo" else 90)).strftime('%Y-%m-%d')
                df = fdr.DataReader(ticker_symbol, start=start_date)
            else:
                # 미국 주식은 period 방식 사용 (안정적)
                ticker = yf.Ticker(ticker_symbol)
                df = ticker.history(period=period)
            
            if df is None or df.empty: return None
            
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df.columns = [str(c).lower() for c in df.columns]
            if 'adj close' in df.columns: df['close'] = df['adj close']
            
            mapping = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
            existing = [c for c in mapping.keys() if c in df.columns]
            df = df[existing].rename(columns={c: mapping[c] for c in existing})
            return df
        except: return None

    @functools.lru_cache(maxsize=32)
    def get_realtime_price(self, ticker_symbol, market='KR'):
        try:
            if market == 'KR':
                df = fdr.DataReader(ticker_symbol)
                if not df.empty and len(df) > 1:
                    latest, prev = df.iloc[-1], df.iloc[-2]
                    return {"price": latest['Close'], "change": latest['Close'] - prev['Close'], "pct_change": (latest['Close'] / prev['Close'] - 1) * 100}
            else:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    prev = hist.iloc[-2] if len(hist)>1 else latest
                    return {"price": latest['Close'], "change": latest['Close'] - prev['Close'], "pct_change": (latest['Close'] / prev['Close'] - 1) * 100 if prev['Close'] != 0 else 0}
        except: pass
        return None


fetcher = StockDataFetcher()
