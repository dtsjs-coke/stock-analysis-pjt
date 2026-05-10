# Stock Analysis Project (Binance Style)

## Vision
한국 및 미국 주식을 위한 AI 기반 통합 분석 플랫폼. 실시간 데이터, 기술 지표 분석, AI 감성 분석, 그리고 로직 기반의 자동 투자 시뮬레이션을 제공합니다.

## Tech Stack
- **Language:** Python 3.13
- **Framework:** Streamlit (UI), FastAPI (Backend ready)
- **Data Source:** Yfinance (US), FinanceDataReader (KR)
- **Database:** SQLite (aiosqlite)
- **Logic:** 
  - `data_fetcher.py`: 통합 종목 캐싱 (KR/US) 및 검색 엔진
  - `indicators.py`: Pandas 기반 기술 지표
  - `strategies.py`: AI 하이브리드 투자 전략 엔진
  - `sentiment.py`: Naver/Finnhub API 기반 감성 분석

## UI Architecture
- **Sidebar Isolation:** 탭(메뉴) 전환 시 사이드바 위젯이 컨테이너별로 분리되어 충돌 방지.
- **Smart Auto-complete:** 로컬 캐시를 이용한 실시간 종목 검색.
- **Navigation:** 세션 상태 관리(`st.session_state`)를 통해 분석 페이지와 시뮬레이션 간 유기적 전환.

## Project Structure
```text
stock-analysis-pjt/
├── app/
│   ├── core/
│   │   ├── data_fetcher.py   # 통합 데이터 엔진 & 검색
│   │   ├── indicators.py     # 기술적 지표 계산
│   │   └── strategies.py     # AI 투자 전략 엔진
│   ├── models/
│   │   └── database.py       # SQLite DB 스키마
│   ├── utils/
│   │   └── sentiment.py      # 뉴스 수집 & 감성 분석
│   └── ui.py                 # Streamlit UI & 내비게이션
├── data/
│   └── cache/                # 통합 종목/주가 캐시
├── GEMINI.md                 # 프로젝트 가이드
├── MEMORY.md                 # 진행 상황 및 설정 기록
└── requirements.txt          # 필요 패키지
```

## Deployment Guide (Termux)
```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 필수 라이브러리 설치
pip install -r requirements.txt

# 3. 앱 실행
export STREAMLIT_GATHER_USAGE_STATS=false
streamlit run app/ui.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
```
