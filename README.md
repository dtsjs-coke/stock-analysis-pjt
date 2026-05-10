# 🤖 AI Stock Analyst (Binance Style)

갤럭시 S9(Termux) 환경에 최적화된 **실시간 AI 주식 분석 및 자동 투자 시뮬레이션 플랫폼**입니다.
Binance의 직관적인 다크 모드 디자인을 채택하였으며, AI 감성 분석과 다중 기술 지표를 결합하여 사용자에게 명확한 투자 인사이트를 제공합니다.

## 🚀 주요 기능
- **통합 분석 대시보드:**
  - 한국(KRX)/미국(NASDAQ/NYSE) 통합 검색 엔진 (자동완성 기능).
  - 실시간 주가 및 수익률 추적.
  - 전문가형 분석 기법(RSI, MA, MACD, 볼린저 밴드) 기반의 실시간 매수/매도 의견(Consensus).
  - 뉴스 감성 분석(Sentiment Analysis) 및 원문 링크 연동.
- **지능형 자동 투자 시뮬레이션:**
  - 초기 자본금, 투자 성향(보수/중립/공격), 매수 비중(Partial Fills) 설정 가능.
  - AI 혼합 전략, 골든크로스, RSI 역발상 등 기법 혼용.
  - 상세 매매 기록지(평단가, 잔고, 매수/매도 근거) 실시간 출력.

## 📁 Project Structure
```text
stock-analysis-pjt/
├── app/
│   ├── core/
│   │   ├── data_fetcher.py   # 통합 데이터 엔진 & 검색
│   │   ├── indicators.py     # 기술적 지표 계산
│   │   └── strategies.py     # AI 투자 전략 엔진
│   ├── models/
│   │   └── database.py       # 투자 데이터 관리
│   ├── utils/
│   │   └── sentiment.py      # 뉴스 수집 & 감성 분석
│   └── ui.py                 # Streamlit UI & 내비게이션
├── data/
│   └── cache/                # 고속 검색을 위한 종목 캐시
├── GEMINI.md                 # 프로젝트 가이드
├── MEMORY.md                 # 진행 상황 및 설정 기록
└── requirements.txt          # 패키지 의존성 목록
```

## ⚙️ 실행 가이드 (Termux)
1. **가상환경 활성화:**
   ```bash
   source venv/bin/activate
   ```
2. **앱 실행:**
   ```bash
   export STREAMLIT_GATHER_USAGE_STATS=false
   streamlit run app/ui.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
   ```
   *접속: http://localhost:8501*

## 💡 개발 철학
- **Lightweight:** S9 기기 환경을 고려해 무거운 빌드 과정(Numba 등)을 배제하고 순수 Pandas 산술 연산으로 최적화.
- **Causality:** 시뮬레이션은 미래 데이터를 참조하지 않는 엄격한 인과율(Causality) 원칙을 준수.
- **Professional:** Binance의 디자인 시스템을 벤치마킹하여 정보의 우선순위가 명확한 UI 구성.
