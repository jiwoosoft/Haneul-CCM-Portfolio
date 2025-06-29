import streamlit as st
import requests
import json
from datetime import datetime
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

def load_channel_data():
    """채널 데이터 로드"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {e}")
    
    # 기본 데이터 반환
    return {
        "channel_info": {
            "title": "Haneul CCM",
            "description": "CCM 작곡가 하늘의 음악 세계에 오신 것을 환영합니다.",
            "subscriber_count": "1,234",
            "video_count": "0",
            "view_count": "0",
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        "videos": []
    }

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
        if response.status_code == 200:
            data = response.json()
            if data['items']:
                return data['items'][0]
        else:
            st.error(f"채널 정보 API 오류 (상태 코드 {response.status_code}): {response.text}")
    except Exception as e:
        st.error(f"채널 정보를 가져오는 중 오류가 발생했습니다: {e}")
    
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
        if response.status_code == 200:
            return response.json()['items']
    except Exception as e:
        st.error(f"동영상 목록을 가져오는 중 오류가 발생했습니다: {e}")
    
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
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    details[item['id']] = item
            else:
                st.error(f"동영상 상세 정보 API 오류 (상태 코드 {response.status_code}): {response.text}")

        except Exception as e:
            st.error(f"동영상 상세 정보를 가져오는 중 오류가 발생했습니다: {e}")
    
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
            if response.status_code != 200:
                st.error(f"동영상 목록 API 오류 (상태 코드 {response.status_code}): {response.text}")
                break
            data = response.json()
            videos.extend(data.get('items', []))
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
        return videos
    except Exception as e:
        st.error(f"동영상 목록을 가져오는 중 오류가 발생했습니다: {e}")
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
            if response.status_code != 200:
                break
            data = response.json()
            videos.extend(data.get('items', []))
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
        return videos
    except Exception as e:
        st.error(f"플레이리스트 동영상을 가져오는 중 오류가 발생했습니다: {e}")
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

def main():
    # 채널 데이터 로드
    channel_data = load_channel_data()
    channel_info_static = channel_data["channel_info"]

    # 채널 정보 가져오기 (API 우선)
    api_channel_info = get_channel_info()
    if api_channel_info:
        stats = api_channel_info.get('statistics', {})
        title = api_channel_info.get('snippet', {}).get('title', 'Haneul CCM')
        description = api_channel_info.get('snippet', {}).get('description', '')
        subscriber_count = stats.get('subscriberCount', '0')
        video_count = stats.get('videoCount', '0')
        view_count = stats.get('viewCount', '0')
    else:
        # API 실패 시 정적 데이터 사용
        title = channel_info_static['title']
        description = channel_info_static['description']
        subscriber_count = channel_info_static['subscriber_count']
        video_count = channel_info_static['video_count']
        view_count = channel_info_static['view_count']

    # CSS 적용
    st.markdown(get_css_theme(), unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">🎵 Haneul CCM Portfolio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">CCM 작곡가 하늘의 음악 세계에 오신 것을 환영합니다</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2.5])

    with col1:
        st.header("🎵 채널 정보")
        st.markdown(f"**채널명:** {title}")
        st.markdown(f"**구독자:** {format_stat(subscriber_count)}")
        st.markdown(f"**총 동영상:** {format_stat(video_count)}")
        st.markdown(f"**총 조회수:** {format_stat(view_count)}")
        
        st.header("🔍 필터")
        sort_by = st.selectbox("정렬 기준", ["최신순", "인기순", "제목순"], label_visibility="collapsed")
        search_term = st.text_input("검색어 입력", placeholder="검색어를 입력하세요...")
        
        st.header("📱 연락처")
        st.markdown("**이메일:** contact@haneulccm.com")
        st.markdown("**인스타그램:** @haneulccm")
        st.markdown("**YouTube:** [Haneul CCM](https://www.youtube.com/@HaneulCCM)")
        
        st.header("🌙 테마 설정")
        st.toggle('다크 모드', key='dark_mode')

    with col2:
        # 본문(채널카드+동영상리스트)
        with st.container():
            st.markdown(
                f'''
                <div style="padding: 2.5rem 1.5rem; background: linear-gradient(135deg, rgb(240, 147, 251) 0%, rgb(245, 87, 108) 100%); border-radius: 22px; text-align: center; color: white; position: relative; overflow: hidden; box-shadow: rgba(0, 0, 0, 0.1) 0px 8px 32px;">
                    <img src="CCM.png" style="position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; opacity:0.18; filter:blur(4px); z-index:0;" />
                    <div style="position:relative; z-index:1;">
                        <h1 style="margin-bottom:0.5rem; font-size:2.6rem; font-weight:900; letter-spacing:0.02em;">{title}</h1>
                        <div style="font-size:1.15rem; color:#fff; opacity:0.92; margin-bottom:1.5rem; font-weight:400;">{description if description else '채널 소개글을 작성해 주세요.'}</div>
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
            st.markdown("""
            <div class="shortcut-buttons" style="margin-bottom:2.2rem;">
                <a href="#동영상" class="shortcut-button">동영상</a>
                <a href="#Shorts" class="shortcut-button">Shorts</a>
            </div>
            """, unsafe_allow_html=True)

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
            
            # API에서 동영상 가져오기
            videos = get_all_videos()
            
            if videos:
                # 동영상 상세 정보 가져오기
                video_ids = [v['id']['videoId'] for v in videos]
                video_details = get_video_details(video_ids)
                
                # Shorts/일반 동영상 분리
                shorts = []
                normal_videos = []
                
                for video in videos:
                    video_id = video['id']['videoId']
                    details = video_details.get(video_id, {})
                    content_details = details.get('contentDetails', {})
                    duration_str = content_details.get('duration', 'PT0S')
                    
                    try:
                        duration = isodate.parse_duration(duration_str)
                        seconds = duration.total_seconds()
                    except:
                        seconds = 0
                    
                    if seconds <= 60:
                        shorts.append((video, details))
                    else:
                        normal_videos.append((video, details))
                
                # 팟캐스트 플레이리스트 동영상 가져오기
                podcast_videos = get_playlist_videos(PODCAST_PLAYLIST_ID)
                podcast_video_ids = set()
                for item in podcast_videos:
                    vid = item['snippet']['resourceId']['videoId']
                    podcast_video_ids.add(vid)
                
                # 일반/Shorts에서 팟캐스트 동영상 제외
                normal_videos = [t for t in normal_videos if t[0]['id']['videoId'] not in podcast_video_ids]
                shorts = [t for t in shorts if t[0]['id']['videoId'] not in podcast_video_ids]
                
                # 검색 필터 적용
                if search_term:
                    normal_videos = [t for t in normal_videos if search_term.lower() in t[0]['snippet']['title'].lower()]
                    shorts = [t for t in shorts if search_term.lower() in t[0]['snippet']['title'].lower()]
                
                # 정렬 적용
                if sort_by == "최신순":
                    normal_videos.sort(key=lambda x: x[0]['snippet']['publishedAt'], reverse=True)
                    shorts.sort(key=lambda x: x[0]['snippet']['publishedAt'], reverse=True)
                elif sort_by == "인기순":
                    normal_videos.sort(key=lambda x: int(x[1].get('statistics', {}).get('viewCount', '0')), reverse=True)
                    shorts.sort(key=lambda x: int(x[1].get('statistics', {}).get('viewCount', '0')), reverse=True)
                elif sort_by == "제목순":
                    normal_videos.sort(key=lambda x: x[0]['snippet']['title'])
                    shorts.sort(key=lambda x: x[0]['snippet']['title'])
                
                # 일반 동영상 표시
                st.subheader("🎞️ 일반 동영상", anchor="일반-동영상")
                if not normal_videos:
                    st.info("일반 동영상이 없습니다.")
                else:
                    for idx, (video, details) in enumerate(normal_videos, 1):
                        snippet = video['snippet']
                        video_id = video['id']['videoId']
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
                                        조회수: {int(view_count):,} | 좋아요: {int(like_count):,} | 길이: {duration} | 업로드: {published_at}
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
                    for idx, (video, details) in enumerate(shorts, 1):
                        snippet = video['snippet']
                        video_id = video['id']['videoId']
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
                                        조회수: {int(view_count):,} | 좋아요: {int(like_count):,} | 길이: {duration} | 업로드: {published_at}
                                    </div>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                
                # 팟캐스트 표시
                if podcast_videos:
                    st.subheader("🎧 팟캐스트")
                    for idx, item in enumerate(podcast_videos, 1):
                        snippet = item['snippet']
                        video_id = snippet['resourceId']['videoId']
                        published_at = format_date(snippet['publishedAt'])
                        
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
                # API 호출 실패 시 정적 데이터 사용
                st.warning("YouTube API에서 동영상을 가져올 수 없어 샘플 데이터를 표시합니다.")
                
                data = load_channel_data()
                sample_videos = data["videos"]
                
                for idx, video in enumerate(sample_videos, 1):
                    st.markdown(f"""
                    <div class="video-card">
                        <div class="video-card-content">
                            <img src="{video['thumbnail']}" class="video-thumbnail">
                            <div class="video-info">
                                <h3>
                                    <a href="{video['youtube_url']}" target="_blank">
                                        {idx}. {video['title']}
                                    </a>
                                </h3>
                                <p>{video['description']}</p>
                                <div class="video-meta">
                                    조회수: {video['views']} | 좋아요: {video['likes']} | 길이: {video['duration']} | 업로드: {format_date(video['published_at'])}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>© 2024 Haneul CCM. 모든 권리 보유.</p>
        <p>CCM 작곡과 찬양으로 하나님을 찬양합니다.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 