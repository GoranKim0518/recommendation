import streamlit as st
import requests
import os
from datetime import datetime

# 환경 변수 바인딩
BACKEND_IP = os.getenv("BACKEND_IP", "localhost").strip()
API_URL = f"http://{BACKEND_IP}:8000/api/recommend"

st.set_page_config(page_title="Lunch Engine", page_icon="🍱", layout="centered")

# 타임스탬프
if "history_log" not in st.session_state:
    st.session_state.history_log = []

# Frontend Cache + 네트워크 try-except 예외 처리
@st.cache_data(ttl=600, show_spinner=False)
def get_recommendation_from_api(payload, url):
    try:
        # 네트워크 지연 현상을 대비한 5초 타임아웃 제한 조건 설정
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("🚫 백엔드 API 서버에 연결할 수 없습니다. 포트 개방 상태나 컨테이너 구동 여부를 확인하세요.")
    except requests.exceptions.Timeout:
        st.error("⏰ 요청 시간이 초과되었습니다. AWS 클라우드 네트워크 연결 상태를 확인하세요.")
    except requests.exceptions.HTTPError:
        st.error(f"🌐 서버 에러가 발생했습니다. (HTTP Status: {response.status_code})")
    except Exception as e:
        st.error(f"❗ 시스템 장애가 발생했습니다: {e}")
    return None

st.title("🍱 점심 추천 엔진")
st.write("지금 딱 당기시는 스타일을 골라보세요! 점심 메뉴를 추천해 드립니다.")
st.markdown("---")

with st.form("main_input_form"):
    st.subheader("🔮 지금 어떤 스타일이 당기시나요?")
    
    target_category = st.selectbox("1단계: 오늘 원하는 음식 종류를 고르세요", ["한식", "중식", "양식", "일식"])
    target_soup_type = st.radio("2단계: 국물 요리를 선호하시나요?", ["국물 있음", "국물 없음"], horizontal=True)
    target_spiciness = st.select_slider("3단계: 원하는 매운맛 정도를 선택하세요", options=["순한맛", "보통", "매운맛"])

    if target_soup_type == "국물 있음":
        target_cooking_style = st.selectbox("4단계: 원하는 조리 방식을 선택하세요", ["탕류/국물", "볶음/조림"])
    else:
        target_cooking_style = st.selectbox("4단계: 원하는 조리 방식을 선택하세요", ["튀김/구이", "볶음/조림", "회/비빔"])
        
    target_vibe = st.radio("5단계: 어떤 성격의 식사를 원하시나요?", ["가성비", "든든하게", "특별한날"], horizontal=True)
    
    submitted = st.form_submit_button("🔍 내 스타일과 어울리는 음식 찾기")

if submitted:
    payload = {
        "target_category": target_category,
        "target_soup_type": target_soup_type,
        "target_cooking_style": target_cooking_style,
        "target_spiciness": target_spiciness,
        "target_vibe": target_vibe
    }
    
    with st.spinner("지금 가장 당기는 스타일과 매칭되는 음식을 찾는 중..."):
        result = get_recommendation_from_api(payload, API_URL)
    
    if result:
        # 타임스탬프 로그 생성 및 기록
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history_log.append({"time": current_time, "menu": result['recommended_menu']})
        
        st.balloons()
        st.subheader(f"🎯 오늘 추천하는 최적 메뉴: **{result['recommended_menu']}**")
        st.markdown(f"📊 **스타일 일치도: {result['match_score']}%**")
        st.progress(result['match_score'] / 100)
        
        # 백엔드에서 보낸 직관적인 사유(rationale) 출력
        st.info(f"💡 {result['rationale']}")

# 사이드바 레이아웃(타임스탬프 + 로그)
with st.sidebar:
    st.header("🕒 실시간 추천 로그")
    if not st.session_state.history_log:
        st.write("아직 생성된 히스토리 로그가 없습니다.")
    for log in reversed(st.session_state.history_log):
        st.markdown(f"**[{log['time']}]**")
        st.write(f"👉 메뉴명: {log['menu']}")
        st.divider()