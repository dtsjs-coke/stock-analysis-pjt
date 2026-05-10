import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import asyncio
from datetime import datetime, timedelta
from core.data_fetcher import fetcher
from core.indicators import indicators
from core.strategies import strategy_engine
from utils.sentiment import sentiment_analyzer
from models.database import init_db

# Binance Design Tokens
COLORS = {
    "canvas_dark": "#0b0e11",
    "surface_card": "#1e2329",
    "primary": "#FCD535",
    "primary_hover": "#f0b90b",
    "trading_up": "#0ecb81",
    "trading_down": "#f6465d",
    "text_muted": "#707a8a",
    "text_body": "#eaecef"
}

USD_KRW = 1400.0

def format_currency(val, market='KR'):
    if val is None: return "N/A"
    if market == 'KR': return f"{int(val):,}원"
    else: return f"${val:,.2f} ({int(val * USD_KRW):,}원)"

def apply_custom_style():
    st.markdown(f"""
        <style>
        html, body, [class*="css"] {{ font-family: 'Apple SD Gothic Neo', sans-serif; background-color: {COLORS['canvas_dark']}; color: {COLORS['text_body']}; }}
        .stApp {{ background-color: {COLORS['canvas_dark']}; }}
        .stButton>button {{ background-color: {COLORS['primary']}; color: black; border-radius: 6px; font-weight: 700; border: none; }}
        .card {{ background-color: {COLORS['surface_card']}; padding: 1.2rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #2b3139; }}
        .up {{ color: {COLORS['trading_up']}; }}
        .down {{ color: {COLORS['trading_down']}; }}
        .signal-box {{ padding: 1rem; border-radius: 10px; text-align: center; font-weight: 800; font-size: 1.5rem; margin: 1rem 0; }}
        /* 사이드바 selectbox 강조 */
        div[data-testid="stSidebar"] .stSelectbox label {{ color: {COLORS['primary']}; font-weight: bold; font-size: 1.1rem; }}
        </style>
    """, unsafe_allow_html=True)

async def run_db_init():
    await init_db()

# --- 자동완성 검색 핸들러 (개선) ---
def handle_search_change():
    """멀티셀렉트에서 종목 선택 시 세션 상태를 즉시 업데이트"""
    selected_list = st.session_state.smart_search
    if selected_list:
        label = selected_list[0]
        stock_data = fetcher.get_stock_by_label(label)
        if stock_data:
            st.session_state.current_stock = stock_data
            st.session_state.page_mode = "시장 분석 (메인)"


def main():
    st.set_page_config(page_title="AI 주식 분석 전문가", layout="wide")
    apply_custom_style()
    
    if 'db_initialized' not in st.session_state:
        asyncio.run(run_db_init())
        st.session_state.db_initialized = True

    # --- 세션 상태 통합 관리 ---
    if 'favorites' not in st.session_state:
        st.session_state.favorites = [
            {'symbol': '005930', 'name': '삼성전자', 'market': 'KR'},
            {'symbol': 'NVDA', 'name': 'NVIDIA', 'market': 'US'}
        ]
    if 'current_stock' not in st.session_state:
        st.session_state.current_stock = st.session_state.favorites[0]
    if 'page_mode' not in st.session_state:
        st.session_state.page_mode = "시장 분석 (메인)"

    # --- 사이드바: 메뉴 선택 ---
    st.sidebar.markdown(f"<h1 style='color:{COLORS['primary']};'>AI ANALYST</h1>", unsafe_allow_html=True)
    page = st.sidebar.radio("메뉴", ["시장 분석 (메인)", "자동 시뮬레이션"], 
                            index=0 if st.session_state.page_mode == "시장 분석 (메인)" else 1,
                            key="nav_radio_main")
    
    if page != st.session_state.page_mode:
        st.session_state.page_mode = page
        st.rerun()
    
    st.sidebar.divider()

    # --- 탭별 전용 컨테이너 생성 ---
    analysis_container = st.sidebar.container()
    simulation_container = st.sidebar.container()

    if st.session_state.page_mode == "시장 분석 (메인)":
        with analysis_container:
            st.subheader("🔍 종목 검색")
            st.markdown(f"""
                <div class='card' style='padding:0.8rem; background-color: {COLORS['primary']}; color: black;'>
                    <div style='font-size:0.7rem;'>현재 분석 중</div>
                    <div style='font-weight:700;'>{st.session_state.current_stock['name']}</div>
                    <div style='font-size:0.8rem;'>{st.session_state.current_stock['symbol']} ({st.session_state.current_stock['market']})</div>
                </div>
            """, unsafe_allow_html=True)
            
            all_options = fetcher.get_all_search_options()
            st.multiselect("검색 (선택 즉시 분석):", options=all_options, max_selections=1, key="smart_search", on_change=handle_search_change)
            
            st.divider()
            st.subheader("⭐ 즐겨찾기 관리")
            for fav in st.session_state.favorites:
                col_name, col_del = st.columns([4, 1])
                with col_name:
                    if st.button(f"{fav['name']}", key=f"side_fav_{fav['symbol']}", use_container_width=True):
                        st.session_state.current_stock = fav
                        st.rerun()
                with col_del:
                    if st.button("❌", key=f"del_{fav['symbol']}"):
                        st.session_state.favorites = [f for f in st.session_state.favorites if f['symbol'] != fav['symbol']]
                        st.rerun()
    
    elif st.session_state.page_mode == "자동 시뮬레이션":
        with simulation_container:
            st.subheader("🤖 시뮬레이션 설정")
            initial_cap = st.number_input("초기 자본금", value=10000000, key="sim_cap")
            mode = st.selectbox("전략", ["AI 혼합 전략", "골든크로스", "RSI 역발상"], key="sim_mode")
            risk = st.selectbox("투자 성향", ["보수적", "중립", "공격적"], key="sim_risk")
            ratio = st.slider("1회 매수 비중", 0.1, 1.0, 0.5, 0.1, key="sim_ratio")
            tickers_input = st.text_input("테스트 종목 (쉼표 구분)", value="삼성전자, NVDA", key="sim_tickers")
            period = st.select_slider("기간", options=["3mo", "6mo", "1y", "2y"], value="1y", key="sim_period")
            
            if st.button("시뮬레이션 시작", use_container_width=True):
                st.session_state.sim_params = {"cap": initial_cap, "mode": mode, "risk": risk, "ratio": ratio, "tickers": tickers_input, "period": period}
                st.session_state.run_sim = True
                st.rerun()

    # 페이지 렌더링
    if st.session_state.page_mode == "시장 분석 (메인)":
        render_analysis_page()
    else:
        render_simulation_tab()

def render_analysis_page():
    curr = st.session_state.current_stock
    
    # 상단 퀵바
    st.markdown("### ⚡ 퀵 액세스")
    q_cols = st.columns(8)
    for i, fav in enumerate(st.session_state.favorites[:7]):
        with q_cols[i]:
            if st.button(fav['name'], key=f"top_fav_{fav['symbol']}", use_container_width=True):
                st.session_state.current_stock = fav
                st.rerun()
    
    # 즐겨찾기 추가 버튼
    is_fav = any(f['symbol'] == curr['symbol'] for f in st.session_state.favorites)
    if not is_fav:
        with q_cols[-1]:
            if st.button("⭐ 추가", use_container_width=True):
                st.session_state.favorites.append(curr)
                st.rerun()

    st.divider()

    # 분석 수행
    with st.spinner(f"분석 전문가가 {curr['name']}의 리포트를 작성 중입니다..."):
        rt_info = fetcher.get_realtime_price(curr['symbol'], curr['market'])
        df = fetcher.get_ohlcv(curr['symbol'], curr['market'])
        headlines = sentiment_analyzer.get_news_headlines(curr['symbol'], curr['name'], curr['market'])
        sentiment = sentiment_analyzer.analyze_sentiment(headlines)
        
        score, label, reasons = 50, "중립", []

    col1, col2 = st.columns([2, 1])

    with col1:
        if rt_info:
            p_class = "up" if rt_info['change'] >= 0 else "down"
            st.markdown(f"## {curr['name']} <span style='font-size:1rem; color:gray;'>{curr['symbol']}</span>", unsafe_allow_html=True)
            st.markdown(f"<h3 class='{p_class}'>{format_currency(rt_info['price'], curr['market'])} <span style='font-size:1.2rem;'>{rt_info['pct_change']:+.2f}%</span></h3>", unsafe_allow_html=True)

        if df is not None and len(df) > 10:
            df = indicators.add_indicators(df)
            score, label, reasons = strategy_engine.get_market_signal(df, sentiment['score'])
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = score,
                title = {'text': f"전문가 종합 의견: {label}"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': COLORS['primary']},
                         'steps': [{'range': [0, 35], 'color': COLORS['trading_down']},
                                   {'range': [35, 65], 'color': "#444"},
                                   {'range': [65, 100], 'color': COLORS['trading_up']}]}
            ))
            fig_gauge.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, margin=dict(t=50, b=0))
            st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_main")

            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='주가')])
            if 'MA20' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='20일선', line=dict(color='#ff9900', width=1.5)))
            if 'MA60' in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], name='60일선', line=dict(color='#00ffcc', width=1.5)))
            fig.update_layout(template="plotly_dark", height=450, margin=dict(t=0, b=0, l=0, r=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True, key="candle_main")
        else:
            st.warning("분석을 위한 충분한 주가 데이터를 확보하지 못했습니다.")

    with col2:
        if df is not None:
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.subheader("👨‍💼 분석가 인사이트")
            bg_color = COLORS['trading_up'] if score >= 65 else COLORS['trading_down'] if score <= 35 else "#444"
            st.markdown(f"<div class='signal-box' style='background-color:{bg_color}; color:white;'>{label}</div>", unsafe_allow_html=True)
            
            # 상세 분석 기법 결과 출력
            st.write("---")
            for item in reasons: # 여기서 reasons는 signals 리스트를 받음
                st.markdown(f"**{item['signal']} {item['technique']}**: {item['verdict']} <br><small>{item['reason']}</small>", unsafe_allow_html=True)
            
            st.divider()
            if score >= 65: advice = "🚀 강력한 매수세가 확인됩니다. 비중 확대를 고려하세요."
            elif score <= 35: advice = "📉 하락 압력이 거셉니다. 리스크 관리가 최우선입니다."
            else: advice = "⏳ 변곡점 구간입니다. 확실한 방향성 확인 후 진입이 안전합니다."
            st.info(f"**가이드:** {advice}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📰 최신 뉴스 & 링크")
        if not sentiment['details']: st.write("관련 뉴스가 없습니다.")
        else:
            for news in sentiment['details'][:5]:
                st.markdown(f"- [{news['text']}]({news['url']})", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def render_simulation_tab():
    st.markdown(f"## 🤖 AI 투자 시뮬레이션")
    st.write("본 시뮬레이션은 **인과율(Causality)**을 준수합니다.")

    # 사이드바에서 이미 정의된 params를 세션 상태에서 읽어오기만 함
    if 'sim_params' not in st.session_state:
        st.info("왼쪽 사이드바에서 시뮬레이션을 설정하고 시작 버튼을 눌러주세요.")
        return

    params = st.session_state.sim_params
    st.info(f"설정: 자본금 {params['cap']:,}원 | 전략: {params['mode']} | 성향: {params['risk']} | 비중: {params['ratio']*100}% | 기간: {params['period']}")

    ticker_list = [t.strip() for t in params['tickers'].split(",")]
    for t_name in ticker_list:
        m_list = fetcher.get_search_suggestions(t_name)
        if not m_list: continue

        stock = m_list[0]
        sym, name, m_type = stock['symbol'], stock['name'], stock['market']

        df = fetcher.get_ohlcv(sym, m_type, period=params['period'])
        if df is not None:
            df = indicators.add_indicators(df)
            res = strategy_engine.run_backtest(df, params['cap'], params['mode'], params['risk'], params['ratio'])

            with st.expander(f"📊 {name} ({sym}) 결과", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("최종 자산", format_currency(res['final_value'], m_type))
                c2.metric("수익률", f"{res['total_return']:+.2f}%")
                c3.metric("매매 횟수", f"{res['trade_count']}회")
                fig_curve = go.Figure(go.Scatter(x=df.index, y=res['equity_curve'], fill='tozeroy', line=dict(color=COLORS['primary'])))
                fig_curve.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig_curve, width='stretch', key=f"sim_{sym}")

                # 매매 내역 및 누적 결과 표
                st.subheader("📋 상세 매매 기록")
                if res['trades']:
                    trades_df = pd.DataFrame(res['trades'])
                    st.dataframe(trades_df, use_container_width=True)
                else:
                    st.write("해당 기간 동안 발생한 매매 내역이 없습니다.")

if __name__ == "__main__":
    main()
