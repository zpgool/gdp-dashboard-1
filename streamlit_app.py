import streamlit as st
import requests

@st.cache_data(ttl=600)
def get_live_weather(city_name):
    """
    wttr.in API를 사용하여 도시의 실시간 날씨 정보를 가져옵니다.
    """
    url = f"https://wttr.in/{city_name}?format=j1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        current_condition = data['current_condition'][0]
        nearest_area = data['nearest_area'][0]['areaName'][0]['value']
        
        weather_info = {
            'city': nearest_area,
            'temperature': float(current_condition['temp_C']),
            'humidity': int(current_condition['humidity']),
            'description': current_condition['weatherDesc'][0]['value']
        }
        return weather_info

    except requests.exceptions.RequestException:
        st.error("네트워크 오류가 발생했습니다. 인터넷 연결을 확인해주세요.")
        return None
    except (KeyError, IndexError):
        st.error(f"'{city_name}' 도시를 찾을 수 없거나, 날씨 정보를 가져올 수 없습니다. 영문 이름으로 다시 시도해보세요.")
        return None

# --- Streamlit 앱 UI (화면) 구성 ---
st.title("오늘의 날씨")

# --- 핵심 수정 1: 입력창의 상태를 관리할 session_state 키 초기화 ---
# 'last_city' 대신 입력창과 직접 연결된 'city_input' 키를 사용합니다.
if "city_input" not in st.session_state:
    st.session_state.city_input = "Seoul"

# --- 핵심 수정 2: 'value' 대신 'key' 파라미터 사용 ---
# 'key'를 사용하면 Streamlit이 이 위젯의 상태를 자동으로 관리해주므로
# 사용자가 입력한 내용이 사라지지 않고 그대로 유지됩니다.
st.text_input(
    "도시 이름을 입력하세요 (예: London, Tokyo, 제주)",
    key="city_input" # value=... 대신 key=... 를 사용
)

if st.button("날씨 조회하기"):
    # --- 핵심 수정 3: st.session_state.city_input 에서 직접 값을 읽어옴 ---
    # 이제 user_input 변수 없이, session_state에 저장된 최신 입력값을 사용합니다.
    user_input = st.session_state.city_input.strip()

    if user_input:
        with st.spinner(f"'{user_input}'의 최신 날씨를 확인하는 중..."):
            weather_data = get_live_weather(user_input)

        if weather_data:
            st.subheader(f"📍 {weather_data['city']}의 현재 날씨")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ 온도", f"{weather_data['temperature']:.1f} °C")
            col2.metric("💧 습도", f"{weather_data['humidity']} %")
            col3.metric("☀️ 날씨", weather_data['description'])
    else:
        st.warning("도시 이름을 입력해주세요.")