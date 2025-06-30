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

# --- 1. 스타일링(CSS) 함수 ---
def get_css():
    dark_mode = st.session_state.get('dark_mode', True)
    
    base_css = """
        .block-container { max-width: 1200px !important; padding: 2rem 1rem 10rem 1rem !important; }
        .main-header { font-size: 2.8rem; font-weight: bold; text-align: center; margin-bottom: 0.5rem; }
        .sub-header { font-size: 1.2rem; text-align: center; margin-bottom: 3rem; opacity: 0.8; }
        .video-card { border-radius: 15px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: all 0.2s ease-in-out; }
        .video-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
        .video-card-content { display: flex; align-items: flex-start; gap: 1rem; }
        .video-thumbnail { width: 160px; height: 90px; object-fit: cover; border-radius: 8px; }
        .video-info h3 { margin: 0 0 0.5rem 0; font-size: 1.1rem; font-weight: bold; }
        .video-info p { margin: 0.3rem 0; font-size: 0.9rem; }
        .video-meta { font-size: 0.8rem; opacity: 0.7; margin-top: 0.5rem; }
    """
    
    light_theme = f"""
        <style>
            body {{ background-color: #f0f2f6; }}
            .stApp {{ background-color: #f0f2f6; color: #333; }}
            .video-card {{ background: #ffffff; }}
            h1, h2, h3, h4, h5, h6, p, li, strong {{ color: #333; }}
            a {{ color: #1f77b4; }}
            {base_css}
        </style>
    """
            
    dark_theme = f"""
        <style>
            body {{ background-color: #0f172a; }}
            .stApp {{ background-color: #0f172a; color: #e2e8f0; }}
            .video-card {{ background: #1e293b; border: 1px solid #334155; }}
            h1, h2, h3, h4, h5, h6, p, li, strong {{ color: #e2e8f0; }}
            a {{ color: #60a5fa; }}
            {base_css}
        </style>
    """

    return dark_theme if dark_mode else light_theme

# --- 2. 페이지 기본 설정 ---
st.set_page_config(page_title="Haneul CCM Portfolio", page_icon="🎵", layout="wide", initial_sidebar_state="auto")

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

st.markdown(get_css(), unsafe_allow_html=True)

# --- 3. 전역 변수 및 보안 설정 ---
YOUTUBE_API_KEY = st.secrets.get("youtube_api", {}).get("api_key", "")
CHANNEL_ID = "UC4nfPrwy8bi0q-eryODxiGQ"
PODCAST_PLAYLIST_ID = "PL-3k4y9L5-k19y3Yn8a2nB_yS1E8A9GR"

# --- 4. 데이터 처리 및 API 호출 함수 (올바른 캐시 구조) ---

@st.cache_data(ttl=3600)
def get_channel_info(api_key, channel_id):
    """채널 정보를 가져옵니다. (1시간 캐시)"""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("pageInfo", {}).get("totalResults", 0) > 0 and "items" in data:
            return data["items"][0]
        else:
            return None
    except Exception as e:
        print(f"Error getting channel info: {e}")
        return None

@st.cache_data(ttl=3600)
def get_all_videos(api_key, channel_id):
    videos = []
    params = {'part': 'snippet', 'channelId': channel_id, 'order': 'date', 'type': 'video', 'maxResults': 50, 'key': api_key}
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
    except Exception as e:
        print(f"Error getting all videos: {e}")
    return videos

@st.cache_data(ttl=3600)
def get_video_details(api_key, video_ids):
    details = {}
    for i in range(0, len(video_ids), 50):
        batch_ids = ','.join(video_ids[i:i+50])
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={batch_ids}&key={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            for item in response.json().get('items', []):
                details[item['id']] = item
        except Exception as e:
            print(f"Error getting video details: {e}")
    return details

@st.cache_data(ttl=3600)
def get_playlist_videos(api_key, playlist_id):
    videos = []
    params = {'part': 'snippet', 'playlistId': playlist_id, 'maxResults': 50, 'key': api_key}
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
    except Exception as e:
        print(f"Error getting playlist videos: {e}")
    return videos

def get_combined_api_data(api_key, channel_id, podcast_playlist_id):
    channel_info = get_channel_info(api_key, channel_id)
    if not channel_info: 
        return None
    
    all_videos_search = get_all_videos(api_key, channel_id)
    video_ids = [v['id']['videoId'] for v in all_videos_search]
    video_details = get_video_details(api_key, video_ids)
    
    processed_videos = [
        {"search_snippet": v['snippet'], "details": video_details[v['id']['videoId']]}
        for v in all_videos_search if v['id']['videoId'] in video_details
    ]
    
    podcast_videos = get_playlist_videos(api_key, podcast_playlist_id)
    
    return {
        "channel_info": channel_info,
        "videos": processed_videos,
        "podcast_videos": podcast_videos,
    }

# --- 5. Firebase 관련 함수 ---
@st.cache_resource
def initialize_firebase():
    try:
        creds_dict = dict(st.secrets["firebase_credentials"])
        db_url = st.secrets["firebase_database"]["databaseURL"]
        if not firebase_admin._apps:
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred, {'databaseURL': db_url})
        return firestore.client()
    except Exception as e:
        if 'db' not in st.session_state:
            st.error(f"Firebase 초기화 실패: {e}")
        return None

def get_and_increment_visitor_count(_db):
    if _db is None: return "N/A"
    doc_ref = _db.collection('visitors').document('counter')
    
    @firestore.transactional
    def update_in_transaction(transaction, doc_ref):
        snapshot = doc_ref.get(transaction=transaction)
        current_count = snapshot.to_dict().get("count", 0) if snapshot.exists else 0
        new_count = current_count + 1
        transaction.set(doc_ref, {"count": new_count})
        return new_count
    try:
        transaction = _db.transaction()
        return update_in_transaction(transaction, doc_ref)
    except Exception as e:
        print(f"방문자 수 업데이트 오류: {e}")
        return "N/A"

# --- 6. 헬퍼 함수 ---
def format_stat(val):
    try: return f"{int(val):,}"
    except: return "0"

def format_date(date_string):
    try: return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y년 %m월 %d일')
    except: return "날짜 정보 없음"

def format_duration(duration_str):
    try:
        duration = isodate.parse_duration(duration_str)
        total_seconds = int(duration.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"
    except:
        return ""

# --- 7. 메인 애플리케이션 실행 ---
def main():
    db = initialize_firebase()
    
    api_data = get_combined_api_data(YOUTUBE_API_KEY, CHANNEL_ID, PODCAST_PLAYLIST_ID)
    
    if not api_data:
        st.error("YouTube API에서 데이터를 가져오는 데 실패했습니다. 채널이 비공개이거나 API 할당량을 초과했을 수 있습니다.")
        return

    channel_info = api_data["channel_info"]
    all_videos = api_data["videos"]
    podcast_videos_list = api_data["podcast_videos"]
    stats = channel_info.get('statistics', {})
    title = channel_info.get('snippet', {}).get('title', 'Haneul CCM')

    # --- 사이드바 UI ---
    with st.sidebar:
        st.markdown(f"## {title}")
        
        visitor_count = get_and_increment_visitor_count(db)
        if visitor_count != "N/A":
            st.markdown(f"**방문자 수:** {visitor_count:,}")

        st.markdown("---")
        st.subheader("채널 정보")
        st.markdown(f"**구독자:** {format_stat(stats.get('subscriberCount'))}")
        st.markdown(f"**총 동영상:** {format_stat(stats.get('videoCount'))}")
        st.markdown(f"**총 조회수:** {format_stat(stats.get('viewCount'))}")
        st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown("---")
        st.subheader("테마 설정")
        st.toggle('다크 모드', key='dark_mode')
    
    # --- 메인 컨텐츠 UI ---
    st.markdown(f"<h1 class='main-header'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>{channel_info.get('snippet', {}).get('description', '')}</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🎬 모든 동영상", "🎙️ 팟캐스트"])

    with tab1:
        st.markdown("### 전체 동영상 목록")
        for video_data in all_videos:
            snippet = video_data['search_snippet']
            details = video_data.get('details', {})
            video_id = details.get('id', snippet['id']['videoId'])
            
            with st.container():
                st.markdown(f"""
                <div class="video-card">
                    <div class="video-card-content">
                        <img src="{snippet['thumbnails']['medium']['url']}" class="video-thumbnail">
                        <div class="video-info">
                            <h3><a href="https://www.youtube.com/watch?v={video_id}" target="_blank">{snippet['title']}</a></h3>
                            <div class="video-meta">
                                <span>{format_date(snippet['publishedAt'])}</span>
                                | <span>조회수 {format_stat(details.get('statistics', {}).get('viewCount', '0'))}</span>
                                | <span>길이 {format_duration(details.get('contentDetails', {}).get('duration', ''))}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 팟캐스트 재생목록")
        for item in podcast_videos_list:
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']
            
            with st.container():
                st.markdown(f"""
                <div class="video-card">
                    <div class="video-card-content">
                        <img src="{snippet['thumbnails']['medium']['url']}" class="video-thumbnail">
                        <div class="video-info">
                            <h3><a href="https://www.youtube.com/watch?v={video_id}" target="_blank">{snippet['title']}</a></h3>
                            <div class="video-meta">
                                <span>{format_date(snippet['publishedAt'])}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 