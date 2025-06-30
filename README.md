# ⚔️ LAST WAR:SURVIVAL PZTK #777 연맹 대시보드

라스트워: 서바이벌 게임의 PZTK #777 연맹을 위한 종합 정보 대시보드입니다.

## 🎮 프로젝트 소개

이 프로젝트는 라스트워: 서바이벌 게임 플레이어들이 연맹 활동을 효율적으로 관리할 수 있도록 도와주는 웹 대시보드입니다.

### 주요 기능
- 📅 **일일 일정 관리**: 게임 내 이벤트와 활동 일정 확인
- 📊 **연맹 대결 정보**: 연맹전 일정과 전략 정보
- 🎯 **이벤트 추적**: 진행 중인 이벤트와 보상 정보
- 🖩 **게임 계산기**: 영웅 레벨업, 장비 강화 등 계산 도구
- ⚙️ **관리자 도구**: 데이터 관리 및 수정 기능

## 🚀 빠른 시작

### 필요 조건
- Python 3.11+
- Google Sheets API 접근 권한
- Streamlit Cloud 계정 (배포용)

### 로컬 실행
```bash
# 저장소 클론
git clone https://github.com/KimGB777/PZTK777.git
cd PZTK777

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
mkdir -p .streamlit
cp .streamlit/config.toml.example .streamlit/config.toml
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Google Sheets 연결 설정
# secrets.toml 파일에서 YOUR_GOOGLE_SHEETS_URL을 실제 URL로 변경

# 앱 실행
streamlit run app.py
```

## 📁 프로젝트 구조

```
PZTK777/
├── app.py                 # 메인 애플리케이션
├── requirements.txt       # 의존성 목록
├── README.md             # 프로젝트 문서
├── .streamlit/
│   ├── config.toml       # Streamlit 설정
│   └── secrets.toml      # 비밀 설정 (Git 제외)
├── pages/                # 페이지 모듈
│   ├── Dashboard.py      # 대시보드 페이지
│   ├── Calculator.py     # 계산기 페이지
│   └── R4.py            # 관리자 페이지
├── components/           # UI 컴포넌트
│   └── copy_button.py    # 복사 버튼 컴포넌트
├── utils/               # 유틸리티 함수
│   ├── gsheet_loader.py  # Google Sheets 데이터 로더
│   ├── data_extract.py   # 데이터 추출 함수
│   └── logger.py         # 로깅 유틸리티
├── tests/               # 테스트 파일
└── .github/
    └── workflows/        # GitHub Actions 워크플로우
```

## 🔧 일정 수정 방법
### R4 메뉴에서 수정하기
1. Google Sheets에서 데이터베이스 스프레드시트 생성
2. 필요에 따라 각 시트로 이동"
   - `daily`: 날짜별 이벤트(열차, 좀공, 군사훈련, 시즌 관련 일정 등)
   - `weekly`: 주간 반복 이벤트(연맹대결 등)
   - `monthly`: 4주 주기 반복 이벤트(간격 이벤트: 장군의 시련, 등)
   - `note`: 항상 노출되는 이벤트 (고정 공지 등)
3. 시트 내 변수명

### 📊  데이터베이스 구조 (daily 시트 예시)
| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| Date | Date | 날짜 |
| schedule_daily | Text | 일일 일정 |
| duel_daily | Text | 연맹대결 일정 |
| event_daily | Text | 일일 이벤트 |
| train_daily | Text | 훈련 일정 |
| zombie_daily | Text | 좀비 이벤트 |

---

⚔️ **LAST WAR:SURVIVAL PZTK #777 연맹과 함께 생존하세요!** ⚔️