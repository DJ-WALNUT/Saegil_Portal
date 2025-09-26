# 새길 포털 - 공과대학 물품 대여 시스템 📖

**새길 포털**은 대학교 공과대학 학생회를 위한 간단한 물품 대여 웹 서비스입니다. 기존의 수기 장부 방식을 대체하여 재고 관리의 효율성을 높이고, 학생들의 대여 과정을 간소화하기 위해 개발되었습니다.

<br>

## ✨ 주요 기능

### 👤 사용자 기능

  - **메인 페이지**: 학생회 활동 사진이 자동으로 스크롤되는 동적인 메인 화면
  - **물품 대여 신청**: 사용자가 원하는 물품을 선택하고 간편하게 대여를 신청
  - **신청/대여 현황 확인**: 이름과 학번으로 자신의 대여 기록 및 현재 상태(신청, 미반납, 반납)를 조회

### ⚙️ 관리자 기능

  - **관리자 로그인**: 별도의 비밀번호로 관리자 페이지에 접근
  - **대시보드**: 금일 대여 건수 등 주요 현황 요약
  - **대여 수락 관리**: 사용자의 대여 신청 목록을 확인하고, 담당자 이름을 기입하여 대여 수락 (수락 시 재고 차감)
  - **반납 처리 관리**: 미반납 목록을 확인하고, 담당자 이름을 기입하여 반납 처리 (처리 시 재고 증가)
  - **재고 현황 관리**: 전체 물품의 재고를 실시간으로 확인하고 수량 수정 및 신규 물품 추가
  - **검색 기능**: 대여 수락 및 반납 처리 페이지에서 이름으로 특정 학생을 검색
  - **로그 다운로드**: 전체 대여 기록을 Excel 파일로 다운로드

<br>

## 🛠️ 기술 스택

  - **Backend**: `Python`, `Flask`
  - **Database**: `Excel` (데이터 관리를 위해 `Pandas` 라이브러리 사용)
  - **Frontend**: `HTML`, `CSS`, `JavaScript`

<br>

## 📂 프로젝트 구조

```
saegil_portal/
├── app.py              # Flask 메인 애플리케이션
├── data/
│   ├── borrow_log.xlsx   # 전체 대여 기록
│   ├── stuff_ongoing.xlsx # 현재 재고 현황
│   └── major.xlsx        # 학과 목록
├── static/
│   ├── css/              # CSS 파일
│   ├── js/               # JavaScript 파일
│   └── files/            # 이미지, 폰트 등 정적 파일
└── templates/
    ├── components/       # 헤더, 푸터 등 공통 컴포넌트
    └── *.html            # 각 페이지 HTML 템플릿
```

<br>

## 🚀 시작하기

### 1\. 프로젝트 복제

```bash
git clone https://github.com/your-username/saegil-portal.git
cd saegil-portal
```

### 2\. 가상 환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3\. 필요 라이브러리 설치

프로젝트 실행에 필요한 라이브러리들을 설치합니다.

```bash
pip install Flask pandas openpyxl
```

### 4\. 데이터 파일 준비

`data/` 폴더 안에 아래 형식에 맞는 Excel 파일 3개를 준비해야 합니다.

  - `borrow_log.xlsx`: `이름 | 전화번호 | 학번 | 학과 | 대여물품 | 대여담당자 | 대여시각 | 대여현황 | 반납담당자 | 반납시각`
  - `stuff_ongoing.xlsx`: `물품 | 재고현황`
  - `major.xlsx`: `학과명`

### 5\. 서버 실행

```bash
flask run
```

또는

```bash
python app.py
```

서버 실행 후, 웹 브라우저에서 `http://127.0.0.1:5000` 주소로 접속하세요.

<br>

## 🔧 설정

  - **관리자 비밀번호**: `app.py` 파일 상단의 `ADMIN_PASSWORD` 변수 값을 수정하여 변경할 수 있습니다.

<br>

## 📄 라이선스

&copy; 2025 Catholic University of Korea, CUK Engineering Student Council. All Rights Reserved.
[새길] 홈페이지 제작 TF팀
  - 최원서
  - 엄예빈
  - 이준용
  - 김세호