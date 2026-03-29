"""
==========================================================================
[SOP] 세종시 산하기관 입찰정보 스크래퍼
==========================================================================
세종특별자치시 산하 공공기관 입찰공고를 수집하여
event_data.js에 반영할 수 있는 JSON 형태로 변환합니다.

대상 기관:
  1. 교통공사 (www.sctc.kr)
  2. 세종특별자치시설공단 (www.sjsisul.or.kr)
  3. 세종특별자치시사회서비스원 (www.sjpass.or.kr)
  4. 문화관광재단 (www.sjcf.or.kr)
  5. 평생교육원 (www.sjile.or.kr)
  6. 테크노파크 (sjtp.or.kr)
  7. 신용보증재단 (www.sjsinbo.or.kr)
  8. 세종특별자치시로컬푸드주식회사 (sjlocalfood.or.kr)
  9. 창조경제센터 (sejong.ccei.creativekorea.or.kr)
  10. 보건환경연구원 (www.sejong.go.kr/heri.do)
  11. 농업기술센터 (adtc.sejong.go.kr)
  12. 소방본부 (www.sejong.go.kr/fire.do)
==========================================================================
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

# 프로젝트 경로
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, '.tmp')

# 전시회 스크래퍼 임포트 (같은 디렉토리)
try:
    from scrape_exhibitions import collect_all_exhibitions
except ImportError:
    collect_all_exhibitions = None


class SimpleHTMLTextExtractor(HTMLParser):
    """HTML에서 텍스트만 추출하는 파서"""
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_data(self, data):
        self.result.append(data)

    def get_text(self):
        return ''.join(self.result).strip()


def strip_html(text):
    """HTML 태그 제거"""
    extractor = SimpleHTMLTextExtractor()
    try:
        extractor.feed(text)
        return extractor.get_text()
    except Exception:
        return re.sub(r'<[^>]+>', '', text).strip()


def safe_request(url, timeout=15):
    """
    안전한 HTTP 요청. SSL 검증 비활성화 및 User-Agent 설정.
    실패 시 None 반환.
    """
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            raw = response.read()
            for enc in ('utf-8', 'euc-kr', 'cp949'):
                try:
                    return raw.decode(enc)
                except (UnicodeDecodeError, LookupError):
                    continue
            return raw.decode('utf-8', errors='replace')
    except urllib.error.URLError as e:
        print(f"  [네트워크 오류] {url}: {e}")
        return None
    except Exception as e:
        print(f"  [요청 오류] {url}: {e}")
        return None


# 산하기관 입찰 색상 (Teal)
INSTITUTION_COLOR = '#0d9488'

# 세종시 산하기관 레지스트리 (12개 기관)
INSTITUTION_REGISTRY = {
    'sctc': {
        'name': '교통공사',
        'short': '교통',
        'url': 'https://www.sctc.kr',
        'bid_url': 'https://www.sctc.kr/bbs/BBSS1612021757537630',
        'desc': '도시철도, BRT 운영 및 교통 관련 사업',
        'color': INSTITUTION_COLOR,
    },
    'sjsisul': {
        'name': '시설공단',
        'short': '시설공단',
        'url': 'https://www.sjsisul.or.kr',
        'bid_url': 'https://www.sjsisul.or.kr/bbs/content/245',
        'desc': '공영주차장, 환경시설, 체육시설 등 관리',
        'color': INSTITUTION_COLOR,
    },
    'sjpass': {
        'name': '사회서비스원',
        'short': '사회서비스원',
        'url': 'https://sj.pass.or.kr',
        'bid_url': 'https://sj.pass.or.kr/menu.es?mid=a10502010000',
        'desc': '사회복지 관련 정책 및 사업 연구',
        'color': INSTITUTION_COLOR,
    },
    'sjcf': {
        'name': '문화관광재단',
        'short': '문화관광재단',
        'url': 'https://www.sjcf.or.kr',
        'bid_url': 'https://www.sjcf.or.kr/bid/list.do?key=2111060067',
        'desc': '문화예술 축제, 관광 활성화',
        'color': INSTITUTION_COLOR,
    },
    'sjile': {
        'name': '평생교육원',
        'short': '교육',
        'url': 'https://www.sjile.or.kr',
        'bid_url': 'https://www.sjile.or.kr/bbs/board.do?menuId=MN050202',
        'desc': '인재 양성 및 평생 프로그램 운영',
        'color': INSTITUTION_COLOR,
    },
    'sjtp': {
        'name': '테크노파크',
        'short': '테크노파크',
        'url': 'https://sjtp.or.kr',
        'bid_url': 'https://sjtp.or.kr/cop/bbs/selectBoardList.do?bbsId=BBSMSTR_000000000006',
        'desc': '산업 육성 및 기업 지원',
        'color': INSTITUTION_COLOR,
    },
    'sjsinbo': {
        'name': '신용보증재단',
        'short': '신용보증재단',
        'url': 'https://sjsinbo.or.kr',
        'bid_url': 'https://sjsinbo.or.kr/sub060105',
        'desc': '소상공인 금융 지원',
        'color': INSTITUTION_COLOR,
    },
    'sjlocal': {
        'name': '로컬푸드',
        'short': '로컬푸드',
        'url': 'https://www.sjlocal.or.kr',
        'bid_url': 'https://www.sjlocal.or.kr/board/post/notice',
        'desc': '로컬푸드 직매장(마켓) 운영',
        'color': INSTITUTION_COLOR,
    },
    'sjccei': {
        'name': '창조경제센터',
        'short': '창경',
        'url': 'https://sejong.ccei.creativekorea.or.kr',
        'bid_url': 'https://sejong.ccei.creativekorea.or.kr/service/business_list.do',
        'desc': '창업 지원 및 혁신 생태계 조성',
        'color': INSTITUTION_COLOR,
    },
    'sjheri': {
        'name': '보건환경연구원',
        'short': '보건환경연구원',
        'url': 'https://www.sejong.go.kr/heri.do',
        'bid_url': 'https://www.sejong.go.kr/heri/sub04_01.do',
        'desc': '보건환경 조사연구 및 감시검사',
        'color': INSTITUTION_COLOR,
    },
    'sjadtc': {
        'name': '농업기술센터',
        'short': '농업',
        'url': 'http://adtc.sejong.go.kr',
        'bid_url': 'http://adtc.sejong.go.kr/sub04_01.do',
        'desc': '농업인 교육 및 기술 보급',
        'color': INSTITUTION_COLOR,
    },
    'sjfire': {
        'name': '소방본부',
        'short': '소방본부',
        'url': 'https://www.sejong.go.kr/fire.do',
        'bid_url': 'https://www.sejong.go.kr/fire/sub04_01.do',
        'desc': '남부·북부소방서 및 소방 관련',
        'color': INSTITUTION_COLOR,
    },
}


def parse_korean_date(date_str):
    """
    다양한 한국어 날짜 형식을 YYYY-MM-DD로 파싱 시도
    지원 형식: YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD, YYYYMMDD
    """
    date_str = date_str.strip()
    patterns = [
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', '%Y.%m.%d'),
        (r'(\d{4})/(\d{1,2})/(\d{1,2})', '%Y/%m/%d'),
        (r'(\d{8})', None),
    ]

    for pattern, fmt in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if fmt is None:
                    dt = datetime.strptime(match.group(1), '%Y%m%d')
                else:
                    dt = datetime.strptime(match.group(0), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    return None


def fetch_g2b_sejong_bids(api_key):
    """
    나라장터 API로 세종시 관련 입찰공고를 검색합니다.
    세종 산하기관에 해당하는 공고가 포함됩니다.
    """
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("[경고] 공공 API 키 미설정. 나라장터 입찰 정보 스크래핑을 건너뜁니다.")
        return []

    print("[나라장터 API] 세종시 산하기관 입찰 검색 중...")

    base_url = 'http://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServc04'
    now = datetime.now()
    start_date = (now - timedelta(days=7)).strftime('%Y%m%d0000')
    end_date = (now + timedelta(days=90)).strftime('%Y%m%d2359')

    search_keywords = ('세종', '세종시', '세종특별자치시')
    events = []

    for keyword in search_keywords:
        params = {
            'serviceKey': api_key,
            'numOfRows': '20',
            'pageNo': '1',
            'inqryDiv': '1',
            'inqryBgnDt': start_date,
            'inqryEndDt': end_date,
            'ntceInsttNm': keyword,
            'type': 'json',
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
                    inst_name = item.get('ntceInsttNm', '세종')
                    write_dt = item.get('bidNtceDt', '') or item.get('bidWrtDt', '')
                    start_str = write_dt[:8] if len(write_dt) >= 8 else now.strftime('%Y%m%d')
                    formatted_start = f"{start_str[:4]}-{start_str[4:6]}-{start_str[6:]}"
                    bid_no = item.get('bidNtceNo', '')

                    events.append({
                        'title': f"[{inst_name}] {title[:30]}",
                        'start': formatted_start,
                        'color': INSTITUTION_COLOR,
                        'extendedProps': {
                            'category': 'sejong_inst',
                            'categoryLabel': '세종 산하기관 입찰',
                            'description': f"공고명: {title}\n기관: {inst_name}\n공고번호: {bid_no}",
                            'price': '나라장터 세부조회',
                            'url': item.get('bidNtceDtlUrl', 'https://www.g2b.go.kr'),
                            'source': 'g2b_api',
                            'bidNo': bid_no,
                        }
                    })

            print(f"  [API 결과] 키워드 '{keyword}' 검색 결과: {len(items) if items else 0}건")

        except Exception as e:
            print(f"  [수집 완료] 나라장터 세종 관련 {len(events)}건")

    # 중복 제거 (bidNo 기준)
    seen = set()
    unique_events = []
    for ev in events:
        key = ev.get('extendedProps', {}).get('bidNo', '')
        if key and key not in seen:
            seen.add(key)
            unique_events.append(ev)
        elif not key:
            unique_events.append(ev)

    return unique_events


def scrape_generic_board(inst_key):
    """
    범용 홈페이지 게시판 일반 입찰 스크래핑합니다.
    대부분의 공공기관 게시판의 HTML 테이블/리스트 구조에 대응합니다.
    """
    inst = INSTITUTION_REGISTRY.get(inst_key)
    if not inst:
        return []

    print(f"  [{inst['name']}] 입찰 정보 스크래핑 시도...")

    html = safe_request(inst['bid_url'])
    if not html:
        print(f"  [{inst['name']}] 입찰 정보 없음. 건너뜁니다.")
        return []

    events = []

    # 날짜 패턴
    date_pattern = re.compile(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})')

    # 입찰 관련 키워드
    bid_keywords = ('입찰', '용역', '공사', '물품', '구매', '설계', '감리', '위탁', '한정', '제안서')

    # 제외 키워드
    exclude_keywords = ('채용', '전시회', '안내', '인사', '합격', '교육', '소개', '홈페이지', '연혁',
                        '조직', '사업소개', '공고', '전시회', '일정', '현황', '물품', '결과', '공지',
                        '전시회', '행사')

    cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    # 링크와 제목 추출
    link_pattern = re.compile(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
    matches = link_pattern.findall(html)

    for href, title_html in matches:
        title_html = strip_html(title_html).strip()
        if len(title_html) < 12:
            continue

        # 입찰 관련 키워드 확인
        is_bid_related = any(kw in title_html for kw in bid_keywords)
        is_excluded = any(kw in title_html for kw in exclude_keywords)

        if not is_bid_related or is_excluded:
            continue

        # 주변 텍스트에서 날짜 찾기
        title_pos = html.find(title_html)
        if title_pos < 0:
            continue
        surrounding = html[max(0, title_pos - 200):min(len(html), title_pos + 300)]
        date_match = date_pattern.search(surrounding)
        if not date_match:
            continue

        date_str = parse_korean_date(date_match.group(1))
        if not date_str:
            continue

        # URL 정규화
        full_url = href.replace('&amp;', '&')
        if not full_url.startswith('http'):
            if full_url.startswith('/'):
                full_url = inst['url'] + full_url
            else:
                full_url = inst['url'] + '/' + full_url

        events.append({
            'title': f"[{inst['short']}] {title_html[:35]}",
            'start': date_str,
            'color': inst['color'],
            'extendedProps': {
                'category': 'sejong_inst',
                'categoryLabel': '세종 산하기관 입찰',
                'description': f"공고명: {title_html}\n({inst['desc']})\n\n기관: {inst['name']} 홈페이지",
                'price': ' 참조',
                'url': full_url,
                'source': f"web_{inst_key}",
            }
        })

    if events:
        print(f"  [{inst['name']}] 입찰 정보 수집 완료")
    else:
        print(f"  [{inst['name']}] 입찰 0건 (연결 불가능 또는 해당 공고 없음). 건너뜁니다.")

    # 최대 10건
    return events[:10]


def generate_placeholder_event(inst_key):
    """
    (미사용) 플레이스홀더 이벤트 – 현재 사용하지 않습니다.
    입찰 정보가 없을 때 캘린더에 표시합니다.
    """
    pass


def collect_all_sejong_institution_bids(api_key):
    """
    전체 세종 산하기관 입찰정보를 수집합니다.
    
    Returns:
        list: 캘린더에 추가할 이벤트 목록
    """
    print("============================================================")
    print("=== 세종 산하기관 입찰 정보 수집 중 ===")
    print("============================================================")

    all_events = []

    # 1. 나라장터 API (세종시 관련)
    g2b_events = fetch_g2b_sejong_bids(api_key)
    all_events.extend(g2b_events)

    # 2. 개별 기관 웹 스크래핑
    for inst_key in INSTITUTION_REGISTRY:
        try:
            inst_events = scrape_generic_board(inst_key)
            all_events.extend(inst_events)
        except Exception as e:
            print(f"  [오류] {inst_key} 스크래핑 중 오류: {e}")

    # 날짜 필터링: 오늘 기준 과거 90일 이전 제외
    before_filter = len(all_events)
    cutoff = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    all_events = [ev for ev in all_events if ev.get('start', '') >= cutoff]
    if before_filter > 0 and len(all_events) < before_filter:
        print(f"  [날짜 필터] {before_filter - len(all_events)}건 과거 데이터 제외됨")

    print(f"\n[결과] 세종 산하기관 입찰 정보 {len(all_events)}건")

    # 3. 전시회 일정 수집 (scrape_exhibitions.py 연동)
    if collect_all_exhibitions:
        exhibition_events = collect_all_exhibitions(months_ahead=4)
        all_events.extend(exhibition_events)
    else:
        print("[경고] scrape_exhibitions.py를 불러올 수 없어 전시회 수집을 건너뜁니다.")

    return all_events


def save_to_json(events, filename='sejong_inst_bids.json'):
    """수집 데이터를 JSON 파일로 저장"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"[저장] {filepath} 에 {len(events)}건 저장 완료")


def main():
    """단독 실행 테스트용"""
    # .env 로드
    env_path = os.path.join(PROJECT_DIR, '.env')
    api_key = None
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2 and parts[0].strip() == 'DATA_GO_KR_API_KEY':
                        api_key = parts[1].strip()

    events = collect_all_sejong_institution_bids(api_key)
    save_to_json(events)

    print("\n============================================================")
    print("=== 수집 결과 미리보기 ===")
    for i, ev in enumerate(events[:5]):
        print(f"  {i + 1}. [{ev['start']}] {ev['title']}")
    if len(events) > 5:
        print(f"  ... 외 {len(events) - 5}건")


if __name__ == "__main__":
    main()
