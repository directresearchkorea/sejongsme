import os
import sys
import json
import re
import shutil
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# ==============================================================================
# [SOP] Calendar Auto-Updater (통합 API + 스크래핑 연동)
# ==============================================================================
# 조달청 나라장터 API + 세종시 산하기관 입찰정보를 수집하여
# event_data.js를 업데이트합니다.
#
# 실행 주기: 매주 월, 수, 금
# ==============================================================================

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_FILE_PATH = os.path.join(PROJECT_DIR, 'event_data.js')
BACKUP_FILE_PATH = os.path.join(PROJECT_DIR, 'event_data.js.bak')
ENV_FILE_PATH = os.path.join(PROJECT_DIR, '.env')

# 세종 산하기관 스크래퍼 임포트
sys.path.insert(0, os.path.join(PROJECT_DIR, 'execution'))
try:
    from scrape_sejong_institutions import collect_all_sejong_institution_bids
except ImportError:
    print("[경고] scrape_sejong_institutions.py를 찾을 수 없습니다.")
    collect_all_sejong_institution_bids = None


def load_env():
    """환경변수 파일 로드"""
    env_vars = {}
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        env_vars[parts[0].strip()] = parts[1].strip()
    return env_vars


def fetch_g2b_bidding_data(api_key):
    """조달청 나라장터 API에서 '사회조사' 키워드 입찰공고 검색"""
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("[경고] .env에 DATA_GO_KR_API_KEY가 없습니다. 공공데이터포털 API 발급 필요.")
        return []

    print("[API 요청] 조달청 나라장터 입찰공고 중 '사회조사' 키워드 검색 (공공데이터포털)")
    
    base_url = 'http://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServc04'
    
    now = datetime.now()
    start_date = now.strftime('%Y%m%d0000')
    end_date = (now + timedelta(days=90)).strftime('%Y%m%d2359')
    
    params = {
        'serviceKey': api_key,
        'numOfRows': '10',
        'pageNo': '1',
        'inqryDiv': '1',
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date,
        'bidNtceNm': '사회조사',
        'type': 'json'
    }
    
    query_string = urllib.parse.urlencode(params)
    request_url = f"{base_url}?{query_string}"
    
    events = []
    try:
        req = urllib.request.Request(request_url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('response', {}).get('body', {}).get('items', [])
            
            if isinstance(items, dict):
                items = items.get('item', [])
            if isinstance(items, dict):
                items = [items]
            
            for item in items:
                title = item.get('bidNtceNm', '알 수 없는 입찰공고')
                write_dt = item.get('bidWrtDt', '')
                start_str = write_dt[:8] if len(write_dt) >= 8 else now.strftime('%Y%m%d')
                formatted_start = f"{start_str[:4]}-{start_str[4:6]}-{start_str[6:]}"
                
                events.append({
                    'title': f"[조달청] {title[:20]}...",
                    'start': formatted_start,
                    'color': '#6366f1',
                    'extendedProps': {
                        'category': 'bid',
                        'categoryLabel': '실시간 사회조사 입찰',
                        'description': f"공고명: {title}\n기관: {item.get('ntceInsttNm', '조달청')}",
                        'price': '나라장터 세부조회',
                        'url': item.get('bidNtceDtlUrl', 'https://www.g2b.go.kr')
                    }
                })
        print(f"[수집 완료] 조달청 실시간 공고 {len(events)}건 수집됨.")
    except Exception as e:
        print(f"[데이터 수집 실패] 조달청 API 호출 오류: {e}")
        
    return events


def parse_existing_events(filepath):
    """기존 event_data.js 파일에서 이벤트 배열을 파싱"""
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # JS 배열 추출: const calendarEvents = [...];
        match = re.search(r'const\s+calendarEvents\s*=\s*\[', content)
        if not match:
            return []
        
        # 주석을 제거하고 JSON 파싱을 시도합니다
        # // 스타일 주석 제거
        no_comments = re.sub(r'//.*?\n', '\n', content)
        events = []
        # 개별 { ... } 블록 추출 (비보존 필드 포함)
        # 각 블록은 title, start, category 등을 필수로 가짐
        blocks = re.findall(r'\{(.*?)\}', no_comments, re.DOTALL)
        
        for block in blocks:
            # 필드 추출용 도우미 함수
            def get_field(field_name):
                # 패턴: field: 'value' 또는 field: "value"
                m = re.search(rf'{field_name}:\s*[\'"](.*?)[\'"]', block, re.DOTALL)
                return m.group(1).strip() if m else None

            title = get_field('title')
            start = get_field('start')
            if not title or not start:
                continue
            
            # 카테고리 등 확장 속성 추출
            category = get_field('category')
            categoryLabel = get_field('categoryLabel')
            description = get_field('description')
            price = get_field('price')
            url = get_field('url')
            source = get_field('source')
            
            event = {
                'title': title,
                'start': start,
                'color': get_field('color') or '#6366f1',
                'extendedProps': {
                    'category': category or 'sme',
                    'categoryLabel': categoryLabel or '기타',
                    'description': description or '',
                    'price': price or '',
                    'url': url or ''
                }
            }
            if source:
                event['extendedProps']['source'] = source
            
            # end 날짜가 있으면 추가
            end = get_field('end')
            if end:
                event['end'] = end
                
            events.append(event)
            
        print(f"[필터링] 총 {len(events)}건의 기존 이벤트 파싱 성공")
        return events
    except Exception as e:
        print(f"[경고] event_data.js 파싱 중 치명적 오류: {e}")
        return []

def merge_events(existing_events, new_events):
    """
    기존 이벤트와 새 이벤트를 병합합니다.
    - 기존 이벤트 중 'source' 속성이 있는 동적 이벤트는 제거 (최신으로 교체)
    - 정적(수동 입력) 이벤트는 그대로 유지
    """
    # 정적 이벤트 (source 속성이 없는 것) 유지
    static_events = []
    for ev in existing_events:
        props = ev.get('extendedProps', {})
        if 'source' not in props:
            static_events.append(ev)
    
    # 새 이벤트에서 중복 제거 (title + start 기준)
    seen = set()
    unique_new = []
    for ev in new_events:
        key = (ev.get('title', ''), ev.get('start', ''))
        if key not in seen:
            seen.add(key)
            unique_new.append(ev)
    
    merged = static_events + unique_new
    print(f"[병합] 정적 이벤트 {len(static_events)}건 + 동적 이벤트 {len(unique_new)}건 = 총 {len(merged)}건")
    return merged


def write_event_data_js(events, filepath):
    """이벤트 목록을 event_data.js 형태로 저장"""
    
    # 카테고리 순서에 따라 정렬
    category_order = {
        'sme': 0, 'sejong': 1, 'exhibition': 2, 'chungcheong': 3,
        'bid': 4, 'sejong_inst': 5,
    }
    
    events.sort(key=lambda x: (
        category_order.get(x.get('extendedProps', {}).get('category', ''), 99),
        x.get('start', '')
    ))
    
    lines = ['const calendarEvents = [']
    
    # 카테고리별 주석 헤더
    current_cat = None
    cat_comments = {
        'sme': "    // 1. 중소기업 지원사업 (SME Support) - Grey",
        'sejong': "    // 2. 세종시 지원사업 (Sejong City Support) - Orange",
        'exhibition': "    // 3. 박람회 및 전시회 (Exhibitions) - Dark Green",
        'chungcheong': "    // 4. 충청권 행사 (Chungcheong) - Pink",
        'bid': "    // 5. 사회조사 입찰정보 (Bidding Info) - Indigo",
        'sejong_inst': "    // 6. 세종 산하기관 입찰정보 (Sejong Institutions) - Teal",
    }
    
    for ev in events:
        cat = ev.get('extendedProps', {}).get('category', '')
        if cat != current_cat:
            if current_cat is not None:
                lines.append('')
            comment = cat_comments.get(cat)
            if comment:
                lines.append(comment)
            current_cat = cat
        
        # 이벤트 JS 객체 생성
        lines.append('    {')
        lines.append(f"        title: {json.dumps(ev['title'], ensure_ascii=False)},")
        lines.append(f"        start: {json.dumps(ev['start'], ensure_ascii=False)},")
        if 'end' in ev:
            lines.append(f"        end: {json.dumps(ev['end'], ensure_ascii=False)},")
        lines.append(f"        color: {json.dumps(ev.get('color', '#6366f1'), ensure_ascii=False)},")
        
        props = ev.get('extendedProps', {})
        lines.append('        extendedProps: {')
        lines.append(f"            category: {json.dumps(props.get('category', ''), ensure_ascii=False)},")
        lines.append(f"            categoryLabel: {json.dumps(props.get('categoryLabel', ''), ensure_ascii=False)},")
        lines.append(f"            description: {json.dumps(props.get('description', ''), ensure_ascii=False)},")
        lines.append(f"            price: {json.dumps(props.get('price', ''), ensure_ascii=False)},")
        lines.append(f"            url: {json.dumps(props.get('url', ''), ensure_ascii=False)}")
        if 'source' in props:
            # source는 마지막 줄 앞에 쉼표 추가 필요
            lines[-1] += ','
            lines.append(f"            source: {json.dumps(props['source'], ensure_ascii=False)}")
        lines.append('        }')
        lines.append('    },')
    
    lines.append('];')
    lines.append('')
    
    content = '\n'.join(lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[저장] {filepath} 업데이트 완료 ({len(events)}건)")


def main():
    print("===========================================")
    print("=== 중소기업 지원정책 캘린더 자동 업데이트 ===")
    print(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print("===========================================")
    
    env_vars = load_env()
    api_key = env_vars.get('DATA_GO_KR_API_KEY')
    
    # 1. 기존 이벤트 파싱
    existing_events = parse_existing_events(EVENT_FILE_PATH)
    print(f"[기존] event_data.js에서 {len(existing_events)}건의 이벤트 로드")
    
    # 2. 백업 생성
    if os.path.exists(EVENT_FILE_PATH):
        shutil.copy2(EVENT_FILE_PATH, BACKUP_FILE_PATH)
        print(f"[백업] {BACKUP_FILE_PATH} 생성 완료")
    
    # 3. 새 이벤트 수집
    new_events = []
    
    # 3-1. 조달청 나라장터 사회조사 입찰
    g2b_events = fetch_g2b_bidding_data(api_key)
    new_events.extend(g2b_events)
    
    # 3-2. 세종 산하기관 입찰정보 스크래핑
    if collect_all_sejong_institution_bids:
        sejong_events = collect_all_sejong_institution_bids(api_key)
        new_events.extend(sejong_events)
    else:
        print("[건너뜀] 세종 산하기관 스크래퍼를 로드할 수 없습니다.")
    
    # 4. 이벤트 병합
    if new_events:
        merged = merge_events(existing_events, new_events)
        # 5. event_data.js 업데이트
        write_event_data_js(merged, EVENT_FILE_PATH)
    else:
        print("[정보] 새로 수집된 이벤트가 없습니다. 기존 데이터를 유지합니다.")
    
    print("\n[완료] 캘린더 데이터 업데이트 프로세스 종료")


if __name__ == "__main__":
    main()
