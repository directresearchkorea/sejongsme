
import re

content = """const calendarEvents = [
    {
        title: '2026년 백년소상공인 신규지정 모집 마감',
        start: '2026-03-27',
        color: '#71717a',
        extendedProps: {
            category: 'sme',
            categoryLabel: '중소기업 지원사업',
            description: '2026년 백년소상공인 신규 지정 모집 공고 (연장). 소상공인시장진흥공단에서 주관하는 사업으로 신규 지정 마감일입니다.',
            price: '무료 (지원정책)',
            url: 'https://www.mss.go.kr'
        }
    }
];
"""

# Test regex 1 (line 121)
match1 = re.search(r'const\s+calendarEvents\s*=\s*\[', content)
print(f"Match 1: {bool(match1)}")

# Test regex 2 (line 129)
no_comments = content # simplified
match2 = re.search(r'const\s+calendarEvents\s*=\s*(\[.*\])\s*;?\s*$', no_comments, re.DOTALL | re.MULTILINE)
print(f"Match 2: {bool(match2)}")
if match2:
    print(f"Group 1 length: {len(match2.group(1))}")
