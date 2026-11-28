from google import genai
from google.genai import types

def get_reply(user_text, p, survey, instant_chat, groq_key, api_key, messages):
    q = user_text.lower()
    topic = survey.get("topic", "Science & Tech")
    vibe = survey.get("vibe", "Funny")

    def fallback():
        if "roast" in q:
            return f"Honestly, {p.health_score}% vitality? You survived on pure {topic} and zero sleep! Still better discipline than {p.discipline_stat}% of the hall."
        if "hack" in q or "study" in q or "tip" in q:
            return f"Beating {p.study_stat}% of students in academics! Apply your {topic} focus in 25-minute sprints—and follow my tip: {p.health_tip}"
        if "future" in q or "predict" in q:
            return f"A '{p.initial_vibe}' obsessed with {topic}? I see you leading a major project by 2030—once you fix that {p.health_score}% energy bar!"
        return f"Haha classic {vibe} answer! Recalibrating my circuits to match your {topic} energy."

    if instant_chat:
        return fallback()

    sys_inst = f"You are Persona AI, a witty AI Twin created by Shubham Joshi at Shri Vaishnav Academy, Indore. Initial scan: '{p.initial_vibe}', {p.health_score}% vitality. Survey: {survey}. Reply in MAX 2 short sentences."

    if groq_key.strip():
        from groq import Groq
        g = Groq(api_key=groq_key.strip(), timeout=10.0)
        for g_model in ["llama-3.3-70b-versatile", "openai/gpt-oss-20b", "qwen/qwen3-32b"]:
            try:
                res = g.chat.completions.create(
                    model=g_model,
                    messages=[{"role": "system", "content": sys_inst}] + messages,
                    max_tokens=90,
                    temperature=0.8,
                )
                return next(iter(res.choices)).message.content

            except Exception:
                continue

    if api_key.strip():
        try:
            c = genai.Client(api_key=api_key.strip())
            hist = [types.Content(role="user" if m["role"] == "user" else "model", parts=[types.Part.from_text(text=m["content"])]) for m in messages]
            res = c.models.generate_content(
                model="gemini-3.8-flash-lite",
                contents=hist,
                config=types.GenerateContentConfig(system_instruction=sys_inst, temperature=0.8),
            )
            return res.text
        except Exception:
            pass

    return fallback()
