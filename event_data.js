const calendarEvents = [
    // 1. 중소기업 지원사업 (SME Support) - Grey
    {
        title: "소상공인 정책자금 구조개편 아이디어 공모전 마감",
        start: "2026-03-20",
        color: "#71717a",
        extendedProps: {
            category: "sme",
            categoryLabel: "중소기업 지원사업",
            description: "소상공인 정책자금의 효율적 운용을 위한 국민/기업 대상 아이디어 공모전 접수 마감.",
            price: "무료 (공모전)",
            url: ""
        }
    },
    {
        title: "부산광역시 중소기업 디자인개발 지원과제 모집 마감",
        start: "2026-03-26",
        color: "#71717a",
        extendedProps: {
            category: "sme",
            categoryLabel: "중소기업 지원사업 (지역별)",
            description: "부산광역시 중소기업 디자인개발 지원사업 지원과제 이메일 접수 마감.",
            price: "무료 (지원정책)",
            url: ""
        }
    },
    {
        title: "2026년 백년소상공인 신규지정 모집 마감",
        start: "2026-03-27",
        color: "#71717a",
        extendedProps: {
            category: "sme",
            categoryLabel: "중소기업 지원사업",
            description: "2026년 백년소상공인 신규 지정 모집 공고 (연장). 소상공인시장진흥공단에서 주관하는 사업으로 신규 지정 마감일입니다.",
            price: "무료 (지원정책)",
            url: ""
        }
    },
    {
        title: "2026년 예비창업패키지 사내벤처팀 모집 마감",
        start: "2026-03-30",
        color: "#71717a",
        extendedProps: {
            category: "sme",
            categoryLabel: "중소기업 지원사업",
            description: "2026년 예비창업패키지 특화분야 사내벤처팀 모집 공고 마감. 예비창업자 및 기업의 적극적인 참여가 요구됩니다.",
            price: "무료 (지원정책)",
            url: ""
        }
    },
    {
        title: "2026년 기술보호 바우처 지원사업 모집 마감",
        start: "2026-03-30",
        color: "#71717a",
        extendedProps: {
            category: "sme",
            categoryLabel: "중소기업 지원사업",
            description: "중소기업의 핵심 기술 보호를 위한 바우처 지원사업 참여기업 모집 종료.",
            price: "무료 (지원정책)",
            url: ""
        }
    },
    {
        title: "2026년 AI 통합 바우처 지원사업 수정공고 마감",
        start: "2026-03-30T15:00:00",
        color: "#71717a",
        extendedProps: {
            category: "sme",
            categoryLabel: "중소기업 지원사업",
            description: "AI 통합 바우처 지원사업의 전산 접수 마감일 (15시). 디지털 전환을 모색하는 중소기업 타겟.",
            price: "무료 (바우처/지원)",
            url: ""
        }
    },
    {
        title: "2026년 소상공인 협업활성화 공동사업 모집 마감",
        start: "2026-04-03",
        color: "#71717a",
        extendedProps: {
            category: "sme",
            categoryLabel: "중소기업 지원사업",
            description: "소상공인 협동조합의 공동사업 촉진을 위한 지원 마감일. (신청은 3월 11일부터 시작)",
            price: "무료 지원",
            url: ""
        }
    },

    // 2. 세종시 지원사업 (Sejong City Support) - Orange
    {
        title: "세종형 통합돌봄 서비스 본격 시행",
        start: "2026-03-01",
        color: "#ea580c",
        extendedProps: {
            category: "sejong",
            categoryLabel: "세종시 지원사업",
            description: "일상생활이 어려운 어르신과 중증 장애인을 대상으로 맞춤형 방문 의료, 요양, 주거 수리 등을 제공하는 세종형 통합돌봄 서비스 전면 시행.",
            price: "사업비 지원 (조건 충족시 무료)",
            url: ""
        }
    },
    {
        title: "세종시 소상공인 지원 신청 마감",
        start: "2026-03-15",
        color: "#ea580c",
        extendedProps: {
            category: "sejong",
            categoryLabel: "세종시 지원사업",
            description: "세종 관내 중소기업 및 소상공인을 대상으로 하는 2026년 1분기 정책지원 접수 마감일.",
            price: "무료 지원",
            url: ""
        }
    },
    {
        title: "세종문화회관 서울시예술단 직책단원 채용 마감",
        start: "2026-03-25",
        color: "#ea580c",
        extendedProps: {
            category: "sejong",
            categoryLabel: "세종시 지원사업",
            description: "(재)세종문화회관의 서울시예술단 직책단원(극단, 소년소녀합창단) 공개채용 공고 마감일.",
            price: "무료 (채용)",
            url: ""
        }
    },
    {
        title: "제12회 대한민국 SW융합 해커톤 대회 세종지역 참가팀 모집 공고",
        start: "2026-07-22",
        color: "#ea580c",
        extendedProps: {
            category: "sejong",
            categoryLabel: "세종시 지원사업",
            description: "기관: 세종테크노파크\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n제12회 대한민국 SW융합 해커톤 대회 세종지역 참가팀 모집 공고 안내.",
            price: "세종테크노파크 공고",
            url: ""
        }
    },
    {
        title: "2026년 지역특화콘텐츠개발지원사업 역량강화 교육 수강생 모집",
        start: "2026-08-29",
        color: "#ea580c",
        extendedProps: {
            category: "sejong",
            categoryLabel: "세종시 지원사업",
            description: "기관: 세종테크노파크\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n2026년 지역특화콘텐츠개발지원사업 역량강화 교육 수강생 모집 안내.",
            price: "세종테크노파크 공고",
            url: ""
        }
    },

    // 3. 박람회 및 전시회 (Exhibitions) - Dark Green
    {
        title: "2026 대구국제섬유박람회 (EXCO)",
        start: "2026-03-04",
        end: "2026-03-07",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "리부트(RE:BOOT) 슬로건으로 열리는 프리뷰 인 대구 (PID) 국제섬유박람회.",
            price: "사전등록 무료 / 현장등록 유료",
            url: ""
        }
    },
    {
        title: "AW2026 (스마트공장·자동화산업전) (COEX)",
        start: "2026-03-04",
        end: "2026-03-07",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "2026 스마트공장·자동화산업전 전시가 코엑스에서 개최됩니다. 산업동향 파악 목적 필수 참석 추천.",
            price: "사전예약 무료 / 현장예매 10,000원",
            url: ""
        }
    },
    {
        title: "KIBS 2026 (국제보트쇼) & KOFISH (KINTEX)",
        start: "2026-03-06",
        end: "2026-03-09",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "Korea International Boat Show 및 낚시 박람회 병행 개최. 장소: 킨텍스.",
            price: "일반 7,000원 / 초중고 학생/사전등록자 무료",
            url: ""
        }
    },
    {
        title: "InterBattery 2026 (COEX)",
        start: "2026-03-11",
        end: "2026-03-14",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "국내 최대 배터리 산업 전문 전시회 인터배터리가 코엑스에서 개최됩니다.",
            price: "해외바이어/사전등록 무료 / 일반 20,000원",
            url: ""
        }
    },
    {
        title: "고양 가구엑스포 (KINTEX)",
        start: "2026-03-12",
        end: "2026-03-16",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "킨텍스에서 열리는 프리미엄 가구 엑스포.",
            price: "무료 관람",
            url: ""
        }
    },
    {
        title: "세계유학 및 웨딩박람회 주간 (COEX)",
        start: "2026-03-14",
        end: "2026-03-16",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "세계유학/영국유학박람회 및 제411회 웨덱스 웨딩박람회가 동시에 코엑스에서 진행됩니다.",
            price: "무료 입장",
            url: ""
        }
    },
    {
        title: "SECON 2026 (세계 보안 엑스포) (KINTEX)",
        start: "2026-03-18",
        end: "2026-03-21",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "사이버 에셋 및 물리 보안 총괄 아시아 최대 통합보안 전시회. B2B 리서치 필수 타겟.",
            price: "무료 (사전등록/초청장 소지자 필수 참관)",
            url: ""
        }
    },
    {
        title: "제26회 대구건축박람회 (EXCO)",
        start: "2026-03-19",
        end: "2026-03-23",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "엑스코 동관에서 개최되는 지역 대표 건축 비즈니스 전시회.",
            price: "사전등록 접수시 무료 / 현장 5,000원",
            url: ""
        }
    },
    {
        title: "제41회 KIMES (국제의료기기설비) (COEX)",
        start: "2026-03-19",
        end: "2026-03-23",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "의료기기, 병원설비 등을 전시하는 KIMES 박람회. 헬스케어 관련 리서치 시 참고 요망.",
            price: "초청장 소지자/사전등록 무료 / 일반 10,000원",
            url: ""
        }
    },
    {
        title: "BDEX 2026 부산 치의학 전시회 (BEXCO)",
        start: "2026-03-21",
        end: "2026-03-23",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "벡스코 제2전시장에서 열리는 부산 치의학 학술대회 및 전시회.",
            price: "유료 (학술대회 등록비 별도)",
            url: ""
        }
    },
    {
        title: "SPOEX (서울 국제스포츠레저산업전) (COEX)",
        start: "2026-03-26",
        end: "2026-03-30",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "국내 최대 스포츠 및 레저 산업 전시회 SPOEX 진행.",
            price: "사전등록 무료 / 현장예매 10,000원",
            url: ""
        }
    },
    {
        title: "KOREA PACK & KOREA CHEM 2026 (KINTEX)",
        start: "2026-03-31",
        end: "2026-04-04",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "국제 화학장치산업전(CHEM), 포장기자재전(PACK) 등 B2B 종합 박람회. 킨텍스 개최.",
            price: "사전등록시 무료 / 일반 10,000원",
            url: ""
        }
    },
    {
        title: "ESG-ECO EXPO KOREA 2026 (COEX)",
        start: "2026-10-21",
        end: "2026-10-24",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "국내 최대 규모의 ESG 및 친환경 혁신 전문 전시회. 코엑스 개최.",
            price: "사전등록 무료",
            url: ""
        }
    },
    {
        title: "BIOPLUS - INTERPHEX KOREA (COEX)",
        start: "2026-10-28",
        end: "2026-10-31",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "바이오 제약 가치 사슬을 포괄하는 바이오 제약 전시회.",
            price: "사전등록 무료",
            url: ""
        }
    },
    {
        title: "COEX Food Week 2026",
        start: "2026-11-04",
        end: "2026-11-08",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "아시아를 대표하는 식품 전문 전시회 코엑스 푸드 위크.",
            price: "일반 10,000원",
            url: ""
        }
    },
    {
        title: "서울국제카페쇼 2026 (COEX)",
        start: "2026-11-11",
        end: "2026-11-15",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "세계 최대 규모 커피 전문 전시회.",
            price: "사전등록 무료",
            url: ""
        }
    },
    {
        title: "SOFTWAVE 2026 (COEX)",
        start: "2026-12-02",
        end: "2026-12-05",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "소프트웨어 전문 박람회. SW기술 트렌드 등.",
            price: "무료 (초청장/사전등록)",
            url: ""
        }
    },
    {
        title: "2026 SEOUL ART SHOW & 일러스트레이션 페어 (COEX)",
        start: "2026-12-23",
        end: "2026-12-28",
        color: "#065f46",
        extendedProps: {
            category: "exhibition",
            categoryLabel: "박람회 및 전시회",
            description: "국내 최대 미술시장 서울아트쇼 및 서울일러스트레이션페어 동시 개최.",
            price: "일반 15,000원",
            url: ""
        }
    },

    // 4. 충청권 행사 (Chungcheong) - Pink
    {
        title: "충청·청주가구박람회 (OSCO)",
        start: "2026-02-28",
        end: "2026-03-03",
        color: "#db2777",
        extendedProps: {
            category: "chungcheong",
            categoryLabel: "충청권 행사 및 박람회",
            description: "청주 OSCO(오스코)에서 진행되는 충청/청주 가구 박람회.",
            price: "무료 입장",
            url: ""
        }
    },
    {
        title: "하우투웨딩박람회 (OSCO)",
        start: "2026-03-07",
        end: "2026-03-09",
        color: "#db2777",
        extendedProps: {
            category: "chungcheong",
            categoryLabel: "충청권 행사 및 박람회",
            description: "청주 OSCO에서 진행되는 프리미엄 웨딩 박람회.",
            price: "사전 참가신청시 무료",
            url: ""
        }
    },
    {
        title: "렙타일페어 (OSCO)",
        start: "2026-03-07",
        end: "2026-03-09",
        color: "#db2777",
        extendedProps: {
            category: "chungcheong",
            categoryLabel: "충청권 행사 및 박람회",
            description: "희귀 반려동물 및 이색애완동물 박람회 렙타일페어. 청주 OSCO 개최.",
            price: "사전예매 할인(유료) / 현장구매 가능",
            url: ""
        }
    },
    {
        title: "청주월명공원 에피트 입주박람회 (OSCO)",
        start: "2026-03-13",
        end: "2026-03-16",
        color: "#db2777",
        extendedProps: {
            category: "chungcheong",
            categoryLabel: "충청권 행사 및 박람회",
            description: "청주월명공원 에피트 온더파크 입주 박람회. 청주 OSCO.",
            price: "무료 (입주예정자 한정)",
            url: ""
        }
    },
    {
        title: "유사나킥오프셀레브레이션 (OSCO)",
        start: "2026-03-21",
        color: "#db2777",
        extendedProps: {
            category: "chungcheong",
            categoryLabel: "충청권 행사 및 박람회",
            description: "2026 유사나킥오프셀레브레이션 기업 행사. 청주 OSCO 개최.",
            price: "유료/초청자 한정",
            url: ""
        }
    },
    {
        title: "충청 코베 베이비페어&유아교육전 (OSCO)",
        start: "2026-03-26",
        end: "2026-03-30",
        color: "#db2777",
        extendedProps: {
            category: "chungcheong",
            categoryLabel: "충청권 행사 및 박람회",
            description: "임신, 출산, 육아 및 유아교육 관련 종합 박람회. 청주 OSCO.",
            price: "어플/사전등록시 무료 / 현장 5,000원",
            url: ""
        }
    },
    {
        title: "대전가구박람회 (DCC)",
        start: "2026-03-26",
        end: "2026-03-30",
        color: "#db2777",
        extendedProps: {
            category: "chungcheong",
            categoryLabel: "충청권 행사 및 박람회",
            description: "대전컨벤션센터(DCC) 제2전시장에서 개최되는 대전가구박람회.",
            price: "무료 입장",
            url: ""
        }
    },

    // 5. 사회조사 입찰정보 (Bidding Info) - Indigo
    {
        title: "[조달청] 2026년 전국 사회안전망 실태조사 위탁",
        start: "2026-03-12",
        color: "#6366f1",
        extendedProps: {
            category: "bid",
            categoryLabel: "사회조사 입찰정보",
            description: "조달청 나라장터 발주. 전국 단위 사회안전망 구축을 위한 통계 조사 수행 업체 선정 (추정가격 5억 이상).",
            price: "나라장터 입찰",
            url: ""
        }
    },
    {
        title: "[세종시] 2026년 세종특별자치시 사회조사 수행",
        start: "2026-03-18",
        color: "#6366f1",
        extendedProps: {
            category: "bid",
            categoryLabel: "사회조사 입찰정보",
            description: "세종시 지역민의 주거, 교통, 환경 만족도 조사를 위한 2026년도 정기 사회조사 용역.",
            price: "기관 공고 참고",
            url: ""
        }
    },
    {
        title: "[국책연구원] 저출산 대응 정책 효과성 분석 조사",
        start: "2026-03-24",
        color: "#6366f1",
        extendedProps: {
            category: "bid",
            categoryLabel: "사회조사 입찰정보",
            description: "대한민국 국책연구기관 발주. 저출산 극복을 위한 국민 인식 및 정책 체감도 정밀 실태조사 용역 선정.",
            price: "입찰 공고",
            url: ""
        }
    },
    {
        title: "[세종테크노파크] 세종 관내 기업 정주여건 조사",
        start: "2026-03-31",
        color: "#6366f1",
        extendedProps: {
            category: "bid",
            categoryLabel: "사회조사 입찰정보",
            description: "세종시 산하 세종테크노파크 발주. 지역 전략 산업 기업 종사자들의 정주 여건 및 만족도 분석 조사.",
            price: "자체 입찰",
            url: ""
        }
    },
    {
        title: "[KDI] 미래세대 경제관념 및 소비행태 심층조사",
        start: "2026-04-05",
        color: "#6366f1",
        extendedProps: {
            category: "bid",
            categoryLabel: "사회조사 입찰정보",
            description: "KDI(한국개발연구원) 주관. MZ세대 및 알파세대의 경제 관념 변화 추이 분석을 위한 설문조사 입찰.",
            price: "KDI 홈페이지 공고",
            url: ""
        }
    },

    // 6. 세종 산하기관 입찰정보 (Sejong Institutions) - Teal
    {
        title: "[교통] 세종도시교통공사 임직원 사칭주의",
        start: "2026-02-27",
        color: "#0d9488",
        extendedProps: {
            category: "sejong_inst",
            categoryLabel: "세종 산하기관 입찰",
            description: "공고명: 세종도시교통공사 임직원 사칭주의\n(도시철도, BRT 운영 및 교통 관련 사업)\n\n기관: 교통공사 홈페이지",
            price: " 참조",
            url: "https://www.sctc.kr/bbs/view/BBSS1612021757537630/BBSW2602271645026417/?",
            source: "web_sctc"
        }
    },
];
