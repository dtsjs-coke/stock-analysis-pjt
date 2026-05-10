import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
import os
from dotenv import load_dotenv
import re

logger = logging.getLogger(__name__)

# 외부 .env 로드 (Butler 기반)
BUTLER_ENV_PATH = os.path.expanduser("~/my_butler/.env")
if os.path.exists(BUTLER_ENV_PATH):
    load_dotenv(BUTLER_ENV_PATH)

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.naver_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _clean_and_deduplicate(self, headlines_with_links):
        """
        중복 뉴스를 제거하고 텍스트를 정제함 (URL 포함 구조 대응)
        """
        if not headlines_with_links: return []
        
        seen_norms = set()
        unique_results = []
        
        for item in headlines_with_links:
            text = item['text']
            norm = re.sub(r'[^가-힣a-zA-Z0-9]', '', text).lower()
            if len(norm) < 10: continue
            
            prefix = norm[:20]
            if prefix not in seen_norms:
                seen_norms.add(prefix)
                unique_results.append(item)
                
        return unique_results

    def get_news_headlines(self, ticker_symbol, ticker_name="", market='US'):
        """
        네이버 검색/크롤링을 활용하여 국내/외 뉴스 모두 수집
        """
        results = []
        try:
            # 네이버 API 시도 (국내/외 불문)
            search_query = f"{ticker_name} {ticker_symbol}" if ticker_name else ticker_symbol
            if self.naver_id and self.naver_secret:
                url = f"https://openapi.naver.com/v1/search/news.json?query={search_query}&display=15&sort=sim"
                headers = {"X-Naver-Client-Id": self.naver_id, "X-Naver-Client-Secret": self.naver_secret}
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    for item in res.json().get('items', []):
                        clean_title = BeautifulSoup(item['title'], "html.parser").get_text()
                        results.append({'text': clean_title, 'url': item.get('link', '#')})
            
            # API 실패 시 네이버 통합검색 크롤링 백업
            if not results:
                url = f"https://search.naver.com/search.naver?where=news&query={search_query}"
                response = requests.get(url, headers=self.headers, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.select('a.news_tit'):
                    results.append({'text': a.get('title'), 'url': a.get('href')})
                        
        except Exception as e:
            logger.error(f"뉴스 수집 에러 ({ticker_symbol}): {e}")
            
        return self._clean_and_deduplicate(results)[:10]

    def analyze_sentiment(self, news_items):
        if not news_items:
            return {"score": 0, "label": "중립", "count": 0, "details": [], "message": "뉴스가 없습니다."}
            
        total_compound = 0
        for item in news_items:
            score = self.analyzer.polarity_scores(item['text'])
            item['score'] = score['compound']
            total_compound += item['score']
            
        avg_score = total_compound / len(news_items)
        label = "긍정" if avg_score >= 0.05 else "부정" if avg_score <= -0.05 else "중립"
            
        return {
            "score": avg_score,
            "label": label,
            "count": len(news_items),
            "details": news_items
        }

sentiment_analyzer = SentimentAnalyzer()
