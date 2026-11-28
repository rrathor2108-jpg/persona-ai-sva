import base64
import io
import json
import time
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel

class VisitorProfile(BaseModel):
    age_range: str = "18-24"
    gender: str = "Visitor"
    study_stat: int = 88
    discipline_stat: int = 85
    health_score: int = 89
    health_tip: str = "Stay hydrated and take a 10-minute breather today!"
    facial_notes: str = "Composed expression, attentive focus"
    initial_vibe: str = "Curious Explorer"

def run_vision_scan(gemini_key, small_img, prompt, groq_key):
    start_t = time.time()
    errs = []
    detailed_prompt = (
        prompt
        + " Carefully inspect the person's real facial features, eye contact, glasses, smile or tiredness, posture, and attire in the photo to generate an accurate, personalized first-impression profile. "
        + 'Return ONLY valid JSON with exact keys: {"age_range":"16-18","gender":"Male","study_stat":88,"discipline_stat":85,"health_score":90,"health_tip":"...","facial_notes":"...","initial_vibe":"..."}'
    )

    # 1. GEMINI 3.8 FLASH FIRST (Capped at 15s)
    if gemini_key.strip():
        try:
            client = genai.Client(
                api_key=gemini_key.strip(),
                http_options=types.HttpOptions(
                    timeout=15000,
                    retry_options=types.HttpRetryOptions(attempts=1)
                )
            )
            res = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=[small_img, detailed_prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=VisitorProfile,
                    temperature=0.6,
                )
            )
            return VisitorProfile.model_validate_json(res.text)
        except Exception as e:
            errs.append(f"Gemini: {str(e)[:60]}")

    # 2. GROQ LLAMA-4 MAVERICK BACKUP (Uses remaining time up to 28.5s max)
    remaining = 28.5 - (time.time() - start_t)
    if groq_key.strip() and remaining > 2.0:
        try:
            from groq import Groq
            buf = io.BytesIO()
            small_img.convert("RGB").save(buf, format="JPEG", quality=88)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            g = Groq(api_key=groq_key.strip(), timeout=remaining, max_retries=0)
            gr = g.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": detailed_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}],
                response_format={"type": "json_object"},
                temperature=0.6,
            )
            data = json.loads(gr.choices[0].message.content)
            return VisitorProfile(**data)
        except Exception as e:
            errs.append(f"Groq: {str(e)[:60]}")

    if errs:
        st.toast(" | ".join(errs))

    return VisitorProfile()
