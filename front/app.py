import streamlit as st
import requests
import time
from html import escape

# 1. 페이지 기본 설정
st.set_page_config(page_title="심야의 바텐더", page_icon="🍸", layout="centered")

# 2. 커스텀 CSS 주입: UI/UX 디자인 시스템 반영
st.markdown("""
<style>
    /* 전체 다크 테마 톤 앤 매너 적용 */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    /* 선택지 버튼: 라디오 동작은 유지하되 화면에서는 pill 버튼처럼 표시 */
    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 12px;
    }

    div.row-widget.stRadio > div > label {
        --option-rgb: 0, 255, 204;
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px !important;
        min-height: 40px;
        padding: 9px 18px !important;
        border-radius: 100px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        background: rgba(255, 255, 255, 0.025) !important;
        color: #FAFAFA !important;
        font-weight: 800;
        line-height: 1.1;
        cursor: pointer;
        box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.04);
        transition: all 0.25s ease !important;
    }

    div.row-widget.stRadio > div > label:nth-child(1) { --option-rgb: 94, 198, 255; }
    div.row-widget.stRadio > div > label:nth-child(2) { --option-rgb: 176, 119, 255; }
    div.row-widget.stRadio > div > label:nth-child(3) { --option-rgb: 255, 132, 199; }
    div.row-widget.stRadio > div > label:nth-child(4) { --option-rgb: 133, 159, 255; }
    div.row-widget.stRadio > div > label:nth-child(5) { --option-rgb: 255, 99, 118; }
    div.row-widget.stRadio > div > label:nth-child(6) { --option-rgb: 109, 221, 164; }
    div.row-widget.stRadio > div > label:nth-child(7) { --option-rgb: 255, 174, 82; }

    div.row-widget.stRadio > div > label > div:first-child {
        display: none !important;
    }

    div.row-widget.stRadio > div > label::before {
        content: "";
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: rgb(var(--option-rgb));
        box-shadow: 0 0 12px rgba(var(--option-rgb), 0.72);
        flex: 0 0 auto;
    }

    div.row-widget.stRadio > div > label:hover {
        color: rgb(var(--option-rgb)) !important;
        border-color: rgba(var(--option-rgb), 0.95) !important;
        background:
            radial-gradient(circle at 18% 16%, rgba(var(--option-rgb), 0.26), transparent 36%),
            rgba(var(--option-rgb), 0.13) !important;
        box-shadow:
            0 0 18px rgba(var(--option-rgb), 0.46),
            inset 0 0 14px rgba(var(--option-rgb), 0.14) !important;
        transform: translateY(-2px);
    }

    div.row-widget.stRadio > div > label:has(input:checked),
    div.row-widget.stRadio > div > label:has([aria-checked="true"]) {
        color: #FAFAFA !important;
        border-color: rgba(var(--option-rgb), 1) !important;
        background:
            linear-gradient(135deg, rgba(var(--option-rgb), 0.72), rgba(var(--option-rgb), 0.28)),
            #151820 !important;
        box-shadow:
            0 0 22px rgba(var(--option-rgb), 0.48),
            inset 0 0 16px rgba(255, 255, 255, 0.1) !important;
    }

    /* 주문 버튼 */
    div[data-testid="stButton"] button {
        min-height: 40px;
        border-radius: 100px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        background: rgba(255, 255, 255, 0.025) !important;
        color: #FAFAFA !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.04) !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stButton"] button:hover {
        border-color: rgba(0, 255, 204, 0.95) !important;
        background:
            radial-gradient(circle at 18% 16%, rgba(0, 255, 204, 0.26), transparent 36%),
            rgba(0, 255, 204, 0.13) !important;
        color: #00FFCC !important;
        box-shadow:
            0 0 18px rgba(0, 255, 204, 0.46),
            inset 0 0 14px rgba(0, 255, 204, 0.14) !important;
        transform: translateY(-2px);
    }

    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stButton"] button[data-testid="baseButton-primary"] {
        border-color: rgba(0, 255, 204, 1) !important;
        background:
            linear-gradient(135deg, rgba(0, 255, 204, 0.72), rgba(0, 255, 204, 0.28)),
            #151820 !important;
        color: #FAFAFA !important;
        box-shadow:
            0 0 22px rgba(0, 255, 204, 0.48),
            inset 0 0 16px rgba(255, 255, 255, 0.1) !important;
    }

    div[data-testid="stSlider"] {
        padding-top: 0;
    }

    div[data-testid="stSlider"] [role="slider"] {
        background-color: #ff5269 !important;
        border-color: #ff5269 !important;
        box-shadow: 0 0 16px rgba(255, 82, 105, 0.55) !important;
    }

    div[data-testid="stSlider"] [data-baseweb="slider"] > div {
        transition: all 0.25s ease;
    }

    .abv-guide {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        margin-top: -6px;
        color: #D6D9E0;
        font-size: 0.94rem;
        font-weight: 700;
    }

    .abv-guide-percent {
        color: #FAFAFA;
        font-size: 1.05rem;
        font-weight: 900;
    }

    .abv-guide-label {
        color: #FF8393;
    }

    .result-page {
        padding-top: 8px;
    }

    .result-kicker {
        color: #00FFCC;
        font-size: 0.92rem;
        font-weight: 900;
        letter-spacing: 0;
        margin-bottom: 8px;
    }

    .drink-title {
        margin: 0;
        color: #FAFAFA;
        font-size: clamp(2.2rem, 7vw, 4.2rem);
        line-height: 1.02;
        font-weight: 950;
    }

    .drink-subcopy {
        margin-top: 18px;
        color: #C9CED8;
        font-size: 1.08rem;
        line-height: 1.7;
    }

    .result-hero {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(0, 255, 204, 0.28);
        border-radius: 18px;
        padding: 34px;
        background:
            radial-gradient(circle at 18% 20%, rgba(0, 255, 204, 0.22), transparent 34%),
            radial-gradient(circle at 86% 6%, rgba(255, 82, 105, 0.2), transparent 28%),
            linear-gradient(145deg, #1a1c23, #101217);
        box-shadow: 0 0 32px rgba(0, 255, 204, 0.12);
    }

    .result-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-top: 18px;
    }

    .result-panel {
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 12px;
        padding: 18px;
        background: rgba(255, 255, 255, 0.035);
    }

    .result-panel-label {
        color: #8D96A8;
        font-size: 0.8rem;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .result-panel-value {
        color: #FAFAFA;
        font-size: 0.98rem;
        font-weight: 800;
        line-height: 1.45;
    }

    .ingredient-list {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 12px;
    }

    .ingredient-chip {
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 100px;
        padding: 8px 13px;
        color: #F0F3F8;
        background: rgba(255, 255, 255, 0.045);
        font-weight: 750;
    }

    .note-block {
        margin-top: 18px;
        border-left: 3px solid #00FFCC;
        padding: 4px 0 4px 16px;
        color: #DFE4EC;
        font-size: 1.05rem;
        line-height: 1.75;
        font-style: italic;
    }

    @media (max-width: 760px) {
        .result-grid {
            grid-template-columns: 1fr;
        }

        .result-hero {
            padding: 24px;
        }
    }

</style>
""", unsafe_allow_html=True)


def render_option_buttons(state_key, options):
    return st.radio(
        state_key,
        options,
        index=None,
        horizontal=True,
        label_visibility="collapsed",
        key=state_key,
    )


def format_abv_label(abv_percent):
    if abv_percent <= 5:
        return "0~5% (오늘은 분위기만 내는)"
    if abv_percent <= 10:
        return "5~10% (기분 좋게 알딸딸)"
    if abv_percent <= 20:
        return "10~20% (좀 더 취해보자)"
    return "20% 이상 (오늘 밤 다 잊고 취할래)"


def render_result_page():
    result = st.session_state.get("recommendation_result")
    payload = st.session_state.get("recommendation_payload", {})

    if not result:
        st.session_state.current_view = "form"
        st.experimental_rerun()

    drink = escape(result.get("drink", "바텐더의 비밀 레시피"))
    comment = escape(result.get("comment", "오늘 밤에 어울리는 한 잔을 준비했습니다."))
    ingredients = [
        escape(item.strip())
        for item in result.get("ingredients", "").split(",")
        if item.strip()
    ]
    if ingredients:
        ingredient_html = "".join(
            f'<span class="ingredient-chip">{ingredient}</span>'
            for ingredient in ingredients
        )
    else:
        ingredient_html = '<span class="ingredient-chip">재료 정보 없음</span>'

    persona_label = escape(payload.get("persona", "-"))
    taste_label = escape(payload.get("taste", "-"))
    abv_label = escape(str(payload.get("abv", "-")))

    st.markdown(
        f"""
        <div class="result-page">
            <div class="result-kicker">MIDNIGHT BARTENDER'S PICK</div>
            <div class="result-hero">
                <h1 class="drink-title">{drink}</h1>
                <p class="drink-subcopy">
                    당신의 밤에 맞춰 고른 한 잔입니다. 아래 노트에서 오늘의 분위기, 맛, 도수를 한 번에 확인해보세요.
                </p>
                <div class="note-block">"{comment}"</div>
            </div>
            <div class="result-grid">
                <div class="result-panel">
                    <div class="result-panel-label">MOOD</div>
                    <div class="result-panel-value">{persona_label}</div>
                </div>
                <div class="result-panel">
                    <div class="result-panel-label">TASTE</div>
                    <div class="result-panel-value">{taste_label}</div>
                </div>
                <div class="result-panel">
                    <div class="result-panel-label">ABV</div>
                    <div class="result-panel-value">{abv_label}</div>
                </div>
            </div>
            <div class="result-panel" style="margin-top: 14px;">
                <div class="result-panel-label">TASTING NOTE</div>
                <div class="ingredient-list">{ingredient_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])
    with left:
        if st.button("조건 수정하기", use_container_width=True):
            st.session_state.current_view = "form"
            st.experimental_rerun()
    with right:
        if st.button("처음부터 고르기", use_container_width=True):
            for key in ["persona", "taste", "abv_percent", "recommendation_result", "recommendation_payload"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_view = "form"
            st.experimental_rerun()


if st.session_state.get("current_view") == "result":
    render_result_page()
    st.stop()


# 3. 헤더 영역
st.title("🍸 심야의 바텐더")
st.subheader("당신만을 위한 맞춤형 칵테일 & 목테일 처방전")
st.markdown("---")

# 4. 사용자 입력 폼 (Information Architecture 구조화)
st.markdown("### Q1. 오늘 밤, 당신의 추구미는 무엇인가요?")
persona_options = [
    "고독을 즐기는 늑대", "주목받고 싶은 파티광", "몽글몽글 감성 낭만파",
    "생각이 많은 사색가", "다 부수고 싶은 반항아", "침대와 물아일체 귀차니스트"
]
persona = render_option_buttons("persona", persona_options)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### Q2. 지금 당신이 원하는 맛은?")
taste_options = [
    "🍋 피로를 깨우는 짜릿한 상큼함", 
    "🍫 하루를 녹여버릴 짙은 달콤함", 
    "🥃 달지 않은 어른의 맛, 묵직한 드라이함",
    "🫧 꽉 막힌 속을 뚫어줄 시원한 청량감", 
    "🍯 부담 없이 입가에 맴도는 은은한 단맛", 
    "🌿 기분 전환에 딱 맞는 산뜻한 새콤함", 
    "🍷 은은하게 취기가 도는 기분 좋은 술맛"
]

taste = render_option_buttons("taste", taste_options)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### Q3. 알콜 농도는 어느 정도가 좋을까요?")
if "abv_percent" not in st.session_state:
    st.session_state.abv_percent = 8

abv_percent = st.slider(
    "도수",
    min_value=0,
    max_value=40,
    step=1,
    format="%d%%",
    label_visibility="collapsed",
    key="abv_percent",
)
abv = format_abv_label(abv_percent)
st.markdown(
    f"""
    <div class="abv-guide">
        <span class="abv-guide-percent">{abv_percent}%</span>
        <span class="abv-guide-label">{abv}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# 5. API 통신 및 결과 렌더링
if st.button("바텐더에게 주문하기 🛎️", use_container_width=True):
    if not persona or not taste:
        st.warning("추구미와 맛을 하나씩 선택해주세요.")
        st.stop()

    # 감성적인 로딩 애니메이션
    with st.spinner("바텐더가 얼음을 조각하고 쉐이커를 흔드는 중... 🧊"):
        time.sleep(1.5) 
        
        payload = {
            "persona": persona,
            "taste": taste,
            "abv": abv_percent  
        }
        
        try:
            # 도커 환경과 로컬 환경(localhost) 통신을 모두 지원하는 Fallback 로직
            try:
                # Docker Compose 내부 네트워크 통신 시도
                response = requests.post("http://back:8000/recommend", json=payload, timeout=3)
            except requests.exceptions.ConnectionError:
                # Docker가 아닐 경우 로컬호스트 통신 시도
                response = requests.post("http://localhost:8000/recommend", json=payload, timeout=3)
                
            if response.status_code == 200:
                result = response.json()
                st.session_state.recommendation_result = result
                st.session_state.recommendation_payload = payload
                st.session_state.current_view = "result"
                st.experimental_rerun()
            else:
                st.error("바텐더가 레시피를 찾는 데 실패했습니다. HTTP 상태 코드: " + str(response.status_code))
                
        except requests.exceptions.RequestException as e:
            st.error("백엔드 서버(FastAPI)와 연결할 수 없습니다. 서버 실행 상태를 확인해주세요.")
