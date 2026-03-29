# ==============================================================================
# [SOP] Exhibition / Trade Show Scraper
# ==============================================================================
# 국내 주요 전시장(COEX, KINTEX, EXCO, BEXCO)의
# 박람회/전시회 일정을 수집하여 캘린더 이벤트로 변환합니다.
#
# 외부 라이브러리 의존 없이 표준 라이브러리만 사용합니다.
# ==============================================================================

import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
from datetime import datetime, timedelta
from html.parser import HTMLParser

# 프로젝트 경로
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_DIR, '.tmp')

# 전시회 카테고리 색상 (Dark Green)
EXHIBITION_COLOR = '#065f46'


def strip_html(text):
    """HTML 태그를 제거하고 텍스트만 반환"""
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
            # 인코딩 시도
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


def scrape_coex(months_ahead=4):
    """
    COEX 전시 일정을 스크래핑합니다.
    """
    print("  [COEX] 전시 일정 스크래핑 중...")
    events = []
    
    url = 'https://www.coex.co.kr/event/full-schedules/'
    html = safe_request(url)
    if not html:
        print("  [COEX] Exhibition 0건 (연결 불가능 또는 페이지 로드 실패)")
        return events

    # 날짜 패턴: YYYY-MM-DD ~ YYYY-MM-DD 또는 YYYY.MM.DD ~ YYYY.MM.DD
    date_pattern = re.compile(r'(\d{4}[.-]\d{2}[.-]\d{2})\s*[-~]\s*(\d{4}[.-]\d{2}[.-]\d{2})')
    link_pattern = re.compile(r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)

    matches = link_pattern.findall(html)

    exhibition_keywords = ('전시', '박람회', '엑스포', 'expo', 'show', 'fair', '페어', '페스타', '포럼')

    for href, title_html in matches:
        title_html = re.sub(r'<[^>]+>', '', title_html).strip()
        if len(title_html) < 5:
            continue

        # 전시회 관련 키워드 필터
        if not any(kw in title_html.lower() for kw in exhibition_keywords):
            continue

        # 주변 텍스트에서 날짜 찾기
        title_pos = html.find(title_html)
        if title_pos < 0:
            continue
        surrounding = html[max(0, title_pos - 200):min(len(html), title_pos + 300)]
        date_match = date_pattern.search(surrounding)
        if not date_match:
            continue

        start_str = date_match.group(1).replace('.', '-')
        end_str = date_match.group(2).replace('.', '-')

        # end 날짜를 FullCalendar exclusive end로 변환 (+1일)
        try:
            end_dt = datetime.strptime(end_str, '%Y-%m-%d')
            end_exclusive = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        except ValueError:
            end_exclusive = end_str

        events.append({
            'title': title_html,
            'start': start_str,
            'end': end_exclusive,
            'color': EXHIBITION_COLOR,
            'extendedProps': {
                'category': 'exhibition',
                'categoryLabel': '박람회 및 전시회',
                'description': f'장소: COEX (서울)\n기간: {start_str} ~ {end_str}',
                'price': '자세한 내용은 홈페이지 확인',
                'url': 'https://www.coex.co.kr/event/full-schedules/',
                'source': 'web_coex',
            }
        })

    if events:
        # 중복 제거
        seen = set()
        unique = []
        for ev in events:
            key = (ev['title'], ev['start'])
            if key not in seen:
                seen.add(key)
                unique.append(ev)
        events = unique
        print(f"  [COEX] {len(events)}건 수집 완료")
    else:
        print("  [COEX] Exhibition 0건 (연결 불가능 또는 해당되는 행사 없음)")

    return events


def scrape_kintex(months_ahead=4):
    """
    킨텍스 전시 일정을 스크래핑합니다.
    """
    print("  [KINTEX] 전시 일정 스크래핑 중...")
    events = []
    now = datetime.now()

    for month_offset in range(months_ahead):
        target = now + timedelta(days=30 * month_offset)
        year = target.year
        month = target.month

        # 여러 URL 패턴 시도
        for url in [
            f'https://www.kintex.com/kor/contentsid/640/index.html?Year={year}&Month={month:02d}',
            f'https://www.kintex.com/kor/EventSchedule/EventScheduleList.asp?Year={year}&Month={month:02d}',
        ]:
            html = safe_request(url)
            if html:
                break
        else:
            continue

        date_pattern = re.compile(r'(\d{4}[.-]\d{2}[.-]\d{2})\s*[-~]\s*(\d{4}[.-]\d{2}[.-]\d{2})')
        link_pattern = re.compile(r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
        matches = link_pattern.findall(html)

        exhibition_keywords = ('전시', '박람회', '엑스포', 'expo', 'show', 'fair', '페어', '페스타', '포럼')

        for href, title_html in matches:
            title_html = re.sub(r'<[^>]+>', '', title_html).strip()
            if len(title_html) < 5:
                continue
            if not any(kw in title_html.lower() for kw in exhibition_keywords):
                continue

            title_pos = html.find(title_html)
            if title_pos < 0:
                continue
            surrounding = html[max(0, title_pos - 200):min(len(html), title_pos + 300)]
            date_match = date_pattern.search(surrounding)
            if not date_match:
                continue

            start_str = date_match.group(1).replace('.', '-')
            end_str = date_match.group(2).replace('.', '-')

            try:
                end_dt = datetime.strptime(end_str, '%Y-%m-%d')
                end_exclusive = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            except ValueError:
                end_exclusive = end_str

            events.append({
                'title': title_html + ' (KINTEX)',
                'start': start_str,
                'end': end_exclusive,
                'color': EXHIBITION_COLOR,
                'extendedProps': {
                    'category': 'exhibition',
                    'categoryLabel': '박람회 및 전시회',
                    'description': f'장소: KINTEX (킨텍스)\n기간: {start_str} ~ {end_str}',
                    'price': '킨텍스 홈페이지 확인',
                    'url': 'https://www.kintex.com',
                    'source': 'web_kintex',
                }
            })

    if events:
        seen = set()
        unique = []
        for ev in events:
            key = (ev['title'], ev['start'])
            if key not in seen:
                seen.add(key)
                unique.append(ev)
        events = unique
        print(f"  [KINTEX] {len(events)}건 수집 완료")
    else:
        print("  [KINTEX] 전시회 0건 (해당 일정 없거나 연결 불가능)")

    return events


def scrape_exco(months_ahead=4):
    """엑스코(대구) 전시 일정 스크래핑"""
    print("  [EXCO] 전시 일정 스크래핑 중...")
    events = []
    now = datetime.now()

    for month_offset in range(months_ahead):
        target = now + timedelta(days=30 * month_offset)
        year = target.year
        month = target.month

        url = f'https://exco.co.kr/kor/Event/eventList.html?year={year}&month={month:02d}'
        html = safe_request(url)
        if not html:
            continue

        date_pattern = re.compile(r'(\d{4}[.-]\d{2}[.-]\d{2})\s*[-~]\s*(\d{4}[.-]\d{2}[.-]\d{2})')
        link_pattern = re.compile(r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
        matches = link_pattern.findall(html)

        exhibition_keywords = ('전시', '박람회', '엑스포', 'expo', 'show', 'fair', '페어', '페스타', '포럼', '전시회')

        for href, title_html in matches:
            title_html = re.sub(r'<[^>]+>', '', title_html).strip()
            if len(title_html) < 5:
                continue
            if not any(kw in title_html.lower() for kw in exhibition_keywords):
                continue

            title_pos = html.find(title_html)
            if title_pos < 0:
                continue
            surrounding = html[max(0, title_pos - 200):min(len(html), title_pos + 300)]
            date_match = date_pattern.search(surrounding)
            if not date_match:
                continue

            start_str = date_match.group(1).replace('.', '-')
            end_str = date_match.group(2).replace('.', '-')

            try:
                end_dt = datetime.strptime(end_str, '%Y-%m-%d')
                end_exclusive = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            except ValueError:
                end_exclusive = end_str

            events.append({
                'title': title_html + ' (EXCO)',
                'start': start_str,
                'end': end_exclusive,
                'color': EXHIBITION_COLOR,
                'extendedProps': {
                    'category': 'exhibition',
                    'categoryLabel': '박람회 및 전시회',
                    'description': f'장소: EXCO (대구)\n기간: {start_str} ~ {end_str}',
                    'price': 'EXCO 홈페이지 확인',
                    'url': 'https://exco.co.kr',
                    'source': 'web_exco',
                }
            })

    if events:
        seen = set()
        unique = []
        for ev in events:
            key = (ev['title'], ev['start'])
            if key not in seen:
                seen.add(key)
                unique.append(ev)
        events = unique
        print(f"  [EXCO] {len(events)}건 수집 완료")
    else:
        print("  [EXCO] 전시회 0건 (해당 일정 없거나 연결 불가능)")

    return events


def scrape_bexco(months_ahead=4):
    """벡스코(부산) 전시 일정 스크래핑"""
    print("  [BEXCO] 전시 일정 스크래핑 중...")
    events = []
    now = datetime.now()

    for month_offset in range(months_ahead):
        target = now + timedelta(days=30 * month_offset)
        year = target.year
        month = target.month

        for url in [
            f'https://www.bexco.co.kr/kor/EventSchedule/SchList.do?year={year}&month={month:02d}',
            f'https://www.bexco.co.kr/kor/EventSchedule/SchCalendar.do?year={year}&month={month:02d}',
        ]:
            html = safe_request(url)
            if html:
                break
        else:
            continue

        date_pattern = re.compile(r'(\d{4}[.-]\d{2}[.-]\d{2})\s*[-~]\s*(\d{4}[.-]\d{2}[.-]\d{2})')
        link_pattern = re.compile(r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
        matches = link_pattern.findall(html)

        exhibition_keywords = ('전시', '박람회', '엑스포', 'expo', 'show', 'fair', '페어', '페스타', '포럼', '전시회', '컨벤션')

        for href, title_html in matches:
            title_html = re.sub(r'<[^>]+>', '', title_html).strip()
            if len(title_html) < 5:
                continue
            if not any(kw in title_html.lower() for kw in exhibition_keywords):
                continue

            title_pos = html.find(title_html)
            if title_pos < 0:
                continue
            surrounding = html[max(0, title_pos - 200):min(len(html), title_pos + 300)]
            date_match = date_pattern.search(surrounding)
            if not date_match:
                continue

            start_str = date_match.group(1).replace('.', '-')
            end_str = date_match.group(2).replace('.', '-')

            try:
                end_dt = datetime.strptime(end_str, '%Y-%m-%d')
                end_exclusive = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            except ValueError:
                end_exclusive = end_str

            events.append({
                'title': title_html + ' (BEXCO)',
                'start': start_str,
                'end': end_exclusive,
                'color': EXHIBITION_COLOR,
                'extendedProps': {
                    'category': 'exhibition',
                    'categoryLabel': '박람회 및 전시회',
                    'description': f'장소: BEXCO (부산)\n기간: {start_str} ~ {end_str}',
                    'price': 'BEXCO 홈페이지 확인',
                    'url': 'https://www.bexco.co.kr',
                    'source': 'web_bexco',
                }
            })

    if events:
        seen = set()
        unique = []
        for ev in events:
            key = (ev['title'], ev['start'])
            if key not in seen:
                seen.add(key)
                unique.append(ev)
        events = unique
        print(f"  [BEXCO] {len(events)}건 수집 완료")
    else:
        print("  [BEXCO] 전시회 0건 (해당 일정 없거나 연결 불가능)")

    return events


def collect_all_exhibitions(months_ahead=4):
    """
    국내 주요 박람회/전시회 일정을 수집합니다.
    
    Args:
        months_ahead: 현재 월부터 몇 개월 앞까지 수집할지 
    
    Returns:
        list: 캘린더에 추가할 전시회 이벤트 목록
    """
    print("============================================================")
    print("=== 국내 박람회/전시회 일정 수집 중 ===")
    print("============================================================")

    all_events = []
    scrapers = [
        ('COEX', scrape_coex),
        ('KINTEX', scrape_kintex),
        ('EXCO', scrape_exco),
        ('BEXCO', scrape_bexco),
    ]

    for name, scraper_fn in scrapers:
        try:
            venue_events = scraper_fn(months_ahead)
            all_events.extend(venue_events)
        except Exception as e:
            print(f"  [오류] {name} 스크래핑 중 오류: {e}")

    # 날짜 필터링: 오늘 이후만 유지
    before_filter = len(all_events)
    filtered = [ev for ev in all_events if ev.get('end', ev.get('start', '')) >= datetime.now().strftime('%Y-%m-%d')]
    if before_filter > 0 and len(filtered) < before_filter:
        print(f"  [날짜 필터] {before_filter - len(filtered)}건 과거 전시회 제외")
    all_events = filtered

    print(f"\n[결과] 박람회/전시회 일정 수집 {len(all_events)}건")
    return all_events


if __name__ == "__main__":
    """단독 실행 테스트"""
    events = collect_all_exhibitions(months_ahead=3)

    print("\n============================================================")
    print("=== 수집 결과 미리보기 ===")

    if events:
        for i, ev in enumerate(events[:10]):
            end_str = f" ~ {ev['end']}" if 'end' in ev else ''
            print(f"  {i + 1}. [{ev['start']}{end_str}] {ev['title']}")
        if len(events) > 10:
            print(f"  ... 외 {len(events) - 10}건")
    else:
        print("  수집된 전시회가 없습니다.")
