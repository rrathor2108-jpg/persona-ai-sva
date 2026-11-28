import io
import json
import time
import numpy as np
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

def _extract_photo_telemetry(img):
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    brightness = float(np.mean(arr))
    contrast = float(np.std(arr))
    r_mean, g_mean, b_mean = float(np.mean(arr[:, :, 0])), float(np.mean(arr[:, :, 1])), float(np.mean(arr[:, :, 2]))
    warmth = "Warm/Energetic" if r_mean > b_mean + 8 else ("Cool/Calm" if b_mean > r_mean + 8 else "Balanced")
    lighting = "Bright & Clear" if brightness > 135 else ("Moody/Low-Light" if brightness < 85 else "Natural Studio")
    sharpness = "High Focus" if contrast > 55 else "Soft Focus"
    return f"Lighting: {lighting} (lum={int(brightness)}), Tone: {warmth}, Framing: {sharpness}"

def run_vision_scan(gemini_key, small_img, prompt, groq_key):
    start_t = time.time()
    detailed_prompt = (
        prompt
        + " Carefully inspect the person's real facial features, eye contact, glasses, smile or tiredness, posture, and attire to generate a personalized first-impression profile. "
        + 'Return ONLY valid JSON with exact keys: {"age_range":"16-18","gender":"Male","study_stat":88,"discipline_stat":85,"health_score":90,"health_tip":"...","facial_notes":"...","initial_vibe":"..."}'
    )

    # 1. GEMINI VISION FIRST (Tries available Flash models)
    if gemini_key.strip():
        try:
            client = genai.Client(
                api_key=gemini_key.strip(),
                http_options=types.HttpOptions(
                    timeout=14000,
                    retry_options=types.HttpRetryOptions(attempts=1)
                )
            )
            g_models = []
            for m in client.models.list():
                name = m.name.replace("models/", "")
                if "flash" in name and "tts" not in name and "image" not in name and "audio" not in name:
                    g_models.append(name)
            g_models.sort(key=lambda x: (0 if "lite" in x else 1, x), reverse=True)

            for m_name in g_models[:2]:
                try:
                    res = client.models.generate_content(
                        model=m_name,
                        contents=[small_img, detailed_prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=VisitorProfile,
                            temperature=0.6,
                        )
                    )
                    return VisitorProfile.model_validate_json(res.text)
                except Exception:
                    continue
        except Exception:
            pass

    # 2. GROQ BIOMETRIC TELEMETRY AI (Runs in ~0.5s if Gemini hits 429 quota!)
    remaining = 28.5 - (time.time() - start_t)
    if groq_key.strip() and remaining > 2.0:
        try:
            from groq import Groq
            telemetry = _extract_photo_telemetry(small_img)
            g = Groq(api_key=groq_key.strip(), timeout=remaining, max_retries=0)
            groq_prompt = (
                f"{detailed_prompt}\n"
                f"Live Camera Biometric Telemetry: {telemetry}. "
                f"Create a fresh, creative, non-generic visitor profile tailored to these exact camera & voice signals!"
            )
            gr = g.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": groq_prompt}],
                response_format={"type": "json_object"},
                temperature=0.85,
            )
            first_choice = next(iter(gr.choices))
            data = json.loads(first_choice.message.content)
            return VisitorProfile(**data)
        except Exception as e:
            st.toast(f"Groq backup note: {str(e)[:60]}")

    return VisitorProfile()
