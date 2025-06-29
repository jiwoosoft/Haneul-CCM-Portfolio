import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="Haneul CCM Data Manager",
    page_icon="⚙️",
    layout="wide"
)

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

def save_channel_data(data):
    """채널 데이터 저장"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"데이터 파일을 저장하는 중 오류가 발생했습니다: {e}")
        return False

def main():
    st.title("⚙️ Haneul CCM Data Manager")
    st.markdown("채널 정보와 동영상 데이터를 관리하는 도구입니다.")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 채널 정보", "🎬 동영상 관리", "📈 통계", "💾 데이터 내보내기"])
    
    # 데이터 로드
    data = load_channel_data()
    
    with tab1:
        st.header("📊 채널 정보 관리")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("기본 정보")
            channel_info = data["channel_info"]
            
            title = st.text_input("채널명", value=channel_info.get("title", ""))
            description = st.text_area("채널 설명", value=channel_info.get("description", ""), height=100)
            
            st.subheader("통계 정보")
            subscriber_count = st.text_input("구독자 수", value=channel_info.get("subscriber_count", ""))
            video_count = st.text_input("총 동영상 수", value=str(len(data["videos"])))
            view_count = st.text_input("총 조회수", value=channel_info.get("view_count", ""))
        
        with col2:
            st.subheader("미리보기")
            st.markdown(f"""
            **채널명:** {title}
            
            **설명:** {description}
            
            **구독자:** {subscriber_count}
            **동영상:** {video_count}
            **조회수:** {view_count}
            """)
        
        if st.button("💾 채널 정보 저장"):
            data["channel_info"].update({
                "title": title,
                "description": description,
                "subscriber_count": subscriber_count,
                "video_count": video_count,
                "view_count": view_count,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            if save_channel_data(data):
                st.success("✅ 채널 정보가 성공적으로 저장되었습니다!")
    
    with tab2:
        st.header("🎬 동영상 관리")
        
        # 동영상 목록 표시
        videos = data["videos"]
        
        if videos:
            st.subheader(f"현재 등록된 동영상 ({len(videos)}개)")
            
            # 동영상 테이블
            video_data = []
            for i, video in enumerate(videos):
                video_data.append({
                    "번호": i + 1,
                    "제목": video["title"],
                    "업로드일": video["published_at"][:10],
                    "조회수": video["views"],
                    "좋아요": video["likes"],
                    "길이": video["duration"]
                })
            
            df = pd.DataFrame(video_data)
            st.dataframe(df, use_container_width=True)
        
        # 새 동영상 추가
        st.subheader("새 동영상 추가")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_title = st.text_input("동영상 제목")
            video_description = st.text_area("동영상 설명", height=100)
            published_date = st.date_input("업로드 날짜")
            published_time = st.time_input("업로드 시간")
            
        with col2:
            youtube_url = st.text_input("YouTube URL")
            duration = st.text_input("재생 시간 (예: 4:32)")
            views = st.text_input("조회수")
            likes = st.text_input("좋아요 수")
            thumbnail_url = st.text_input("썸네일 URL (선택사항)")
        
        if st.button("➕ 동영상 추가"):
            if video_title and youtube_url:
                # 날짜와 시간 결합
                published_datetime = datetime.combine(published_date, published_time)
                
                new_video = {
                    "id": f"video{len(videos) + 1}",
                    "title": video_title,
                    "description": video_description,
                    "published_at": published_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "thumbnail": thumbnail_url or "https://via.placeholder.com/320x180/667eea/ffffff?text=CCM+Music",
                    "youtube_url": youtube_url,
                    "duration": duration,
                    "views": views or "0",
                    "likes": likes or "0"
                }
                
                data["videos"].append(new_video)
                data["channel_info"]["video_count"] = str(len(data["videos"]))
                data["channel_info"]["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if save_channel_data(data):
                    st.success("✅ 동영상이 성공적으로 추가되었습니다!")
                    st.rerun()
            else:
                st.error("❌ 제목과 YouTube URL은 필수입니다.")
        
        # 동영상 삭제
        if videos:
            st.subheader("동영상 삭제")
            video_titles = [v["title"] for v in videos]
            video_to_delete = st.selectbox("삭제할 동영상 선택", video_titles)
            
            if st.button("🗑️ 선택한 동영상 삭제"):
                data["videos"] = [v for v in videos if v["title"] != video_to_delete]
                data["channel_info"]["video_count"] = str(len(data["videos"]))
                data["channel_info"]["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if save_channel_data(data):
                    st.success("✅ 동영상이 성공적으로 삭제되었습니다!")
                    st.rerun()
    
    with tab3:
        st.header("📈 통계")
        
        videos = data["videos"]
        
        if videos:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 동영상 수", len(videos))
            
            with col2:
                total_views = sum(int(v["views"].replace(",", "")) for v in videos if v["views"].replace(",", "").isdigit())
                st.metric("총 조회수", f"{total_views:,}")
            
            with col3:
                total_likes = sum(int(v["likes"].replace(",", "")) for v in videos if v["likes"].replace(",", "").isdigit())
                st.metric("총 좋아요 수", f"{total_likes:,}")
            
            with col4:
                avg_duration = "계산 중..."
                st.metric("평균 재생 시간", avg_duration)
            
            # 최근 업로드된 동영상
            st.subheader("최근 업로드된 동영상")
            recent_videos = sorted(videos, key=lambda x: x["published_at"], reverse=True)[:5]
            
            for video in recent_videos:
                st.markdown(f"**{video['title']}** - {video['published_at'][:10]}")
        
        else:
            st.info("등록된 동영상이 없습니다.")
    
    with tab4:
        st.header("💾 데이터 내보내기")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("JSON 형식")
            if st.button("📄 JSON 다운로드"):
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💾 JSON 파일 다운로드",
                    data=json_str,
                    file_name="channel_data.json",
                    mime="application/json"
                )
        
        with col2:
            st.subheader("CSV 형식")
            if videos:
                if st.button("📊 CSV 다운로드"):
                    video_data = []
                    for video in videos:
                        video_data.append({
                            "제목": video["title"],
                            "설명": video["description"],
                            "업로드일": video["published_at"],
                            "YouTube URL": video["youtube_url"],
                            "재생시간": video["duration"],
                            "조회수": video["views"],
                            "좋아요": video["likes"]
                        })
                    
                    df = pd.DataFrame(video_data)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="💾 CSV 파일 다운로드",
                        data=csv,
                        file_name="videos.csv",
                        mime="text/csv"
                    )
            else:
                st.info("내보낼 동영상이 없습니다.")
        
        # 데이터 백업
        st.subheader("🔒 데이터 백업")
        if st.button("💾 백업 생성"):
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_data = {
                "backup_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "data": data
            }
            
            backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2)
            st.download_button(
                label=f"💾 {backup_filename} 다운로드",
                data=backup_json,
                file_name=backup_filename,
                mime="application/json"
            )

if __name__ == "__main__":
    main() 