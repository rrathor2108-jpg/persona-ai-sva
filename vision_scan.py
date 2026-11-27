import base64
import io
import json
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
    errors = []

    if gemini_key.strip():
        client = genai.Client(api_key=gemini_key.strip())
        for m in ["gemini-2.5-flash", "gemini-3.8-flash-lite", "gemini-3.8-flash"]:
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
                errors.append(f"Gemini({m}): {str(e)[:60]}")
                continue

    if groq_key.strip():
        try:
            from groq import Groq
            buf = io.BytesIO()
            small_img.convert("RGB").save(buf, format="JPEG", quality=75)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            g = Groq(api_key=groq_key.strip())
            jp = prompt + ' Return ONLY JSON with keys: {"age_range":"18-22","gender":"Male","study_stat":88,"discipline_stat":85,"health_score":90,"health_tip":"...","facial_notes":"...","initial_vibe":"..."}'
            gr = g.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": jp},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            data = json.loads(gr.choices.message.content)
            return VisitorProfile(**data)
        except Exception as e:
            errors.append(f"Groq: {str(e)[:60]}")

    if errors:
        st.warning("AI Scan Note: " + " | ".join(errors))

    return VisitorProfile()
