import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import os
from PIL import Image
import io
import base64
import isodate

# CSS 테마 함수 정의
def get_css_theme():
    """현재 테마(다크/라이트)에 맞는 CSS를 반환합니다."""
    dark_mode = st.session_state.get('dark_mode', True)
    
    # 공통 스타일
    base_css = """
        [data-testid="stHorizontalBlock"] {
            overflow: visible !important;
        }
        [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] {
            position: -webkit-sticky;
            position: sticky;
            top: 2rem;
            z-index: 100;
            padding: 1.5rem;
            border-radius: 15px;
        }
        .block-container { max-width: 1024px !important; padding: 2rem 1rem 10rem 1rem !important; }
        .main-header { font-size: 3rem; font-weight: bold; text-align: center; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        .sub-header { font-size: 1.3rem; text-align: center; margin-bottom: 2.5rem; font-style: italic; }
        .stats-container { display: flex; justify-content: center; gap: 3.5rem; margin: 1.5rem 0; padding: 1.2rem; border-radius: 10px; }
        .stat-item { text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .video-card { border-radius: 15px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.15); transition: all 0.3s ease; }
        .video-card:hover { transform: translateY(-5px); box-shadow: 0 12px 40px rgba(0,0,0,0.2); }
        .video-card-content { display: flex; align-items: flex-start; gap: 1rem; }
        .video-thumbnail { width: 180px; border-radius: 8px; }
        .video-info h3 { margin: 0 0 0.5rem 0; font-size: 1.3rem; font-weight: bold; }
        .video-info p { margin: 0.5rem 0; font-size: 0.9rem; }
        .video-info .video-meta { font-size: 0.8rem; margin-top: 0.5rem; }
        .shortcut-buttons { text-align: right; }
        .shortcut-button { display: inline-block; padding: 0.4rem 1rem; border-radius: 8px; text-decoration: none !important; font-weight: bold; margin-left: 0.5rem; transition: all 0.3s ease; }
    """

    # 라이트 모드 스타일
    light_theme = f"""
        <style>
            .stApp {{ background: #f0f2f6; color: #333; }}
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] {{
                background-color: #ffffff;
            }}
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] h1, 
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] h2, 
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] h3, 
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] strong,
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] div,
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] li {{ color: #333 !important; }}
            .video-card {{ background: #ffffff; }}
            .video-info h3 a {{ color: #1f77b4 !important; }}
            .video-info p, .video-info .video-meta {{ color: #444 !important; }}
            .shortcut-button {{ background: #e2e8f0; color: #1e293b !important; }}
            .shortcut-button:hover {{ background: #cbd5e1; }}
            {base_css}
        </style>
    """

    # 다크 모드 스타일
    dark_theme = f"""
        <style>
            .stApp {{ background: #0f172a; color: #e2e8f0; }}
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] {{
                background-color: #1e293b;
            }}
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] h1, 
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] h2, 
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] h3, 
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] strong,
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] div,
            [data-testid="stHorizontalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] li {{ color: #f8fafc !important; }}
            .video-card {{ background: #1e293b; border: 1px solid #334155; }}
            .video-info h3 a {{ color: #f8fafc !important; }}
            .video-info p, .video-info .video-meta {{ color: #cbd5e1 !important; }}
            .shortcut-button {{ background: #334155; color: #f1f5f9 !important; }}
            .shortcut-button:hover {{ background: #475569; }}
            {base_css}
        </style>
    """
    
    return dark_theme if dark_mode else light_theme

# 페이지 설정
st.set_page_config(
    page_title="Haneul CCM Portfolio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True # 기본값을 다크 모드로 설정

# CSS 스타일링 (다크 모드/라이트 모드)
# 기존 CSS를 수정하여 디자인을 개선
st.markdown(get_css_theme(), unsafe_allow_html=True)

# --- 보안 설정: st.secrets에서 API 정보 가져오기 ---
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", "")
CHANNEL_ID = st.secrets.get("CHANNEL_ID", "")
PODCAST_PLAYLIST_ID = st.secrets.get("PODCAST_PLAYLIST_ID", "")

# 데이터 파일 경로
DATA_FILE = "channel_data.json"

def get_default_data():
    """데이터 파일이 없거나 손상되었을 때 사용할 기본 데이터 구조를 반환합니다."""
    return {
        "channel_info": {
            "snippet": {"title": "Haneul CCM", "description": "CCM 작곡가 하늘의 음악 세계에 오신 것을 환영합니다."},
            "statistics": {"subscriberCount": "0", "videoCount": "0", "viewCount": "0"}
        },
        "videos": [],
        "podcast_videos": [],
        "last_updated": "1970-01-01T00:00:00Z"  # 최초 실행 시 무조건 업데이트되도록 아주 오래된 시간으로 설정
    }

def load_channel_data():
    """JSON 파일에서 채널 데이터를 로드하고 데이터 구조를 검증합니다."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 데이터 구조 검증
                videos = data.get("videos", [])
                if videos:
                    first_video = videos[0]
                    if "search_snippet" not in first_video or "details" not in first_video:
                        st.warning("이전 버전의 데이터 파일(channel_data.json)이 감지되었습니다. 새 데이터 구조로 업데이트가 필요합니다.")
                        return get_default_data()
                
                if "channel_info" in data and "videos" in data:
                    return data
        except (json.JSONDecodeError, FileNotFoundError):
            st.warning("데이터 파일을 읽을 수 없어 기본 데이터로 시작합니다.")
    return get_default_data()

def needs_update(data):
    """데이터를 마지막으로 업데이트한 지 24시간이 지났는지 확인합니다."""
    try:
        last_updated_str = data.get("last_updated", "1970-01-01T00:00:00Z")
        # Python 3.10 or lower doesn't handle 'Z' suffix well, so we replace it
        last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
        return datetime.now(last_updated.tzinfo) - last_updated > timedelta(hours=24)
    except Exception as e:
        st.error(f"업데이트 시간 확인 중 오류 발생: {e}")
        return True # 오류 발생 시 업데이트 시도

def fetch_and_cache_youtube_data():
    """YouTube API에서 최신 데이터를 가져와 JSON 파일로 저장(캐시)합니다."""
    # 1. 채널 정보 가져오기
    channel_info = get_channel_info()
    if not channel_info:
        print("채널 정보를 가져올 수 없어 캐싱을 중단합니다.")
        return None

    # 2. 모든 동영상 목록 가져오기
    all_videos_search = get_all_videos()
    
    # 중요: 채널 통계상 동영상은 있는데, API로 하나도 못가져왔다면 오류로 간주하고 캐싱 중단
    # 이렇게 해야 할당량 초과 등으로 빈 목록이 기존 캐시를 덮어쓰는 것을 방지
    video_count_stat = int(channel_info.get('statistics', {}).get('videoCount', '0'))
    if video_count_stat > 0 and not all_videos_search:
        print("채널에 영상이 있지만 목록을 가져오지 못했습니다. API 할당량 초과일 수 있으므로 캐싱을 중단합니다.")
        return None
        
    video_ids = [v['id']['videoId'] for v in all_videos_search]
    video_details = get_video_details(video_ids)

    processed_videos = []
    for video in all_videos_search:
        video_id = video['id']['videoId']
        if video_id in video_details:
            processed_videos.append({
                "search_snippet": video['snippet'],
                "details": video_details[video_id]
            })

    # 3. 팟캐스트 플레이리스트 동영상 가져오기
    podcast_playlist_items = get_playlist_videos(PODCAST_PLAYLIST_ID)

    # 4. 최종 데이터 객체 생성
    new_data = {
        "channel_info": channel_info,
        "videos": processed_videos,
        "podcast_videos": podcast_playlist_items,
        "last_updated": datetime.utcnow().isoformat() + 'Z'
    }

    # 5. 파일에 저장
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
        return new_data
    except Exception as e:
        st.error(f"캐시 파일 저장 중 오류가 발생했습니다: {e}")
        return None

def get_channel_info():
    """채널 기본 정보 가져오기"""
    url = f"https://www.googleapis.com/youtube/v3/channels"
    params = {
        'part': 'snippet,statistics',
        'id': CHANNEL_ID,
        'key': YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 200번대 코드가 아니면 예외 발생
        data = response.json()
        if data['items']:
            return data['items'][0]
    except requests.exceptions.RequestException as e:
        # st.error 대신 콘솔에만 로그를 남기거나 아무것도 하지 않음
        print(f"채널 정보 API 오류: {e}")
    
    return None

def get_videos():
    """채널의 동영상 목록 가져오기"""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'channelId': CHANNEL_ID,
        'order': 'date',
        'type': 'video',
        'maxResults': 20,
        'key': YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()['items']
    except requests.exceptions.RequestException as e:
        print(f"동영상 목록을 가져오는 중 오류가 발생했습니다: {e}")
    
    return []

def get_video_details(video_ids):
    """동영상 상세 정보 가져오기 (여러 ID 처리 및 contentDetails 포함)"""
    url = "https://www.googleapis.com/youtube/v3/videos"
    details = {}
    
    # YouTube API는 한 번에 50개의 ID만 조회 가능
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(batch_ids),
            'key': YOUTUBE_API_KEY
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            for item in data.get('items', []):
                details[item['id']] = item
        except requests.exceptions.RequestException as e:
            print(f"동영상 상세 정보 API 오류: {e}")
    
    return details

def format_date(date_string):
    """날짜 포맷팅"""
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
        return date_obj.strftime('%Y년 %m월 %d일')
    except:
        return date_string

def format_stat(val):
    try:
        return f"{int(val):,}"
    except:
        return "N/A"

def get_all_videos():
    """모든 동영상 가져오기"""
    url = "https://www.googleapis.com/youtube/v3/search"
    videos = []
    params = {
        'part': 'snippet',
        'channelId': CHANNEL_ID,
        'order': 'date',
        'type': 'video',
        'maxResults': 50,
        'key': YOUTUBE_API_KEY
    }
    
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            videos.extend(data.get('items', []))
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
        return videos
    except requests.exceptions.RequestException as e:
        print(f"전체 동영상 목록을 가져오는 중 오류가 발생했습니다: {e}")
        return []

def get_playlist_videos(playlist_id):
    """플레이리스트 동영상 가져오기"""
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    params = {
        'part': 'snippet',
        'playlistId': playlist_id,
        'maxResults': 50,
        'key': YOUTUBE_API_KEY
    }
    
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            videos.extend(data.get('items', []))
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
        return videos
    except requests.exceptions.RequestException as e:
        print(f"플레이리스트 동영상을 가져오는 중 오류가 발생했습니다: {e}")
        return []

def format_duration(duration_str):
    """ISO 8601 duration을 읽기 쉬운 형태로 변환"""
    try:
        duration = isodate.parse_duration(duration_str)
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    except:
        return "0:00"

# --- Firebase 초기화 함수 ---
@st.cache_resource
def initialize_firebase():
    """
    Streamlit Secrets에서 Firebase 서비스 계정 키를 읽어와 앱을 초기화합니다.
    @st.cache_resource를 사용하여 앱 실행 동안 단 한 번만 실행되도록 합니다.
    """
    try:
        # st.secrets에서 키가 문자열이 아닌 딕셔너리 형태로 로드될 경우를 대비
        firebase_creds_dict = st.secrets.get("firebase_credentials")

        if not firebase_creds_dict:
            st.warning("Secrets에서 Firebase 인증 정보를 찾을 수 없습니다. 방문자 카운터가 비활성화됩니다.")
            return None
        
        # 이미 초기화되었는지 확인
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_creds_dict)
            firebase_admin.initialize_app(cred)
        
        # st.success("Firebase에 성공적으로 연결되었습니다!") # 디버깅 완료 후 주석 처리 가능
        return firestore.client()
    except Exception as e:
        st.error(f"Firebase 초기화 중 오류 발생: {e}")
        st.info("Secrets에 입력한 firebase_credentials 키의 형식이 올바른지, 다운로드한 JSON 파일의 내용과 일치하는지 다시 한 번 확인해주세요.")
        return None

def get_and_increment_visitor_count(db):
    """
    Firestore에서 방문자 수를 가져오고 1 증가시킨 후 반환합니다.
    DB가 없거나 오류 발생 시 None을 반환합니다.
    """
    if db is None:
        return None
        
    try:
        doc_ref = db.collection("app_stats").document("visitors")
        doc = doc_ref.get()

        if doc.exists:
            count = doc.to_dict().get("count", 0)
            new_count = count + 1
            doc_ref.update({"count": new_count})
            return new_count
        else:
            # 문서가 없으면 새로 생성
            doc_ref.set({"count": 1})
            return 1
    except Exception as e:
        st.error(f"방문자 수 업데이트 중 오류 발생: {e}")
        return None

def main():
    # --- 데이터 로딩 및 캐시 관리 ---
    channel_data = load_channel_data()

    # 실시간 갱신 버튼 추가
    if st.button('실시간 갱신'):
        with st.spinner("실시간 데이터를 동기화하는 중입니다..."):
            updated_data = fetch_and_cache_youtube_data()
            if updated_data:
                channel_data = updated_data
                st.success("데이터를 실시간으로 갱신했습니다!")
            else:
                st.warning("데이터를 갱신하지 못했습니다. API 할당량이 초과되었을 수 있습니다.")

    if needs_update(channel_data):
        with st.spinner("최신 YouTube 데이터를 동기화하는 중입니다... (API 할당량 초과 시 이전 데이터 표시)"):
            updated_data = fetch_and_cache_youtube_data()
        
        if updated_data:
            channel_data = updated_data
            st.success("데이터를 최신 상태로 업데이트했습니다!")
        else:
            st.warning("데이터를 새로고침하지 못했습니다. API 할당량이 초과되었을 수 있습니다. 마지막으로 저장된 데이터를 표시합니다.")

    # --- 채널 정보 파싱 ---
    channel_info_data = channel_data.get("channel_info", get_default_data()["channel_info"])
    stats = channel_info_data.get('statistics', {})
    title = channel_info_data.get('snippet', {}).get('title', 'Haneul CCM')
    subscriber_count = stats.get('subscriberCount', '0')
    video_count = stats.get('videoCount', '0')
    view_count = stats.get('viewCount', '0')

    # CSS 적용
    st.markdown(get_css_theme(), unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">🎵 Haneul CCM Portfolio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">CCM 하늘빛 음악 세계에 오신 것을 환영합니다</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2.5])

    with col1:
        st.header("🎵 채널 정보")
        st.markdown(f"**Youtube 채널명:** {title}")
        st.markdown(f"**구독자:** {format_stat(subscriber_count)}")
        st.markdown(f"**총 동영상:** {format_stat(video_count)}")
        st.markdown(f"**총 조회수:** {format_stat(view_count)}")
        
        st.header("🔍 필터")
        sort_by = st.selectbox("정렬 기준", ["최신순", "인기순", "제목순"], label_visibility="collapsed")
        search_term = st.text_input("검색어 입력", placeholder="검색어를 입력하세요...")
        
        st.header("📱 연락처")
        st.markdown("**이메일:** webmaster@jiwoosoft.com")
        st.markdown("**홈페이지:** [www.Jiwoosoft.com](http://www.jiwoosoft.com)")
        st.markdown("**YouTube:** [@HaneulCCM](https://www.youtube.com/@HaneulCCM)")
        
        st.header("🌙 테마 설정")
        st.toggle('다크 모드', key='dark_mode')

    with col2:
        # 본문(채널카드+동영상리스트)
        with st.container():
            # 이 아랫부분의 """...""" 안의 내용을 직접 수정하시면 됩니다.
            # <br>은 줄바꿈(Enter)입니다.
            main_description = """
            ✝ [하늘빛] 채널에 오신 여러분을 환영합니다! ✝<br>
            지친 마음에 위로가 되는 찬양을 들려드리고 싶습니다.<br><br>
            하나님의 은혜와 사랑과 따뜻한 위로가<br>
            여러분의 삶에 가득하길 간절히 기도합니다.
            """

            st.markdown(
                f'''
                <div style="padding: 2.5rem 1.5rem; background: linear-gradient(135deg, rgb(85, 111, 180) 0%, rgb(34, 57, 117) 100%); border-radius: 22px; text-align: center; color: white; position: relative; overflow: hidden; box-shadow: rgba(0, 0, 0, 0.1) 0px 8px 32px;">
                    <img src="CCM.png" style="position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; opacity:0.18; filter:blur(4px); z-index:0;" />
                    <div style="position:relative; z-index:1;">
                        <h1 style="margin-bottom:0.5rem; font-size:2.6rem; font-weight:900; letter-spacing:0.02em;">{title}</h1>
                        <div style="font-size:1.15rem; color:#fff; opacity:0.92; margin-bottom:1.5rem; font-weight:400; line-height: 1.7;">{main_description}</div>
                        <div class="stats-container" style="justify-content:center; gap:3.5rem; background:rgba(255,255,255,0.10); margin-bottom:0.5rem;">
                            <div class="stat-item">
                                <div class="stat-number">{format_stat(subscriber_count)}</div>
                                <div class="stat-label">구독자</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{format_stat(video_count)}</div>
                                <div class="stat-label">동영상</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number">{format_stat(view_count)}</div>
                                <div class="stat-label">총 조회수</div>
                            </div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True
            )

            # 바로가기 버튼
           # st.markdown("""
           #<div class="shortcut-buttons" style="margin-bottom:2.2rem;">
           #    <a href="#동영상" class="shortcut-button">동영상</a>
           #    <a href="#Shorts" class="shortcut-button">Shorts</a>
           #</div>
           # """, unsafe_allow_html=True)

            # 동영상 리스트 전체를 하나의 div로 감싸기
            st.markdown('<div id="video-list">', unsafe_allow_html=True)
            
            # 동영상 리스트 헤더와 바로가기 버튼
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2 style="font-size: 1.75rem; margin: 0;">📹 업로드된 동영상</h2>
                <div class="shortcut-buttons">
                    <a href="#일반-동영상" class="shortcut-button">동영상</a>
                    <a href="#shorts" class="shortcut-button">Shorts</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # API에서 동영상 가져오기 -> 캐시된 데이터 사용으로 변경
            all_videos_data = channel_data.get("videos", [])
            podcast_videos_data = channel_data.get("podcast_videos", [])
            
            if all_videos_data:
                # Shorts/일반 동영상 분리
                shorts = []
                normal_videos = []
                
                for video_data in all_videos_data:
                    details = video_data.get('details', {})
                    content_details = details.get('contentDetails', {})
                    duration_str = content_details.get('duration', 'PT0S')
                    
                    try:
                        duration = isodate.parse_duration(duration_str)
                        seconds = duration.total_seconds()
                    except:
                        seconds = 0
                    
                    if seconds <= 70:
                        shorts.append(video_data)
                    else:
                        normal_videos.append(video_data)
                
                # 팟캐스트 플레이리스트 동영상 ID 추출
                podcast_video_ids = set()
                for item in podcast_videos_data:
                    vid = item['snippet']['resourceId']['videoId']
                    podcast_video_ids.add(vid)
                
                # 일반/Shorts에서 팟캐스트 동영상 제외
                normal_videos = [v for v in normal_videos if v['details']['id'] not in podcast_video_ids]
                shorts = [v for v in shorts if v['details']['id'] not in podcast_video_ids]
                
                # 검색 필터 적용
                if search_term:
                    normal_videos = [v for v in normal_videos if search_term.lower() in v['search_snippet']['title'].lower()]
                    shorts = [v for v in shorts if search_term.lower() in v['search_snippet']['title'].lower()]
                
                # 정렬 적용
                if sort_by == "최신순":
                    normal_videos.sort(key=lambda x: x['search_snippet']['publishedAt'], reverse=True)
                    shorts.sort(key=lambda x: x['search_snippet']['publishedAt'], reverse=True)
                elif sort_by == "인기순":
                    normal_videos.sort(key=lambda x: int(x['details'].get('statistics', {}).get('viewCount', '0')), reverse=True)
                    shorts.sort(key=lambda x: int(x['details'].get('statistics', {}).get('viewCount', '0')), reverse=True)
                elif sort_by == "제목순":
                    normal_videos.sort(key=lambda x: x['search_snippet']['title'])
                    shorts.sort(key=lambda x: x['search_snippet']['title'])
                
                # 일반 동영상 표시
                st.subheader("🎞️ 일반 동영상", anchor="일반-동영상")
                if not normal_videos:
                    st.info("일반 동영상이 없습니다.")
                else:
                    for idx, video_data in enumerate(normal_videos, 1):
                        snippet = video_data['search_snippet']
                        details = video_data['details']
                        video_id = details['id']
                        statistics = details.get('statistics', {})
                        content_details = details.get('contentDetails', {})
                        
                        view_count = statistics.get('viewCount', '0')
                        like_count = statistics.get('likeCount', '0')
                        duration_str = content_details.get('duration', 'PT0S')
                        duration = format_duration(duration_str)
                        published_at = format_date(snippet['publishedAt'])
                        
                        st.markdown(f'''
                        <div class="video-card">
                            <div class="video-card-content">
                                <img src="{snippet['thumbnails']['medium']['url']}" class="video-thumbnail">
                                <div class="video-info">
                                    <h3><a href="https://www.youtube.com/watch?v={video_id}" target="_blank">{idx}. {snippet['title']}</a></h3>
                                    <p>{snippet['description'][:150]}...</p>
                                    <div class="video-meta">
                                        조회수: {format_stat(view_count)} | 좋아요: {format_stat(like_count)} | 길이: {duration} | 업로드: {published_at}
                                    </div>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                
                # Shorts 표시
                st.subheader("📱 Shorts", anchor="shorts")
                if not shorts:
                    st.info("Shorts가 없습니다.")
                else:
                    for idx, video_data in enumerate(shorts, 1):
                        snippet = video_data['search_snippet']
                        details = video_data['details']
                        video_id = details['id']
                        statistics = details.get('statistics', {})
                        content_details = details.get('contentDetails', {})
                        
                        view_count = statistics.get('viewCount', '0')
                        like_count = statistics.get('likeCount', '0')
                        duration_str = content_details.get('duration', 'PT0S')
                        duration = format_duration(duration_str)
                        published_at = format_date(snippet['publishedAt'])
                        
                        st.markdown(f'''
                        <div class="video-card">
                            <div class="video-card-content">
                                <img src="{snippet['thumbnails']['medium']['url']}" class="video-thumbnail">
                                <div class="video-info">
                                    <h3><a href="https://www.youtube.com/watch?v={video_id}" target="_blank">{idx}. {snippet['title']} 📱</a></h3>
                                    <p>{snippet['description'][:150]}...</p>
                                    <div class="video-meta">
                                        조회수: {format_stat(view_count)} | 좋아요: {format_stat(like_count)} | 길이: {duration} | 업로드: {published_at}
                                    </div>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                
                # 팟캐스트 표시
                if podcast_videos_data:
                    st.subheader("🎧 팟캐스트")
                    for idx, item in enumerate(podcast_videos_data, 1):
                        snippet = item['snippet']
                        video_id = snippet['resourceId']['videoId']
                        published_at = format_date(snippet['publishedAt'])
                        
                        # 팟캐스트는 상세 정보가 없으므로 일부 정보만 표시합니다.
                        # 필요하다면 fetch_and_cache_youtube_data에서 팟캐스트 동영상도 상세 정보를 가져올 수 있습니다.
                        st.markdown(f'''
                        <div class="video-card">
                            <div class="video-card-content">
                                <img src="{snippet['thumbnails']['medium']['url']}" class="video-thumbnail">
                                <div class="video-info">
                                    <h3><a href="https://www.youtube.com/watch?v={video_id}" target="_blank">{idx}. {snippet['title']} 🎧</a></h3>
                                    <p>{snippet['description'][:150]}...</p>
                                    <div class="video-meta">
                                        업로드: {published_at}
                                    </div>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                
            else:
                st.warning("표시할 동영상이 없습니다. 채널에 동영상을 업로드했는지 확인해주세요.")
            st.markdown('</div>', unsafe_allow_html=True)

    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>© 2025 HaneulCCM. 모든 권리 보유. Powered by Jiwoosoft.</p>
        <p>CCM 은혜의 찬양으로 하나님을 찬양합니다.</p>
    </div>
    """, unsafe_allow_html=True)

def display_videos():
    """실제 유튜브 채널의 동영상 정보를 표시합니다."""
    # 캐시된 데이터를 로드합니다.
    data = load_channel_data()
    if not data or needs_update(data):
        # 데이터가 없거나 업데이트가 필요하면 API를 통해 데이터를 가져옵니다.
        data = fetch_and_cache_youtube_data()

    if not data:
        st.error("유튜브 데이터를 불러올 수 없습니다.")
        return

    # 팟캐스트 동영상을 먼저 표시합니다.
    st.subheader("팟캐스트 동영상")
    for video in data.get('podcast_videos', []):
        st.write(f"**{video['snippet']['title']}**")
        st.write(f"게시일: {format_date(video['snippet']['publishedAt'])}")
        st.write("---")

    # 일반 동영상과 Shorts를 분류하여 표시합니다.
    normal_videos = []
    shorts = []
    for video in data.get('videos', []):
        duration_str = video['details']['contentDetails']['duration']
        duration = isodate.parse_duration(duration_str).total_seconds()
        if duration > 70:
            normal_videos.append(video)
        else:
            shorts.append(video)

    st.subheader("일반 동영상")
    for video in normal_videos:
        st.write(f"**{video['search_snippet']['title']}**")
        st.write(f"게시일: {format_date(video['search_snippet']['publishedAt'])}")
        st.write(f"조회수: {format_stat(video['details']['statistics']['viewCount'])}")
        st.write("---")

    st.subheader("Shorts")
    for video in shorts:
        st.write(f"**{video['search_snippet']['title']}**")
        st.write(f"게시일: {format_date(video['search_snippet']['publishedAt'])}")
        st.write(f"조회수: {format_stat(video['details']['statistics']['viewCount'])}")
        st.write("---")

if __name__ == "__main__":
    main()
    display_videos() 