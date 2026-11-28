import random
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from styles import CSS_STYLES, get_front_banner_html, build_card_html
from chat_logic import get_reply
from vision_scan import VisitorProfile, run_vision_scan
from gallery import get_scan_gallery, save_scan_to_gallery, render_gallery_tab, analyze_voice

st.set_page_config(page_title="Persona AI - By Shubham Joshi | Shri Vaishnav Academy", layout="wide")
st.markdown(CSS_STYLES, unsafe_allow_html=True)
components.html('<script>const d=window.parent.document;if(!d.sb){d.sb=1;d.addEventListener("keydown",e=>{if(e.code==="Space"&&!["INPUT","TEXTAREA"].includes(d.activeElement.tagName)){const b=d.querySelector(\'[data-testid="stCameraInput"] button\');if(b&&!b.disabled){e.preventDefault();b.click();}}});}</script>', height=0, width=0)

SECRET_GEMINI = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
SECRET_GROQ = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""

for k, v in {
    "step": "scan", "profile": None, "visitor_photo": None,
    "voice_summary": "BALANCED", "visitor_id": f"SVA-{random.randint(1000, 9999)}",
    "messages": [], "survey_data": {}, "last_spoken": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_visitor():
    st.session_state.step = "scan"
    st.session_state.profile = None
    st.session_state.visitor_photo = None
    st.session_state.voice_summary = "BALANCED"
    st.session_state.visitor_id = f"SVA-{random.randint(1000, 9999)}"
    st.session_state.messages = []
    st.session_state.survey_data = {}
    st.session_state.last_spoken = ""

def speak_tts(text):
    if not text or text == st.session_state.last_spoken:
        return
    st.session_state.last_spoken = text
    clean = text.replace('"', '\\"').replace("\n", " ")
    components.html(f'<script>window.parent.speechSynthesis.cancel();const m=new SpeechSynthesisUtterance("{clean}");m.rate=1.15;window.parent.speechSynthesis.speak(m);</script>', height=0, width=0)

ADMIN_PIN = st.secrets.get("ADMIN_PIN", "2026") if hasattr(st, "secrets") else "2026"

with st.sidebar:
    st.header("Persona AI")
    tts_enabled = st.toggle("Voice Output (TTS)", value=True)
    st.divider()
    entered_pin = st.text_input("Admin PIN (Shubham Only)", type="password")
    is_admin = (entered_pin == ADMIN_PIN)

    if is_admin:
        st.success("Admin Unlocked")
        mock_scan = st.toggle("Demo Mode (No API Used)", value=False)
        instant_chat = st.toggle("Offline Instant Chat", value=False)
        api_key = st.text_input("Override Gemini Key", value=SECRET_GEMINI, type="password")
        groq_key = st.text_input("Override Groq Key", value=SECRET_GROQ, type="password")
        if st.button("Clear Scans Wall", use_container_width=True):
            get_scan_gallery().clear()
            st.rerun()
    else:
        mock_scan = False
        instant_chat = False
        api_key = SECRET_GEMINI
        groq_key = SECRET_GROQ

top_l, top_r = st.columns([4.2, 1])
with top_l:
    st.markdown(get_front_banner_html(), unsafe_allow_html=True)
with top_r:
    st.write("")
    st.write("")
    if st.button("Reset for Next Visitor", type="primary", use_container_width=True):
        reset_visitor()
        st.rerun()

tab_scan, tab_gallery = st.tabs(["AI Persona Scanner", f"Previous Scans Wall ({len(get_scan_gallery())})"])

with tab_scan:
    if st.session_state.step == "scan":
        col1, col2 = st.columns([2.2, 1], gap="large")
        with col1:
            cam_mode = st.radio("Select Image Source:", ["Live Camera Feed", "Local Photo Upload"], horizontal=True)
            if cam_mode == "Live Camera Feed":
                img_buffer = st.camera_input("Align your face and click Take Photo")
            else:
                img_buffer = st.file_uploader("Upload a selfie or portrait photo", type=["jpg", "jpeg", "png", "webp"])
                if img_buffer:
                    st.image(img_buffer, width=320, caption="Uploaded Photo Ready")
        with col2:
            st.markdown("**Optional Voice Check (2 sec)**")
            audio_buffer = st.audio_input("Say 'Hello!'")
            components.html("""
<div style="margin-bottom:8px;">
  <button id="recBtn" style="width:100%;padding:10px;background:#111827;color:#fff;font-weight:700;border:none;border-radius:8px;cursor:pointer;font-family:sans-serif;">
    🎙️ Start / Stop Voice (or Press R)
  </button>
</div>
<script>
const d = window.parent.document;
function toggleMic() {
  const micBtn = d.querySelector('[data-testid="stAudioInput"] button');
  if (micBtn && !micBtn.disabled) micBtn.click();
}
document.getElementById("recBtn").onclick = toggleMic;
if (!d.recKeyBound) {
  d.recKeyBound = true;
  d.addEventListener("keydown", function(e) {
    if (e.code === "KeyR" && !["INPUT", "TEXTAREA"].includes(d.activeElement.tagName)) {
      e.preventDefault();
      toggleMic();
    }
  });
}
</script>
""", height=52)

            st.info("Switch between **Live Camera Feed** and **Local Photo Upload** anytime above.")
            if st.button("Analyze & Generate Pass", type="primary", use_container_width=True):
                if not img_buffer and not mock_scan:
                    st.warning("Please take a photo or upload an image first!")
                else:
                    raw_img = Image.open(img_buffer) if img_buffer else None
                    small_img = raw_img.copy() if raw_img else None
                    if small_img:
                        small_img.thumbnail((320, 320))
                    tag, v_detail = analyze_voice(audio_buffer.getvalue()) if audio_buffer else ("VISUAL SCAN", "Visual cues only.")
                    st.session_state.visitor_photo = raw_img
                    st.session_state.voice_summary = tag
                    with st.spinner("Analyzing facial & vocal cues..."):
                        if mock_scan:
                            st.session_state.profile = VisitorProfile()
                        else:
                            if not api_key.strip() and not groq_key.strip():
                                st.error("Add your Gemini or Groq API key in the sidebar!")
                                st.stop()
                            prompt = f"Exhibition demo at Shri Vaishnav Academy, Indore. Voice: {v_detail}. Return JSON: age_range, gender, study_stat (70-98), discipline_stat (70-98), health_score (75-98), 1-sentence health_tip, short facial_notes, 2-word initial_vibe."
                            st.session_state.profile = run_vision_scan(api_key, small_img, prompt, groq_key)
                    save_scan_to_gallery(st.session_state.profile, st.session_state.visitor_id, raw_img)
                    st.session_state.step = "survey"
                    st.rerun()

    elif st.session_state.step in ["survey", "chat"]:
        p = st.session_state.profile
        left_col, right_col = st.columns([1.2, 1], gap="large")
        with left_col:
            st.markdown(build_card_html(p, st.session_state.visitor_id, st.session_state.voice_summary, st.session_state.visitor_photo), unsafe_allow_html=True)
        with right_col:
            if st.session_state.step == "survey":
                if tts_enabled:
                    speak_tts(f"Scan complete. Vitality {p.health_score} percent. {p.health_tip}")
                with st.container(border=True):
                    st.subheader("Step 2: Calibrate Your AI Twin")
                    with st.form("calibration_form"):
                        acc = st.radio("Was the AI's guess right?", ["Spot on!", "Close!", "Way off!"], horizontal=True)
                        topic = st.selectbox("Favorite Topic", ["Science & Tech", "Sports & Fitness", "Business & Finance", "Arts & Movies"])
                        vibe = st.radio("AI Twin Tone", ["Funny", "Encouraging", "Chill"], horizontal=True)
                        if st.form_submit_button("Activate AI Twin", type="primary", use_container_width=True):
                            st.session_state.survey_data = {"acc": acc, "topic": topic, "vibe": vibe}
                            save_scan_to_gallery(p, st.session_state.visitor_id, st.session_state.visitor_photo, accuracy=acc)
                            st.session_state.messages = [{"role": "assistant", "content": f"Persona AI calibrated! You rated my guess '{acc}' and love {topic}. Ask me anything!"}]
                            st.session_state.step = "chat"
                            st.rerun()
            elif st.session_state.step == "chat":
                with st.container(border=True):
                    st.subheader("Persona AI — Live Twin HUD")
                    with st.container(height=270):
                        for m in st.session_state.messages:
                            with st.chat_message(m["role"]):
                                st.write(m["content"])
                    if tts_enabled and st.session_state.messages[-1]["role"] == "assistant":
                        speak_tts(st.session_state.messages[-1]["content"])
                    c1, c2, c3 = st.columns(3)
                    clicked = None
                    if c1.button("Roast my scan", use_container_width=True):
                        clicked = "Roast my scan!"
                    if c2.button("Study hack", use_container_width=True):
                        clicked = "Give me a study hack"
                    if c3.button("Predict future", use_container_width=True):
                        clicked = "Predict my future"
                    final_in = clicked or st.chat_input("Or type a question...")
                    if final_in:
                        st.session_state.messages.append({"role": "user", "content": final_in})
                        reply = get_reply(final_in, p, st.session_state.survey_data, instant_chat, groq_key, api_key, st.session_state.messages)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.rerun()

with tab_gallery:
    render_gallery_tab()
