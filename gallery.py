import base64
import io
import os
import wave
import numpy as np
import streamlit as st

@st.cache_resource
def get_scan_gallery():
    return []

@st.cache_resource
def get_feedback_list():
    return []

def save_scan_to_gallery(p, vid, photo_img, accuracy="Unrated"):
    gallery = get_scan_gallery()
    thumb_b64 = ""
    if photo_img is not None:
        t = photo_img.copy()
        t.thumbnail((140, 140))
        buf = io.BytesIO()
        t.convert("RGB").save(buf, format="JPEG", quality=75)
        thumb_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    entry = {
        "id": vid, "vibe": p.initial_vibe, "age": p.age_range,
        "study": p.study_stat, "health": p.health_score,
        "accuracy": accuracy, "thumb": thumb_b64
    }
    for i, item in enumerate(gallery):
        if item["id"] == vid:
            gallery[i] = entry
            return
    gallery.insert(0, entry)
    if len(gallery) > 20:
        gallery.pop()

def render_gallery_tab():
    gallery = get_scan_gallery()
    feedbacks = get_feedback_list()

    col_wall, col_fb = st.columns([1.4, 1], gap="large")

    # LEFT: PREVIOUS SCANS WALL
    with col_wall:
        st.subheader("Recent Visitor Scans")
        if not gallery:
            st.info("No scans yet! Run a scan in the first tab to see it here.")
        else:
            cols = st.columns(2)
            for idx, item in enumerate(gallery):
                with cols[idx % 2]:
                    with st.container(border=True):
                        if item["thumb"]:
                            st.image(f"data:image/jpeg;base64,{item['thumb']}", width=95)
                        st.markdown(f"**{item['vibe']}** (`{item['id']}`)")
                        st.caption(f"Age: {item['age']} | Vitality: {item['health']}%")
                        st.write(f"Verdict: **{item['accuracy']}**")

    # RIGHT: MINI FEEDBACK FOR SHUBHAM + OFFICIAL SCHOOL QR SLOT
    with col_fb:
        with st.container(border=True):
            st.subheader("Rate Persona AI (For Shubham)")
            with st.form("mini_feedback_form", clear_on_submit=True):
                visitor_name = st.text_input("Your Name (Optional)", placeholder="e.g., Aarav / Parent")
                stars = st.select_slider(
                    "How cool was the AI Twin?",
                    options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
                    value="⭐⭐⭐⭐⭐"
                )
                comment = st.text_input("Quick Review", placeholder="Loved the roast & voice!")
                if st.form_submit_button("Submit Feedback", type="primary", use_container_width=True):
                    feedbacks.insert(0, {
                        "name": visitor_name.strip() or "Exhibition Guest",
                        "stars": stars,
                        "comment": comment.strip() or "Awesome project!"
                    })
                    st.success("Thanks for rating Shubham's Persona AI!")

        # OFFICIAL SCHOOL QR DISPLAY (AUTO-APPEARS WHEN YOU UPLOAD school_feedback_qr.png)
        for qr_fn in ["school_feedback_qr.png", "school_feedback_qr.jpg", "school_feedback_qr.jpeg"]:
            if os.path.exists(qr_fn):
                with st.container(border=True):
                    st.markdown("**Official Shri Vaishnav Academy Feedback QR**")
                    st.image(qr_fn, width=180, caption="Scan for School Exhibition Feedback")
                break

        if feedbacks:
            st.markdown("**Recent Visitor Reviews:**")
            for fb in feedbacks[:6]:
                st.caption(f"{fb['stars']} **{fb['name']}**: {fb['comment']}")

def analyze_voice(audio_bytes):
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(samples**2)))
        zcr = float(np.mean(np.abs(np.diff(np.sign(samples)))))
        p_lbl = "HIGH" if zcr > 0.14 else ("DEEP" if zcr < 0.06 else "BALANCED")
        e_lbl = "ENERGETIC" if rms > 0.03 else "CALM"
        return f"{p_lbl} & {e_lbl}", f"Tone: {p_lbl}, Energy: {e_lbl}"
    except Exception:
        return "BALANCED", "Standard vocal cadence."
