"""
==========================================================================
[SOP] 세종시 산하기관 입찰정보 스크래퍼
==========================================================================
세종특별자치시 산하 공공기관들의 입찰공고 정보를 수집하여
event_data.js에 반영할 수 있는 JSON 형태로 변환합니다.

대상 기관:
  1. 세종도시교통공사 (www.sctc.kr)
  2. 세종특별자치시시설관리공단 (www.sjsisul.or.kr)
  3. 세종특별자치시사회서비스원 (www.sjpass.or.kr)
  4. 세종문화관광재단 (www.sjcf.or.kr)
  5. 세종인재평생교육진흥원 (www.sjile.or.kr)
  6. 세종테크노파크 (sjtp.or.kr)
  7. 세종신용보증재단 (www.sjsinbo.or.kr)
  8. 세종특별자치시로컬푸드주식회사 (sjlocalfood.or.kr)
  9. 세종창조경제혁신센터 (sejong.ccei.creativekorea.or.kr)
  10. 세종특별자치시보건환경연구원 (sejong.go.kr 산하)
  11. 세종특별자치시농업기술센터 (adtc.sejong.go.kr)
  12. 세종남부·북부소방서 (sejong.go.kr/fire.do)

실행 주기: 매주 월, 수, 금 (update_calendar_data.py에서 호출)
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from html.parser import HTMLParser
import ssl

# SSL 인증서 검증 무시 (일부 공공기관 사이트 보안 설정 대응)
ssl._create_default_https_context = ssl._create_unverified_context


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, '.tmp')

# ── 유틸리티 ──────────────────────────────────────────────────────────────

class SimpleHTMLTextExtractor(HTMLParser):
    """HTML 태그를 제거하고 텍스트만 추출하는 간이 파서"""
    def __init__(self):
        super().__init__()
        self.result = []
    def handle_data(self, data):
        self.result.append(data.strip())
    def get_text(self):
        return ' '.join(filter(None, self.result))

def strip_html(html_str):
    """HTML 태그를 제거하고 순수 텍스트 반환"""
    extractor = SimpleHTMLTextExtractor()
    try:
        extractor.feed(html_str)
        return extractor.get_text()
    except:
        return html_str

def safe_request(url, timeout=15, encoding='utf-8'):
    """안전한 HTTP 요청 래퍼"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            # 여러 인코딩 시도
            for enc in [encoding, 'utf-8', 'euc-kr', 'cp949']:
                try:
                    return raw.decode(enc)
                except (UnicodeDecodeError, LookupError):
                    continue
            return raw.decode('utf-8', errors='replace')
    except urllib.error.URLError as e:
        print(f"  [네트워크 오류] {url}: {e}")
        return None
    except Exception as e:
        print(f"  [요청 실패] {url}: {e}")
        return None

def parse_korean_date(date_str):
    """
    다양한 한국어 날짜 포맷을 YYYY-MM-DD로 파싱 시도
    지원 포맷: YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD, YYYYMMDD
    """
    if not date_str:
        return None
    date_str = date_str.strip()
    
    patterns = [
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', '%Y.%m.%d'),
        (r'(\d{4})/(\d{1,2})/(\d{1,2})', '%Y/%m/%d'),
        (r'(\d{8})', None),  # YYYYMMDD
    ]
    
    for pattern, fmt in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if fmt:
                    dt = datetime.strptime(match.group(), fmt)
                else:
                    dt = datetime.strptime(match.group(), '%Y%m%d')
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    return None

# ── 기관별 컬러 매핑 ──────────────────────────────────────────────────────

# 세종 산하기관 입찰정보 전용 컬러 (Teal/보라)
INSTITUTION_COLOR = '#0d9488'  # Teal 600

INSTITUTION_REGISTRY = {
    'sctc': {
        'name': '세종도시교통공사',
        'short': '교통공사',
        'url': 'https://www.sctc.kr',
        'bid_url': 'https://www.sctc.kr/bbs/BBSS1612021757537630',
        'desc': '시내버스, BRT 등 교통 서비스 운영',
        'color': INSTITUTION_COLOR,
    },
    'sjsisul': {
        'name': '세종시설관리공단',
        'short': '시설공단',
        'url': 'https://www.sjsisul.or.kr',
        'bid_url': 'https://www.sjsisul.or.kr/bbs/content/245',
        'desc': '공영주차장, 환경시설, 체육시설 등 관리',
        'color': INSTITUTION_COLOR,
    },
    'sjpass': {
        'name': '세종사회서비스원',
        'short': '사회서비스원',
        'url': 'https://sj.pass.or.kr',
        'bid_url': 'https://sj.pass.or.kr/menu.es?mid=a10502010000',
        'desc': '사회복지 서비스 제공 및 정책 연구',
        'color': INSTITUTION_COLOR,
    },
    'sjcf': {
        'name': '세종문화관광재단',
        'short': '문화관광재단',
        'url': 'https://www.sjcf.or.kr',
        'bid_url': 'https://www.sjcf.or.kr/bid/list.do?key=2111060067',
        'desc': '문화예술 공연, 축제 및 관광 활성화',
        'color': INSTITUTION_COLOR,
    },
    'sjile': {
        'name': '세종인재평생교육진흥원',
        'short': '평생교육원',
        'url': 'https://www.sjile.or.kr',
        'bid_url': 'https://www.sjile.or.kr/bbs/board.do?menuId=MN050202',
        'desc': '인재 양성 및 평생교육 프로그램 운영',
        'color': INSTITUTION_COLOR,
    },
    'sjtp': {
        'name': '세종테크노파크',
        'short': '테크노파크',
        'url': 'https://sjtp.or.kr',
        'bid_url': 'https://sjtp.or.kr/cop/bbs/selectBoardList.do?bbsId=BBSMSTR_000000000006',
        'desc': '지역 산업 육성 및 기업 지원',
        'color': INSTITUTION_COLOR,
    },
    'sjsinbo': {
        'name': '세종신용보증재단',
        'short': '신용보증재단',
        'url': 'https://sjsinbo.or.kr',
        'bid_url': 'https://sjsinbo.or.kr/sub060105',
        'desc': '지역 소상공인 금융 지원',
        'color': INSTITUTION_COLOR,
    },
    'sjlocal': {
        'name': '세종로컬푸드',
        'short': '로컬푸드',
        'url': 'https://www.sjlocal.or.kr',
        'bid_url': 'https://www.sjlocal.or.kr/board/post/notice',
        'desc': '로컬푸드 직매장(싱싱장터) 운영',
        'color': INSTITUTION_COLOR,
    },
    'sjccei': {
        'name': '세종창조경제혁신센터',
        'short': '창조경제센터',
        'url': 'https://sejong.ccei.creativekorea.or.kr',
        'bid_url': 'https://sejong.ccei.creativekorea.or.kr/service/business_list.do',
        'desc': '창업 지원 및 혁신 생태계 조성',
        'color': INSTITUTION_COLOR,
    },
    'sjheri': {
        'name': '세종보건환경연구원',
        'short': '보건환경연구원',
        'url': 'https://www.sejong.go.kr/heri.do',
        'bid_url': 'https://www.sejong.go.kr/heri/sub04_01.do',
        'desc': '보건환경 조사·연구 및 시험·검사',
        'color': INSTITUTION_COLOR,
    },
    'sjadtc': {
        'name': '세종농업기술센터',
        'short': '농업기술센터',
        'url': 'http://adtc.sejong.go.kr',
        'bid_url': 'http://adtc.sejong.go.kr/sub04_01.do',
        'desc': '농업인 교육·상담 및 기술 보급',
        'color': INSTITUTION_COLOR,
    },
    'sjfire': {
        'name': '세종소방본부',
        'short': '소방본부',
        'url': 'https://www.sejong.go.kr/fire.do',
        'bid_url': 'https://www.sejong.go.kr/fire/sub04_01.do',
        'desc': '세종남부·북부 소방서 관할 소방업무',
        'color': INSTITUTION_COLOR,
    },
}



# ── 나라장터 API 연동 (공통 조달 정보) ───────────────────────────────────

def fetch_g2b_sejong_bids(api_key):
    """
    조달청 나라장터 API에서 세종시 관련 기관 입찰 공고를 검색합니다.
    세종 산하기관들은 나라장터에도 공고를 등록하는 경우가 많습니다.
    """
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("[정보] 나라장터 API 키 미설정. 세종 산하기관 공고는 웹 스크래핑으로 대체합니다.")
        return []

    print("[나라장터 API] 세종시 산하기관 입찰공고 검색 중...")
    
    base_url = 'http://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServc04'
    
    now = datetime.now()
    start_date = (now - timedelta(days=7)).strftime('%Y%m%d0000')  # 7일 전부터
    end_date = (now + timedelta(days=90)).strftime('%Y%m%d2359')   # 3개월 뒤까지
    
    # 세종시 관련 키워드로 검색
    search_keywords = ['세종', '세종시', '세종특별자치시']
    events = []
    
    for keyword in search_keywords:
        params = {
            'serviceKey': api_key,
            'numOfRows': '20',
            'pageNo': '1',
            'inqryDiv': '1',
            'inqryBgnDt': start_date,
            'inqryEndDt': end_date,
            'ntceInsttNm': keyword,  # 공고기관명 검색
            'type': 'json'
        }
        
        query_string = urllib.parse.urlencode(params)
        request_url = f"{base_url}?{query_string}"
        
        try:
            req = urllib.request.Request(request_url)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                items = data.get('response', {}).get('body', {}).get('items', [])
                
                if isinstance(items, dict):
                    items = items.get('item', [])
                if isinstance(items, dict):
                    items = [items]
                
                for item in items:
                    title = item.get('bidNtceNm', '알 수 없는 입찰공고')
                    inst_name = item.get('ntceInsttNm', '세종시')
                    write_dt = item.get('bidNtceDt', item.get('bidWrtDt', ''))
                    start_str = write_dt[:8] if len(write_dt) >= 8 else now.strftime('%Y%m%d')
                    formatted_start = f"{start_str[:4]}-{start_str[4:6]}-{start_str[6:8]}"
                    
                    # 중복 방지를 위한 간단한 ID 생성
                    bid_no = item.get('bidNtceNo', '')
                    
                    events.append({
                        'title': f"[{inst_name[:6]}] {title[:30]}",
                        'start': formatted_start,
                        'color': INSTITUTION_COLOR,
                        'extendedProps': {
                            'category': 'sejong_inst',
                            'categoryLabel': '세종 산하기관 입찰',
                            'description': f"공고명: {title}\n기관: {inst_name}\n공고번호: {bid_no}",
                            'price': '나라장터 입찰',
                            'url': item.get('bidNtceDtlUrl', 'https://www.g2b.go.kr'),
                            'source': 'g2b_api',
                            'bidNo': bid_no,
                        }
                    })
                    
        except Exception as e:
            print(f"  [API 오류] 키워드 '{keyword}' 검색 실패: {e}")
    
    # 중복 제거 (공고번호 기준)
    seen = set()
    unique_events = []
    for ev in events:
        bid_no = ev['extendedProps'].get('bidNo', '')
        if bid_no and bid_no in seen:
            continue
        seen.add(bid_no)
        unique_events.append(ev)
    
    print(f"  [수집 완료] 나라장터 세종 관련 공고 {len(unique_events)}건")
    return unique_events


# ── 기관별 웹 스크래핑 (공통 로직) ────────────────────────────────────────

def scrape_generic_board(inst_key):
    """
    기관 홈페이지의 게시판을 일반적인 패턴으로 스크래핑합니다.
    대부분의 공공기관 게시판은 유사한 HTML 테이블/리스트 구조를 가집니다.
    """
    inst = INSTITUTION_REGISTRY.get(inst_key)
    if not inst:
        return []
    
    print(f"  [{inst['name']}] 입찰공고 페이지 스크래핑 시도...")
    
    html = safe_request(inst['bid_url'])
    if not html:
        print(f"  [{inst['name']}] 페이지 접근 실패. 건너뜁니다.")
        return []
    
    events = []
    
    # 게시판 제목과 날짜 패턴 추출 시도
    # 패턴 1: <td> 기반 테이블 구조 (가장 일반적)
    # 패턴 2: <div class="board-list"> 등의 div 구조
    # 패턴 3: <li> 기반 리스트 구조
    
    # 날짜 패턴 검색
    date_pattern = re.compile(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})')
    # 실질적 조달/용역 입찰/공고만 필터링하기 위한 엄격한 키워드 (사업소개, 단순 메뉴 제외)
    bid_keywords = ['입찰', '용역', '견적', '물품구매', '제안서', '조달', '수의계약', '지명경쟁', '제한경쟁', '과업지시서']
    exclude_keywords = ['결과', '설명회', '안내문', '사전규격', '합격자', '면접', '사업소개', '취소', '연기', '계획', '실적', '현황', '소개', '위원회', '추진현황', '모집']
    
    # <a> 태그에서 제목 추출
    link_pattern = re.compile(
        r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE
    )
    
    matches = link_pattern.findall(html)
    
    for href, title_html in matches:
        title = strip_html(title_html).strip()
        if not title or len(title) < 12:
            continue
            
        # 입찰 관련 엄격한 키워드가 포함되고, 결과/안내 등 제외 키워드가 없을 때만 필터링
        is_bid_related = any(kw in title for kw in bid_keywords)
        is_excluded = any(kw in title for kw in exclude_keywords)
        if not is_bid_related or is_excluded:
            continue
        
        # 주변 텍스트에서 날짜 추출 시도
        title_pos = html.find(title_html)
        if title_pos >= 0:
            surrounding = html[max(0, title_pos - 200):min(len(html), title_pos + len(title_html) + 200)]
            date_match = date_pattern.search(surrounding)
            date_str = parse_korean_date(date_match.group(1)) if date_match else datetime.now().strftime('%Y-%m-%d')
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # URL 생성 시 HTML 엔티티 치환 (예: &amp; -> &)
        href = href.replace('&amp;', '&')
        if href.startswith('http'):
            full_url = href
        elif href.startswith('/'):
            full_url = inst['url'] + href
        else:
            full_url = inst['bid_url']
        
        events.append({
            'title': f"[{inst['short']}] {title[:35]}",
            'start': date_str,
            'color': inst['color'],
            'extendedProps': {
                'category': 'sejong_inst',
                'categoryLabel': '세종 산하기관 입찰',
                'description': f"기관: {inst['name']}\n({inst['desc']})\n\n공고: {title}",
                'price': f"{inst['name']} 공고",
                'url': full_url,
                'source': f'web_{inst_key}',
            }
        })
    
    if events:
        print(f"  [{inst['name']}] {len(events)}건 수집 완료")
    else:
        print(f"  [{inst['name']}] 입찰공고 0건 (구조 미매칭 또는 현재 공고 없음). 건너뜁니다.")
    
    return events[:10]  # 최대 10건


def generate_placeholder_event(inst_key):
    """
    (미사용) 플레이스홀더는 더 이상 생성하지 않습니다.
    실제 입찰공고가 있을 때만 캘린더에 표시합니다.
    """
    return []


# ── 메인 수집 로직 ────────────────────────────────────────────────────────

def collect_all_sejong_institution_bids(api_key=None):
    """
    모든 세종 산하기관의 입찰정보를 수집합니다.
    
    Returns:
        list: 캘린더에 추가될 이벤트 목록
    """
    print("=" * 60)
    print("=== 세종시 산하기관 입찰정보 수집 시작 ===")
    print("=" * 60)
    
    all_events = []
    
    # 1) 나라장터 API를 통한 세종 관련 입찰 검색
    if api_key:
        g2b_events = fetch_g2b_sejong_bids(api_key)
        all_events.extend(g2b_events)
    
    # 2) 각 기관 홈페이지 게시판 스크래핑
    for inst_key in INSTITUTION_REGISTRY:
        try:
            inst_events = scrape_generic_board(inst_key)
            all_events.extend(inst_events)
        except Exception as e:
            print(f"  [오류] {inst_key} 스크래핑 실패: {e}")
            # 실패 시 건너뜀 — 실제 공고만 캘린더에 추가
    
    print(f"\n[총 수집] 세종 산하기관 입찰정보 총 {len(all_events)}건")
    return all_events


def save_to_json(events, filename='sejong_inst_bids.json'):
    """수집된 데이터를 JSON 파일로 저장"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    
    print(f"[저장] {filepath} 에 {len(events)}건 저장 완료")
    return filepath


# ── 엔트리포인트 ──────────────────────────────────────────────────────────

def main():
    """독립 실행 시 테스트용"""
    # .env에서 API 키 로드
    env_path = os.path.join(PROJECT_DIR, '.env')
    api_key = None
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2 and parts[0].strip() == 'DATA_GO_KR_API_KEY':
                        api_key = parts[1].strip()
    
    events = collect_all_sejong_institution_bids(api_key)
    save_to_json(events)
    
    # 콘솔 출력 (확인용)
    print("\n" + "=" * 60)
    print("=== 수집 결과 미리보기 ===")
    for i, ev in enumerate(events[:5], 1):
        print(f"  {i}. [{ev['start']}] {ev['title']}")
    if len(events) > 5:
        print(f"  ... 외 {len(events) - 5}건")
    
    return events


if __name__ == '__main__':
    main()
