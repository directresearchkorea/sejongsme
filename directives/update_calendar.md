# Calendar Update Directive (캘린더 주 3회 업데이트 로직)

**Goal:** 매주 월, 수, 금요일마다 중소기업, 사회조사 입찰정보, 국가/지역 전시회 데이터 및 **세종시 산하기관 입찰공고**를 검색하여 캘린더 데이터를 갱신한다. 업데이트 시 현재부터 최소 3개월 치의 데이터를 탐색하며, 연말(12월)까지 공개된 주요 행사가 있다면 포함한다.

**Schedule:** 매주 월(Mon), 수(Wed), 금(Fri) 특정 시간 동작

**Execution Scripts:**
- `execution/update_calendar_data.py` — 메인 업데이트 스크립트 (통합 오케스트레이터)
- `execution/scrape_sejong_institutions.py` — 세종시 산하기관 입찰정보 스크래퍼

**Expected Outcome:**
1. 조달청 나라장터 Open API 연동하여 입찰 정보(사회조사 등) 검색 (3개월 ~ 12월)
2. 세종시 공지사항 / KINTEX / COEX 등의 행사 공고 크롤링 혹은 API 스크래핑
3. **세종시 산하기관 12개 입찰공고 수집** (아래 목록 참조)
4. 추출한 데이터를 JSON/JS Array 형식으로 가공하여 `event_data.js` 파일 갱신
5. 페이지 접속 시 `index.html`이 갱신된 파일을 로드하여 사용자 화면에 최신 일정 표출

## 세종시 산하기관 입찰정보 수집 대상 (12개 기관)

| # | 기관명 | 약칭 | 홈페이지 | 입찰/공고 URL | 비고 |
|---|--------|------|----------|---------------|------|
| 1 | 세종도시교통공사 | 교통공사 | www.sctc.kr | /bbs/BBSS1612021757537630 | 공지사항 (입찰 포함) |
| 2 | 세종시설관리공단 | 시설공단 | www.sjsisul.or.kr | /bbs/content/245 | 공영주차장, 환경·체육시설 |
| 3 | 세종사회서비스원 | 사회서비스원 | sj.pass.or.kr | /menu.es?mid=a10502010000 | 사회복지, 정책연구 |
| 4 | 세종문화관광재단 | 문화관광재단 | www.sjcf.or.kr | /bid/list.do?key=2111060067 | 문화예술, 축제 |
| 5 | 세종인재평생교육진흥원 | 평생교육원 | www.sjile.or.kr | MN050202 게시판 | 인재양성, 평생교육 |
| 6 | 세종테크노파크 | 테크노파크 | sjtp.or.kr | 공고·알림 > 계약정보 | 산업육성, 기업지원 |
| 7 | 세종신용보증재단 | 신용보증재단 | sjsinbo.or.kr | /sub060105 | 소상공인 금융지원 |
| 8 | 세종로컬푸드 | 로컬푸드 | sjlocal.or.kr | /board/post/notice | 싱싱장터 운영 |
| 9 | 세종창조경제혁신센터 | 창조경제센터 | sejong.ccei.creativekorea.or.kr | 사업공고 리스트 | 창업지원, 혁신생태계 |
| 10 | 세종보건환경연구원 | 보건환경연구원 | sejong.go.kr/heri.do | /heri/sub04_01.do | 보건환경 조사·연구 |
| 11 | 세종농업기술센터 | 농업기술센터 | adtc.sejong.go.kr | /sub04_01.do | 농업인 교육·기술보급 |
| 12 | 세종소방본부 | 소방본부 | sejong.go.kr/fire.do | /fire/sub04_01.do | 남부·북부소방서 |

## UI 카테고리 매핑

| 카테고리 key | 라벨 | 색상 | 설명 |
|-------------|------|------|------|
| `sme` | 중소기업 지원사업 | #71717a (Grey) | 정부/공공기관 공고 |
| `sejong` | 세종시 지원사업 | #ea580c (Orange) | 세종 지역 정책 |
| `exhibition` | 박람회 및 전시회 | #065f46 (Dark Green) | COEX, KINTEX 등 |
| `chungcheong` | 충청권 행사 | #db2777 (Pink) | 지역 박람회 |
| `bid` | 사회조사 입찰정보 | #6366f1 (Indigo) | 조달청, 국책연구원 |
| `sejong_inst` | 세종 산하기관 입찰 | #0d9488 (Teal) | 12개 산하기관 공고 |

**Notes / Edge Cases:**
- 웹 사이트의 DOM 구조가 변경되었을 경우 스크래퍼가 멈출 수 있으므로, 공공 API 활용을 최우선으로 진행할 것 (예: data.go.kr API 팝업)
- 오류 발생 시 이전 데이터 `event_data.js.bak`을 가져오도록 백업 로직 구성 완료
- 나라장터에 동시 등록된 세종기관 입찰건은 중복 제거 로직으로 처리
- 스크래핑 실패 시 또는 현재 공고가 없으면 해당 기관은 건너뜀 (실제 입찰건만 캘린더에 추가)
- **기관 URL이 변경될 경우** `execution/scrape_sejong_institutions.py`의 `INSTITUTION_REGISTRY` 딕셔너리를 업데이트할 것
