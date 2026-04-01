"""
주간 요약 이메일 발송 스크립트
매주 금요일 오전 9시에 실행되어, 한 주간의 캘린더 업데이트 내역을 요약 이메일로 전송합니다.
"""
import os
import sys
import re
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from collections import Counter

# 프로젝트 경로
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_FILE_PATH = os.path.join(PROJECT_DIR, 'event_data.js')

# .env 파일에서 환경변수 로드
env_path = os.path.join(PROJECT_DIR, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip()

GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')


def send_email(subject, body, to_email):
    """Gmail SMTP로 이메일 전송"""
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()
        print("[이메일] 주간 요약 이메일 전송 성공!")
    except Exception as e:
        print(f"[이메일 오류] 전송 실패: {e}")


def get_git_log_summary():
    """이번 주 Git 커밋 내역 요약"""
    try:
        # PATH에 git 포함
        env = os.environ.copy()
        git_path = r"C:\Program Files\Git\cmd"
        if git_path not in env.get('PATH', ''):
            env['PATH'] = git_path + ";" + env.get('PATH', '')

        # 지난 7일간의 커밋 로그
        result = subprocess.run(
            ['git', 'log', '--oneline', '--since=7.days.ago', '--no-merges'],
            cwd=PROJECT_DIR,
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            env=env
        )
        commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return commits
    except Exception as e:
        return [f"(Git 로그 조회 실패: {e})"]


def analyze_event_data():
    """현재 event_data.js의 이벤트 분석"""
    if not os.path.exists(EVENT_FILE_PATH):
        return {}, 0

    with open(EVENT_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 카테고리별 이벤트 수 집계
    categories = re.findall(r"category:\s*['\"](\w+)['\"]", content)
    cat_counts = Counter(categories)

    # 총 이벤트 수
    total = len(re.findall(r"title:\s*['\"]", content))

    # 이번달(현재)과 다음달 이벤트 수
    now = datetime.now()
    this_month = now.strftime('%Y-%m')
    next_month = (now.replace(day=1) + timedelta(days=32)).strftime('%Y-%m')

    this_month_count = len(re.findall(rf'start:\s*["\']({re.escape(this_month)})', content))
    next_month_count = len(re.findall(rf'start:\s*["\']({re.escape(next_month)})', content))

    # source별 집계 (동적 vs 정적)
    sources = re.findall(r"source:\s*['\"](\w+)['\"]", content)
    dynamic_count = len(sources)
    static_count = total - dynamic_count

    return {
        'total': total,
        'categories': dict(cat_counts),
        'this_month': this_month,
        'this_month_count': this_month_count,
        'next_month': next_month,
        'next_month_count': next_month_count,
        'dynamic_count': dynamic_count,
        'static_count': static_count,
    }


def get_upcoming_events(days=14):
    """앞으로 2주간의 주요 이벤트 목록"""
    if not os.path.exists(EVENT_FILE_PATH):
        return []

    with open(EVENT_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    now = datetime.now()
    end_date = now + timedelta(days=days)

    # 간단한 title + start 추출
    events = []
    blocks = re.findall(r'\{(.*?)\}', content, re.DOTALL)
    for block in blocks:
        title_m = re.search(r'title:\s*["\'](.+?)["\']', block)
        start_m = re.search(r'start:\s*["\']([\d-]+)', block)
        if title_m and start_m:
            try:
                start_dt = datetime.strptime(start_m.group(1), '%Y-%m-%d')
                if now <= start_dt <= end_date:
                    events.append((start_m.group(1), title_m.group(1)))
            except ValueError:
                continue

    events.sort(key=lambda x: x[0])
    return events


def build_weekly_summary():
    """주간 요약 보고서 생성"""
    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')  # 월요일
    week_end = now.strftime('%Y-%m-%d')

    # 카테고리 한글 매핑
    cat_labels = {
        'sme': '중소기업 지원사업',
        'sejong': '세종시 지원사업',
        'exhibition': '박람회 및 전시회',
        'chungcheong': '충청권 행사',
        'bid': '사회조사 입찰정보',
        'sejong_inst': '세종 산하기관 입찰',
    }

    # 데이터 수집
    commits = get_git_log_summary()
    stats = analyze_event_data()
    upcoming = get_upcoming_events(14)

    # 보고서 작성
    lines = []
    lines.append("=" * 60)
    lines.append("  세종시 중소기업 지원정책 캘린더 - 주간 요약 보고서")
    lines.append("=" * 60)
    lines.append(f"\n보고 기간: {week_start} ~ {week_end} (금요일 발송)")
    lines.append(f"발송 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"대시보드: https://directresearchkorea.github.io/sejongsme/")

    # 1. 캘린더 현황
    lines.append(f"\n{'─' * 50}")
    lines.append("[현황] 캘린더 현황")
    lines.append(f"{'─' * 50}")
    lines.append(f"  전체 이벤트: {stats.get('total', 0)}건")
    lines.append(f"  - 정적(수동 입력): {stats.get('static_count', 0)}건")
    lines.append(f"  - 동적(자동 수집): {stats.get('dynamic_count', 0)}건")
    lines.append(f"\n  {stats.get('this_month', '?')}월 이벤트: {stats.get('this_month_count', 0)}건")
    lines.append(f"  {stats.get('next_month', '?')}월 이벤트: {stats.get('next_month_count', 0)}건")

    # 카테고리별
    lines.append(f"\n  [카테고리별 분포]")
    for cat_key, count in sorted(stats.get('categories', {}).items(), key=lambda x: -x[1]):
        label = cat_labels.get(cat_key, cat_key)
        lines.append(f"    • {label}: {count}건")

    # 2. 이번 주 업데이트 내역
    lines.append(f"\n{'─' * 50}")
    lines.append("[업데이트] 이번 주 업데이트 내역 (Git 커밋)")
    lines.append(f"{'─' * 50}")
    if commits and commits[0]:
        for commit in commits[:10]:
            lines.append(f"  • {commit}")
        if len(commits) > 10:
            lines.append(f"  ... 외 {len(commits) - 10}건")
    else:
        lines.append("  이번 주 업데이트 없음")

    # 3. 향후 2주 주요 일정
    lines.append(f"\n{'─' * 50}")
    lines.append("[일정] 향후 2주간 주요 일정")
    lines.append(f"{'─' * 50}")
    if upcoming:
        for date, title in upcoming[:15]:
            lines.append(f"  [{date}] {title}")
        if len(upcoming) > 15:
            lines.append(f"  ... 외 {len(upcoming) - 15}건")
    else:
        lines.append("  향후 2주간 등록된 일정 없음")

    # 4. 시스템 상태
    lines.append(f"\n{'─' * 50}")
    lines.append("[시스템] 시스템 상태")
    lines.append(f"{'─' * 50}")

    api_key = os.environ.get('DATA_GO_KR_API_KEY', 'YOUR_API_KEY_HERE')
    if api_key == 'YOUR_API_KEY_HERE':
        lines.append("  ⚠️ 조달청 API 키 미설정 (data.go.kr 발급 필요)")
    else:
        lines.append("  ✅ 조달청 API 키 설정됨")

    lines.append(f"  ✅ 자동 업데이트 스케줄: 매주 월/수/금 20:00")
    lines.append(f"  ✅ 주간 보고 스케줄: 매주 금요일 09:00")

    lines.append(f"\n{'=' * 60}")
    lines.append("이 메일은 자동으로 발송되었습니다.")
    lines.append("=" * 60)

    return '\n'.join(lines)


def main():
    now = datetime.now()
    subject = f"[주간보고] 세종시 캘린더 대시보드 주간 요약 ({now.strftime('%Y-%m-%d')})"
    body = build_weekly_summary()

    # 콘솔 출력 (Windows cp949 인코딩 문제 방지)
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    print(body)
    print()

    # 이메일 발송
    if GMAIL_USER and GMAIL_APP_PASSWORD:
        send_email(subject, body, GMAIL_USER)
    else:
        print("[경고] Gmail 크리덴셜이 설정되지 않아 이메일을 발송할 수 없습니다.")
        print("       .env 파일의 GMAIL_USER, GMAIL_APP_PASSWORD를 확인하세요.")


if __name__ == "__main__":
    main()
