# 🎵 Haneul CCM Portfolio

CCM 작곡가 하늘의 YouTube 채널 포트폴리오 웹사이트입니다. 이 프로젝트는 Streamlit을 사용하여 YouTube 채널의 데이터를 실시간으로 가져와 동적으로 보여주는 웹 애플리케이션입니다.

## ✨ 주요 기능

- **실시간 데이터 연동**: YouTube API를 통해 채널 정보, 동영상 목록, 통계 등을 실시간으로 가져옵니다.
- **동적 동영상 목록**: 채널에 업로드된 동영상을 일반 동영상, Shorts, 팟캐스트로 자동 분류하여 보여줍니다.
- **검색 및 정렬**: 사용자가 원하는 동영상을 쉽게 찾을 수 있도록 제목 기반 검색 및 최신순, 인기순, 제목순 정렬 기능을 제공합니다.
- **세련된 UI/UX**: 다크/라이트 모드를 지원하며, 채널의 아이덴티티를 나타내는 깔끔하고 현대적인 디자인을 적용했습니다.
- **API 키 관리**: Streamlit의 `secrets.toml`을 사용하여 API 키를 안전하게 관리합니다.
- **백업 데이터 표시**: YouTube API 호출에 실패할 경우, 로컬에 저장된 `channel_data.json` 파일을 사용하여 샘플 데이터를 표시합니다.

## 🚀 설치 및 실행

### 1. 저장소 복제
```bash
git clone https://github.com/jiwoosoft/Haneul-CCM-Portfolio.git
cd Haneul-CCM-Portfolio
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. YouTube API 키 설정
프로젝트를 실행하려면 YouTube Data API v3 사용 설정 및 API 키 발급이 필요합니다.

1.  [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트를 생성하고, **YouTube Data API v3**를 활성화합니다.
2.  **API 및 서비스 > 사용자 인증 정보**에서 API 키를 생성합니다.
3.  프로젝트 루트 디렉터리에 `.streamlit` 폴더를 생성하고, 그 안에 `secrets.toml` 파일을 만듭니다.
4.  `secrets.toml` 파일에 다음과 같이 API 키와 채널 정보를 추가합니다.

    ```toml
    # .streamlit/secrets.toml

    YOUTUBE_API_KEY = "여기에_발급받은_API_키를_입력하세요"
    CHANNEL_ID = "UCq95B9P_M-A9A5A4A-Z7A9Q"  # 예시: Haneul CCM 채널 ID
    PODCAST_PLAYLIST_ID = "PL_... " # 팟캐스트 플레이리스트 ID (선택 사항)
    ```

### 4. 웹사이트 실행
```bash
streamlit run youtube_portfolio.py
```

## 📁 파일 구조

```
Haneul-CCM-Portfolio/
├── .streamlit/
│   └── secrets.toml         # API 키 및 채널 정보 저장
├── youtube_portfolio.py     # 메인 스트림릿 웹 애플리케이션
├── data_manager.py          # (백업용) 데이터 관리 도구
├── channel_data.json        # API 실패 시 사용할 백업 데이터
├── requirements.txt         # 필요한 Python 패키지 목록
└── README.md                # 프로젝트 설명서
```

## 🎨 디자인 특징

- **그라데이션 배경**: 보라색과 파란색 그라데이션으로 음악적 분위기 연출
- **카드형 레이아웃**: 각 동영상을 카드 형태로 깔끔하게 표시
- **호버 효과**: 마우스를 올리면 카드가 살짝 위로 올라가는 애니메이션
- **반응형 디자인**: 다양한 화면 크기에 최적화
- **새로고침 버튼**: 중앙에 위치한 눈에 띄는 새로고침 버튼

## 📱 사용법

### 메인 웹사이트
1. **메인 페이지**: 채널 정보와 최근 동영상들이 표시됩니다
2. **새로고침 버튼**: 🔄 버튼을 클릭하여 데이터를 새로고침합니다
3. **사이드바**: 
   - 채널 통계 정보
   - 검색 및 필터링 옵션
   - 연락처 정보
   - 테마 설정
4. **동영상 카드**: 
   - 썸네일 이미지
   - 제목과 설명
   - 업로드 날짜, 조회수, 좋아요 수
   - YouTube 링크

### 데이터 관리 도구
1. **채널 정보 관리**: 채널명, 설명, 통계 정보 수정
2. **동영상 관리**: 새 동영상 추가, 기존 동영상 삭제
3. **통계 확인**: 총 조회수, 좋아요 수 등 통계 정보
4. **데이터 내보내기**: JSON, CSV 형식으로 데이터 백업

## 🔧 데이터 관리

### 동영상 추가 방법
1. `data_manager.py` 실행
2. "🎬 동영상 관리" 탭 선택
3. 동영상 정보 입력:
   - 제목 (필수)
   - 설명
   - 업로드 날짜/시간
   - YouTube URL (필수)
   - 재생 시간
   - 조회수, 좋아요 수
4. "➕ 동영상 추가" 버튼 클릭

### 데이터 파일 구조
```json
{
  "channel_info": {
    "title": "Haneul CCM",
    "description": "채널 설명",
    "subscriber_count": "1,234",
    "video_count": "25",
    "view_count": "45,678",
    "last_updated": "2024-01-15 10:30:00"
  },
  "videos": [
    {
      "id": "video1",
      "title": "동영상 제목",
      "description": "동영상 설명",
      "published_at": "2024-01-15T10:00:00Z",
      "thumbnail": "썸네일 URL",
      "youtube_url": "YouTube URL",
      "duration": "4:32",
      "views": "1,234",
      "likes": "89"
    }
  ]
}
```

## 🔄 새로고침 기능

- **수동 새로고침**: 🔄 버튼을 클릭하여 데이터 갱신
- **마지막 업데이트 시간**: 언제 마지막으로 업데이트되었는지 표시
- **로딩 효과**: 새로고침 중 스피너 표시
- **성공 메시지**: 새로고침 완료 시 확인 메시지

## 📊 기술 스택

- **Web Framework**: Streamlit
- **API Communication**: requests
- **Data Handling**: json, isodate
- **Styling**: HTML/CSS

## 🎵 CCM 포트폴리오 특징

이 웹사이트는 CCM(Contemporary Christian Music) 작곡가의 포트폴리오로 특별히 설계되었습니다:

- **음악적 분위기**: 그라데이션과 색상으로 음악적 분위기 연출
- **찬양 중심**: 하나님을 찬양하는 마음을 담은 디자인
- **평화로운 느낌**: 차분하고 평화로운 색상 조합
- **접근성**: 모든 연령대가 쉽게 사용할 수 있는 직관적인 인터페이스
- **정적 데이터**: 안정적이고 빠른 로딩 속도

## 🔧 커스터마이징

### 색상 변경
CSS 스타일에서 다음 색상들을 변경할 수 있습니다:
- 메인 헤더: `#1f77b4`
- 카드 그라데이션: `#667eea` → `#764ba2`
- 채널 정보 그라데이션: `#f093fb` → `#f5576c`

### 레이아웃 수정
- `st.columns()` 함수를 사용하여 레이아웃 조정
- CSS 클래스를 수정하여 스타일 변경

### 데이터 구조 변경
- `channel_data.json` 파일 구조를 수정하여 추가 필드 추가 가능
- 새로운 동영상 정보 필드 추가 가능

## 📞 연락처

- **이메일**: webmaster@jiwoosoft.com
- **홈페이지**: [www.Jiwoosoft.com](http://www.jiwoosoft.com)
- **YouTube**: [@HaneulCCM](https://www.youtube.com/@HaneulCCM)

## 📄 라이선스

© 2025 HaneulCCM. 모든 권리 보유. Powered by Jiwoosoft.

---

*CCM 은혜의 찬양으로 하나님을 찬양합니다.* 🎵🙏

## 🚀 빠른 시작

1. **패키지 설치**: `pip install -r requirements.txt`
2. **웹사이트 실행**: `streamlit run youtube_portfolio.py`
3. **데이터 관리**: `streamlit run data_manager.py`
4. **브라우저에서 확인**: `http://localhost:8501`

새 동영상이 업로드되면 데이터 관리 도구에서 쉽게 추가하고, 메인 웹사이트에서 새로고침 버튼을 눌러 최신 정보를 확인하세요! 🔄 
