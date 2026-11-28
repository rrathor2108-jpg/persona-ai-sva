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

    # 1. GEMINI AUTO-DISCOVER FLASH MODEL (Capped at 16s)
    if gemini_key.strip():
        try:
            client = genai.Client(
                api_key=gemini_key.strip(),
                http_options=types.HttpOptions(
                    timeout=16000,
                    retry_options=types.HttpRetryOptions(attempts=1)
                )
            )
            g_models = []
            for m in client.models.list():
                name = m.name.replace("models/", "")
                if "flash" in name and "tts" not in name and "image" not in name and "audio" not in name:
                    g_models.append(name)
            g_models.sort(key=lambda x: (0 if "lite" in x else 1, x), reverse=True)
            chosen_gemini = next(iter(g_models), "gemini-2.5-flash")

            res = client.models.generate_content(
                model=chosen_gemini,
                contents=[small_img, detailed_prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=VisitorProfile,
                    temperature=0.6,
                )
            )
            return VisitorProfile.model_validate_json(res.text)
        except Exception as e:
            errs.append(f"Gemini: {str(e)[:65]}")

    # 2. GROQ AUTO-DISCOVER VISION MODEL (Uses remaining time up to 28.5s)
    remaining = 28.5 - (time.time() - start_t)
    if groq_key.strip() and remaining > 2.5:
        try:
            from groq import Groq
            buf = io.BytesIO()
            small_img.convert("RGB").save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            g = Groq(api_key=groq_key.strip(), timeout=remaining, max_retries=0)

            all_ids = [m.id for m in g.models.list().data]
            v_list = [m for m in all_ids if any(k in m.lower() for k in ["scout", "maverick", "vision", "pixtral", "vl"])]
            if not v_list:
                raise RuntimeError("No vision model active on Groq")

            gr = g.chat.completions.create(
                model=next(iter(v_list)),
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": detailed_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}],
                response_format={"type": "json_object"},
                temperature=0.6,
            )
            first_choice = next(iter(gr.choices))
            data = json.loads(first_choice.message.content)
            return VisitorProfile(**data)
        except Exception as e:
            errs.append(f"Groq: {str(e)[:65]}")

    if errs:
        st.toast(" | ".join(errs))

    return VisitorProfile()
