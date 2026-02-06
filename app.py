import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import io
import base64

# --- 1. 現代化 UI 設定 (Threads 風格) ---
st.set_page_config(page_title="Grok-4 EP Assistant", page_icon="🧠", layout="centered")

# CSS: 模擬現代 App 的黑白極簡風格 (Dark Mode)
st.markdown("""
    <style>
    /* 全局背景與字體 */
    .stApp {
        background-color: #101010;
        color: #F3F5F7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 標題區域 */
    .header-container {
        padding-top: 20px;
        padding-bottom: 20px;
        text-align: center;
        border-bottom: 1px solid #333;
    }
    .header-title {
        font-size: 24px;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        font-size: 14px;
        color: #777;
        margin-top: 5px;
    }

    /* 對話氣泡：使用者 (右側) */
    .user-bubble {
        background-color: #1D1D1D;
        color: #FFF;
        padding: 12px 16px;
        border-radius: 18px;
        border-top-right-radius: 4px;
        margin: 10px 0 10px auto;
        max-width: 85%;
        font-size: 15px;
        line-height: 1.5;
        border: 1px solid #333;
    }

    /* 對話氣泡：Grok (左側) */
    .grok-bubble {
        background-color: #000;
        color: #FFF;
        padding: 12px 16px;
        border-radius: 18px;
        border-top-left-radius: 4px;
        margin: 10px auto 10px 0;
        max-width: 85%;
        font-size: 15px;
        line-height: 1.5;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* 錄音按鈕區域微調 */
    .audio-container {
        display: flex;
        justify_content: center;
        margin-top: 20px;
        padding: 10px;
        background-color: #1A1A1A;
        border-radius: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 標題區 ---
st.markdown("""
    <div class="header-container">
        <div class="header-title">Grok-4 EP</div>
        <div class="header-subtitle">Educational Psychologist • Interactive • AI</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. 初始化 xAI Grok ---
# 只需在 Streamlit Secrets 設定 GROK_API_KEY，無需 OpenAI Key
if "GROK_API_KEY" in st.secrets:
    client = OpenAI(
        api_key=st.secrets["GROK_API_KEY"],
        base_url="https://api.x.ai/v1",
    )
else:
    st.error("請在 Advanced Settings 設定 GROK_API_KEY")
    st.stop()

# --- 4. 互動邏輯 ---
st.write("") # Spacer

# 使用者語音輸入 (免費元件)
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.caption("👇 點擊下方按鈕開始說話")
    # 這裡的 speech_to_text 使用瀏覽器內建功能 (Google Chrome 引擎)，完全免費
    text_input = speech_to_text(
        language='zh-HK',  # 設定為廣東話/繁體中文
        start_prompt="🎤 錄音 (Record)",
        stop_prompt="⏹️ 停止 (Stop)",
        just_once=True,
        key='STT'
    )

if text_input:
    # 1. 顯示使用者文字 (Threads 風格)
    st.markdown(f'<div class="user-bubble">{text_input}</div>', unsafe_allow_html=True)

    # 2. 呼叫 Grok-4
    with st.spinner("Grok-4 正在分析 (Reasoning)..."):
        try:
            response = client.chat.completions.create(
                model="grok-4", # <--- 使用最新的旗艦模型
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一位資深的教育心理學家 (Educational Psychologist)。你的對象是小學學生 (P1-P4)。請用溫暖、具備同理心的繁體中文回答。你的回答應該簡短、互動性強，並能引導學生思考。請避免過於深奧的術語，就像在 Instagram/Threads 上與學生輕鬆互動一樣。"
                    },
                    {"role": "user", "content": text_input}
                ]
                # 注意：Grok-4 是推理模型，通常不需要設定 reasoning_effort，它會自動處理
            )
            
            grok_reply = response.choices[0].message.content

            # 3. 顯示 Grok 回覆
            st.markdown(f'<div class="grok-bubble"><b>Grok-4：</b><br>{grok_reply}</div>', unsafe_allow_html=True)

            # 4. 語音合成 (TTS) - 使用 gTTS (免費 Google 服務，不需 API Key)
            tts = gTTS(text=grok_reply, lang='zh-tw')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            
            # 自動播放語音
            st.audio(audio_fp, format="audio/mp3", autoplay=True)

        except Exception as e:
            st.error(f"連線錯誤: {e}")

# --- 頁尾 ---
st.markdown("<div style='text-align: center; color: #444; margin-top: 50px; font-size: 12px;'>Powered by xAI Grok-4 • No OpenAI Key Required</div>", unsafe_allow_html=True)
