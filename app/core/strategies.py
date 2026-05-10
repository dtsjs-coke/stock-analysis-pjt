import pandas as pd
import numpy as np

class StrategyEngine:
    @staticmethod
    def get_market_signal(df, sentiment_score):
        """
        모든 분석 기법의 결과를 상세하게 정리하여 반환
        """
        if df is None or df.empty:
            return 50, "데이터 부족", [{"technique": "종합", "verdict": "중립", "signal": "🟡", "reason": "데이터 없음"}]
            
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        score = 50
        
        # 1. RSI
        if latest['RSI'] < 30:
            signals.append({"technique": "RSI", "verdict": "매수", "signal": "🟢", "reason": "과매도 구간 진입"})
            score += 20
        elif latest['RSI'] > 70:
            signals.append({"technique": "RSI", "verdict": "매도", "signal": "🔴", "reason": "과매수 구간 경계"})
            score -= 20
        else:
            signals.append({"technique": "RSI", "verdict": "관망", "signal": "🟡", "reason": "중립 구간 유지"})
            
        # 2. 이동평균선
        if latest['MA20'] > latest['MA60']:
            signals.append({"technique": "이동평균", "verdict": "매수", "signal": "🟢", "reason": "정배열 상승 추세"})
            score += 15
        else:
            signals.append({"technique": "이동평균", "verdict": "매도", "signal": "🔴", "reason": "역배열 하락 추세"})
            score -= 15

        # 3. 볼린저 밴드
        if latest['Close'] > latest['BB_Upper']:
            signals.append({"technique": "볼린저밴드", "verdict": "매도", "signal": "🔴", "reason": "상단 이탈 과열"})
            score -= 10
        elif latest['Close'] < latest['BB_Lower']:
            signals.append({"technique": "볼린저밴드", "verdict": "매수", "signal": "🟢", "reason": "하단 이탈 과매도"})
            score += 10
        else:
            signals.append({"technique": "볼린저밴드", "verdict": "관망", "signal": "🟡", "reason": "밴드 내 안정화"})

        # 4. MACD
        if latest['MACD'] > latest['MACD_Signal']:
            signals.append({"technique": "MACD", "verdict": "매수", "signal": "🟢", "reason": "골든크로스 상태"})
            score += 15
        else:
            signals.append({"technique": "MACD", "verdict": "매도", "signal": "🔴", "reason": "데드크로스/약세"})
            score -= 15

        # 5. 감성 분석
        if sentiment_score > 0.1:
            signals.append({"technique": "뉴스감성", "verdict": "매수", "signal": "🟢", "reason": "긍정적인 여론"})
            score += 10
        elif sentiment_score < -0.1:
            signals.append({"technique": "뉴스감성", "verdict": "매도", "signal": "🔴", "reason": "부정적인 여론"})
            score -= 10
        else:
            signals.append({"technique": "뉴스감성", "verdict": "관망", "signal": "🟡", "reason": "뉴스 중립"})
            
        score = max(0, min(100, score))
        if score >= 70: label = "강력 매수"
        elif score >= 55: label = "매수"
        elif score >= 45: label = "관망/보유"
        elif score >= 30: label = "매도"
        else: label = "강력 매도"
        
        return score, label, signals

    @staticmethod
    def run_backtest(df, initial_capital, strategy_type, risk_profile="중립형", trade_ratio=0.5):
        """
        분할 매매 및 투자 성향을 반영한 포트폴리오 시뮬레이션
        trade_ratio: 1회 매매 시 자산의 몇 %를 사용할지 (0.1 ~ 1.0)
        risk_profile: 보수적(매수신호 강할 때만), 중립, 공격적(잦은 매매)
        """
        capital = float(initial_capital)
        shares = 0
        avg_price = 0
        trades = []
        equity_curve = []
        
        # 성향에 따른 매수/매도 점수 임계치
        thresholds = {"보수적": 70, "중립": 50, "공격적": 30}
        buy_t = thresholds.get(risk_profile, 50)
        sell_t = 100 - buy_t

        for i in range(20, len(df)):
            current_price = df.iloc[i]['Close']
            _, _, signals = StrategyEngine.get_market_signal(df.iloc[:i+1], 0)
            
            buy_count = sum(1 for s in signals if s['verdict'] == '매수')
            sell_count = sum(1 for s in signals if s['verdict'] == '매도')
            
            buy_signal = (buy_count - sell_count) > (buy_t / 20)
            sell_signal = (sell_count - buy_count) > (sell_t / 20)
            
            # CLI 디버깅 출력
            if i % 50 == 0: # 너무 많으면 터미널 도배되므로 50일마다 출력
                print(f"[{df.index[i].strftime('%Y-%m-%d')}] 매수신호:{buy_count}/매도신호:{sell_count} -> {'매수판단' if buy_signal else '매도판단' if sell_signal else '관망'}")

            # 매매 실행
            if buy_signal and capital >= (current_price * trade_ratio):
                buy_amount = capital * trade_ratio
                qty = int(buy_amount // current_price)
                if qty > 0:
                    new_shares = shares + qty
                    avg_price = ((shares * avg_price) + (qty * current_price)) / new_shares
                    shares = new_shares
                    capital -= (qty * current_price)
                    print(f"  [매수 발생] 수량:{qty}, 가격:{current_price:.0f}, 잔고:{int(capital)}")
                    trades.append({'날짜': df.index[i].strftime('%Y-%m-%d'), '유형': '매수', '수량': qty, '가격': current_price, '평단가': round(avg_price, 2), '잔고': int(capital), '근거': f"매수({buy_count})/매도({sell_count})"})
            
            # 분할 매도
            elif sell_signal and shares > 0:
                qty = int(shares * trade_ratio)
                if qty > 0:
                    shares -= qty
                    capital += (qty * current_price)
                    print(f"  [매도 발생] 수량:{qty}, 가격:{current_price:.0f}, 잔고:{int(capital)}")
                    trades.append({'날짜': df.index[i].strftime('%Y-%m-%d'), '유형': '매도', '수량': qty, '가격': current_price, '평단가': round(avg_price, 2), '잔고': int(capital), '근거': f"매수({buy_count})/매도({sell_count})"})
                
            equity_curve.append(capital + (shares * current_price))
            
        final_val = equity_curve[-1]
        total_return = ((final_val - initial_capital) / initial_capital) * 100
        
        return {
            'final_value': final_val,
            'total_return': total_return,
            'trade_count': len(trades),
            'equity_curve': equity_curve,
            'trades': trades
        }

strategy_engine = StrategyEngine()
