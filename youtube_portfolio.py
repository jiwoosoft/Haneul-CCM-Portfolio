import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import os
from PIL import Image
import io
import base64
import isodate
import firebase_admin
from firebase_admin import credentials, firestore

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

# CSS 스타일링
st.markdown(get_css_theme(), unsafe_allow_html=True)

# --- 보안 및 전역 설정 ---
YOUTUBE_API_KEY = st.secrets.get("youtube_api", {}).get("api_key", "")
CHANNEL_ID = "UC3_tY22M9-1a_Z-a_i-x5iA" 
PODCAST_PLAYLIST_ID = "PL-3k4y9L5-k19y3Yn8a2nB_yS1E8A9GR"

def get_default_data():
    """데이터가 없을 때 사용할 기본 데이터 구조를 반환합니다."""
    return {
        "channel_info": {
            "snippet": {"title": "Haneul CCM", "description": "CCM 작곡가 하늘의 음악 세계에 오신 것을 환영합니다. 이곳에서 저의 다양한 음악과 활동을 만나보세요."},
            "statistics": {"subscriberCount": "0", "videoCount": "0", "viewCount": "0"}
        },
        "videos": [],
        "podcast_videos": [],
        "last_updated": "1970-01-01T00:00:00Z"
    }

def load_data_from_firestore(db):
    """Firestore에서 캐시된 채널 데이터를 로드합니다."""
    if db is None:
        st.warning("데이터베이스에 연결할 수 없어 기본 데이터를 표시합니다.")
        return get_default_data()
    try:
        doc_ref = db.collection('app_cache').document('youtube_data')
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return get_default_data()
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return get_default_data()

def needs_update(data):
    """데이터를 마지막으로 업데이트한 지 24시간이 지났는지 확인합니다."""
    try:
        last_updated_str = data.get("last_updated", "1970-01-01T00:00:00Z")
        last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
        return datetime.now(last_updated.tzinfo) - last_updated > timedelta(hours=24)
    except Exception:
        return True

def fetch_and_cache_youtube_data(db):
    """YouTube API에서 최신 데이터를 가져와 Firestore에 저장(캐시)합니다."""
    if db is None:
        st.error("데이터베이스에 연결되지 않아 캐시를 업데이트할 수 없습니다.")
        return None

    channel_info = get_channel_info()
    if not channel_info:
        st.warning("채널 정보를 가져올 수 없어 캐싱을 중단합니다.")
        return None

    all_videos_search = get_all_videos()
    video_count_stat = int(channel_info.get('statistics', {}).get('videoCount', '0'))
    if video_count_stat > 0 and not all_videos_search:
        st.warning("채널에 영상이 있지만 목록을 가져오지 못했습니다. API 할당량 초과일 수 있으므로 캐싱을 중단합니다.")
        return None
        
    video_ids = [v['id']['videoId'] for v in all_videos_search]
    video_details = get_video_details(video_ids)
    processed_videos = [
        {"search_snippet": v['snippet'], "details": video_details[v['id']['videoId']]}
        for v in all_videos_search if v['id']['videoId'] in video_details
    ]

    podcast_playlist_items = get_playlist_videos(PODCAST_PLAYLIST_ID)

    new_data = {
        "channel_info": channel_info,
        "videos": processed_videos,
        "podcast_videos": podcast_playlist_items,
        "last_updated": datetime.utcnow().isoformat() + 'Z'
    }

    try:
        doc_ref = db.collection('app_cache').document('youtube_data')
        doc_ref.set(new_data)
        st.toast("✅ 채널 정보가 성공적으로 업데이트 및 저장되었습니다!")
        return new_data
    except Exception as e:
        st.error(f"Firestore에 캐시 데이터 저장 중 오류 발생: {e}")
        return None

def get_channel_info():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['items'][0]
    except (requests.exceptions.RequestException, IndexError, KeyError) as e:
        print(f"채널 정보 API 오류: {e}")
        return None

def get_all_videos():
    videos = []
    params = {'part': 'snippet', 'channelId': CHANNEL_ID, 'order': 'date', 'type': 'video', 'maxResults': 50, 'key': YOUTUBE_API_KEY}
    try:
        while True:
            response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
            response.raise_for_status()
            data = response.json()
            videos.extend(data.get('items', []))
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
    except requests.exceptions.RequestException as e:
        print(f"전체 동영상 목록 API 오류: {e}")
    return videos

def get_video_details(video_ids):
    details = {}
    for i in range(0, len(video_ids), 50):
        batch_ids = ','.join(video_ids[i:i+50])
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={batch_ids}&key={YOUTUBE_API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            for item in response.json().get('items', []):
                details[item['id']] = item
        except requests.exceptions.RequestException as e:
            print(f"동영상 상세 정보 API 오류: {e}")
    return details

def get_playlist_videos(playlist_id):
    videos = []
    params = {'part': 'snippet', 'playlistId': playlist_id, 'maxResults': 50, 'key': YOUTUBE_API_KEY}
    try:
        while True:
            response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params=params)
            response.raise_for_status()
            data = response.json()
            videos.extend(data.get('items', []))
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
    except requests.exceptions.RequestException as e:
        print(f"플레이리스트 동영상 API 오류: {e}")
    return videos

def format_duration(duration_str):
    try:
        return str(isodate.parse_duration(duration_str))
    except:
        return "0:00"

def format_stat(val):
    try:
        return f"{int(val):,}"
    except (ValueError, TypeError):
        return "0"

@st.cache_resource
def initialize_firebase():
    """Firebase 앱을 초기화하고 Firestore 클라이언트 객체를 반환합니다."""
    try:
        if "firebase_credentials" in st.secrets and "firebase_database" in st.secrets:
            creds_dict = dict(st.secrets["firebase_credentials"])
            if creds_dict and all(isinstance(v, str) for v in creds_dict.values()):
                if not firebase_admin._apps:
                    cred = credentials.Certificate(creds_dict)
                    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_database"]["databaseURL"]})
                return firestore.client()
    except Exception as e:
        st.error(f"Firebase 초기화 중 오류 발생: {e}")
    return None

def get_and_increment_visitor_count(db):
    """Firestore에서 방문자 수를 가져오고 1 증가시킨 뒤 반환합니다."""
    if db is None: return "N/A"
    try:
        doc_ref = db.collection('visitors').document('counter')
        doc = doc_ref.get()
        count = doc.to_dict().get("count", 0) + 1 if doc.exists else 1
        doc_ref.set({"count": count})
        return count
    except Exception as e:
        st.error(f"방문자 수 업데이트 중 오류 발생: {e}")
        return "N/A"

def main():
    db = initialize_firebase()
    data = load_data_from_firestore(db)

    if needs_update(data):
        st.toast("최신 채널 정보를 가져오는 중... ⏳")
        new_data = fetch_and_cache_youtube_data(db)
        if new_data:
            data = new_data
        else:
            st.warning("데이터 업데이트에 실패했습니다. 잠시 후 다시 시도해주세요. (API 할당량 초과일 수 있습니다)")

    channel_info = data.get("channel_info", get_default_data()["channel_info"])
    stats = channel_info.get('statistics', {})
    title = channel_info.get('snippet', {}).get('title', 'Haneul CCM')
    
    with st.sidebar:
        try:
            with open("CCM.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{encoded_string}" width="120"></div>', unsafe_allow_html=True)
        except FileNotFoundError:
            st.title("🎵 Haneul CCM")

        visitor_count = get_and_increment_visitor_count(db)
        if visitor_count != "N/A":
            st.markdown(f"**방문자 수:** {visitor_count:,}")

        st.markdown("---")
        st.subheader("채널 정보")
        st.markdown(f"""
        - **YouTube 채널명:** {title}
        - **구독자:** {format_stat(stats.get('subscriberCount'))}
        - **총 동영상:** {format_stat(stats.get('videoCount'))}
        - **총 조회수:** {format_stat(stats.get('viewCount'))}
        """)
        
        last_updated_str = data.get("last_updated", "1970-01-01T00:00:00Z").replace('Z', '+00:00')
        last_updated_dt = datetime.fromisoformat(last_updated_str)
        st.caption(f"마지막 업데이트: {last_updated_dt.strftime('%Y-%m-%d %H:%M:%S')}")

        st.markdown("---")
        st.info("이 포트폴리오는 Streamlit을 사용하여 제작되었습니다.")
        
        st.markdown("---")
        st.toggle('다크 모드', key='dark_mode')

    st.markdown(f"<h1 class='main-header'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>{channel_info.get('snippet', {}).get('description', '')}</p>", unsafe_allow_html=True)

    videos = data.get("videos", [])
    if videos:
        tab1, tab2 = st.tabs(["🎬 모든 동영상", "🎙️ 팟캐스트"])
        with tab1:
            st.subheader("전체 동영상 목록")
            # This is a simplified view. Add search/sort/filter as needed.
            for video_data in videos:
                snippet = video_data.get('search_snippet', {})
                details = video_data.get('details', {})
                video_id = details.get('id', '')
                st.markdown(f"#### [{snippet.get('title')}] (https://www.youtube.com/watch?v={video_id})")
                st.image(snippet.get('thumbnails', {}).get('medium', {}).get('url'))
                st.write(snippet.get('description')[:200])
        
        with tab2:
            st.subheader("팟캐스트 목록")
            podcast_videos = data.get("podcast_videos", [])
            if podcast_videos:
                 for item in podcast_videos:
                    snippet = item.get('snippet', {})
                    video_id = snippet.get('resourceId', {}).get('videoId', '')
                    st.markdown(f"#### [{snippet.get('title')}] (https://www.youtube.com/watch?v={video_id})")
                    st.image(snippet.get('thumbnails', {}).get('medium', {}).get('url'))
            else:
                st.info("팟캐스트 동영상이 없습니다.")
    else:
        st.warning("표시할 동영상이 없습니다. 채널 정보를 성공적으로 불러왔는지 확인해주세요.")

if __name__ == "__main__":
    main() 