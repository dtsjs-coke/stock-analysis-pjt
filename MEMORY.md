# Project Memory: Stock Analysis Project

## Context
- **OS:** Android (Termux)
- **Status:** 개발 완료 및 안정화

## Progress Log
- [x] 프로젝트 디렉토리 및 가상환경 구축
- [x] 통합 데이터 엔진 구축 (KR/US 캐싱 완료)
- [x] 기술 지표 엔진 구현 (Pandas 기반 최적화)
- [x] AI 하이브리드 투자 전략 엔진 구현
- [x] Binance 스타일 다크 UI 및 반응형 웹 구축
- [x] 실시간 자동완성 검색 기능 구현 (엔터 분석 연동)
- [x] 즐겨찾기 관리 및 상세 분석 페이지 유기적 연동
- [x] 뉴스 수집 경로 통합 (네이버 기반 KR/US)
- [x] 버그 수정 (Timezone, KeyError, DuplicateID, Sidebar 중복)
- [x] 시뮬레이션 상세 거래 내역 표 출력

## Local Notes
- **검색 엔진:** 통합 종목 캐시(`unified_listings_v3.pkl`)를 통해 초고속 필터링 지원.
- **통화 처리:** KR 주식은 원화, US 주식은 달러($) 및 원화 환산값 병기.
- **데이터 처리:** 미국 주식은 `period`, 한국 주식은 `start date` 필터링으로 최적화.
- **시뮬레이션:** 인과율(Causality)을 준수하는 1-Step 백테스트 로직 적용.
