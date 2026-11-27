import base64
import io
import wave
import numpy as np
import streamlit as st

@st.cache_resource
def get_scan_gallery():
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
    st.subheader("Recent Visitor Scans — Shri Vaishnav Academy")
    if not gallery:
        st.info("No scans saved yet! Run a scan in the first tab and it will appear here.")
        return
    cols = st.columns(3)
    for idx, item in enumerate(gallery):
        with cols[idx % 3]:
            with st.container(border=True):
                if item["thumb"]:
                    st.image(f"data:image/jpeg;base64,{item['thumb']}", width=110)
                st.markdown(f"**{item['vibe']}** (`{item['id']}`)")
                st.caption(f"Est. Age: {item['age']} | Academic: Top {100 - item['study']}% | Vitality: {item['health']}%")
                st.write(f"Visitor Verdict: **{item['accuracy']}**")

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
