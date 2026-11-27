import base64
import io
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel

class VisitorProfile(BaseModel):
    age_range: str
    gender: str
    study_stat: int
    discipline_stat: int
    health_score: int
    health_tip: str
    facial_notes: str
    initial_vibe: str

def run_vision_scan(gemini_key, small_img, prompt, groq_key):
    err_log = []
    if gemini_key.strip():
        client = genai.Client(api_key=gemini_key.strip())
        for m in ["gemini-3.8-flash", "gemini-3.8-flash-lite"]:
            try:
                res = client.models.generate_content(
                    model=m,
                    contents=[small_img, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=VisitorProfile,
                        temperature=0.7,
                    )
                )
                return VisitorProfile.model_validate_json(res.text)
            except Exception as e:
                err_log.append(f"Gemini({m}): {str(e)[:50]}")
                continue

    if groq_key.strip():
        from groq import Groq
        buf = io.BytesIO()
        small_img.convert("RGB").save(buf, format="JPEG", quality=75)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        g = Groq(api_key=groq_key.strip())
        jp = prompt + ' Respond ONLY with valid JSON using exact keys: {"age_range": "18-22", "gender": "Male", "study_stat": 88, "discipline_stat": 85, "health_score": 90, "health_tip": "...", "facial_notes": "...", "initial_vibe": "..."}'
        for gm in ["meta-llama/llama-4-scout-17b-16e-instruct", "meta-llama/llama-4-maverick-17b-128e-instruct"]:
            try:
                gr = g.chat.completions.create(
                    model=gm,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": jp},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                )
                return VisitorProfile.model_validate_json(gr.choices.message.content)
            except Exception as e:
                err_log.append(f"Groq({gm}): {str(e)[:50]}")
                continue

    if err_log:
        st.toast(" | ".join(err_log))

    return VisitorProfile(
        age_range="16-40", gender="Visitor", study_stat=91, discipline_stat=94,
        health_score=89, health_tip="Stay hydrated and take a 10-minute breather today!",
        facial_notes="Composed expression, attentive focus", initial_vibe="Curious Explorer"
    )
