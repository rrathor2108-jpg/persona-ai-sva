import base64
import io
import os

CSS_STYLES = """
<style>
[data-testid="stCameraInput"] { width: 100% !important; }
[data-testid="stCameraInput"] video, [data-testid="stCameraInput"] img {
    width: 100% !important; max-height: 68vh !important;
    object-fit: cover; border-radius: 12px; border: 2px solid #111827;
}
.bio-card {
    background: #ffffff; color: #111827; border: 2px solid #111827;
    border-radius: 12px; padding: 22px; box-shadow: 6px 6px 0px #111827;
    font-family: 'Inter', -apple-system, sans-serif;
}
.bio-top {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 2px solid #111827; padding-bottom: 12px; margin-bottom: 14px; gap: 12px;
}
.school-brand { display: flex; align-items: center; gap: 12px; }
.bio-title { font-weight: 800; font-size: 16px; letter-spacing: 0.5px; text-transform: uppercase; color: #111827; line-height: 1.2; }
.bio-subtitle { font-family: 'Courier New', monospace; font-size: 11px; color: #4b5563; }
.bio-tag { background: #111827; color: #ffffff; font-family: 'Courier New', monospace; font-size: 12px; padding: 5px 10px; border-radius: 4px; font-weight: bold; white-space: nowrap; }
.assumption-banner { background: #f3f4f6; border: 1px dashed #6b7280; color: #374151; font-family: 'Courier New', monospace; font-size: 11px; font-weight: 700; text-align: center; padding: 6px 10px; border-radius: 6px; margin-bottom: 16px; }
.bio-body { display: flex; gap: 20px; align-items: flex-start; }
.bio-photo {
    width: 145px; height: 165px; object-fit: cover; border: 2px solid #111827;
    border-radius: 8px; background: #f3f4f6; display: flex; flex-direction: column;
    align-items: center; justify-content: center; font-family: 'Courier New', monospace;
    font-size: 12px; color: #4b5563; text-align: center; flex-shrink: 0;
}
.bio-name { font-size: 21px; font-weight: 800; color: #111827; margin: 0 0 8px 0; line-height: 1.2; }
.bio-specs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; font-family: 'Courier New', monospace; font-size: 12px; }
.spec-box { border: 1px solid #d1d5db; background: #f9fafb; padding: 4px 8px; border-radius: 4px; }
.metric-item { margin-bottom: 11px; }
.metric-head { display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; margin-bottom: 4px; }
.metric-track { width: 100%; height: 11px; background: #e5e7eb; border: 1px solid #111827; border-radius: 3px; overflow: hidden; }
.metric-fill { height: 100%; background: #111827; }
.metric-fill-health { height: 100%; background: #16a34a; }
.bio-alert { margin-top: 14px; background: #fefce8; border: 1.5px solid #ca8a04; border-radius: 6px; padding: 10px 14px; font-size: 13px; color: #854d0e; }
.bio-footer { margin-top: 12px; padding-top: 10px; border-top: 1px solid #e5e7eb; display: flex; justify-content: space-between; font-family: 'Courier New', monospace; font-size: 11px; color: #6b7280; }
</style>
"""

def _get_logo(size=54):
    for fn in ["school_logo.png", "school_logo.jpg", "school_logo.jpeg"]:
        if os.path.exists(fn):
            with open(fn, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            ext = "png" if fn.endswith("png") else "jpeg"
            return f'<img src="data:image/{ext};base64,{b64}" style="width:{size}px;height:{size}px;object-fit:contain;border-radius:12px;border:2px solid #111827;background:#fff;padding:4px;flex-shrink:0;" />'
    return f'<div style="width:{size}px;height:{size}px;background:#111827;color:#fff;font-weight:900;font-size:{int(size*0.32)}px;display:flex;align-items:center;justify-content:center;border-radius:12px;flex-shrink:0;">SVA</div>'

def get_front_banner_html():
    logo = _get_logo(96)
    return f"""
    <div style="display:flex;align-items:center;gap:22px;padding:18px 24px;background:#ffffff;border:2.5px solid #111827;border-radius:14px;box-shadow:6px 6px 0px #111827;margin-bottom:18px;">
        {logo}
        <div>
            <div style="font-size:17px;font-weight:900;letter-spacing:1.2px;text-transform:uppercase;color:#111827;margin-bottom:4px;">
                SHRI VAISHNAV ACADEMY, INDORE
            </div>
            <div style="font-size:40px;font-weight:900;color:#111827;line-height:1.05;letter-spacing:-0.5px;">
                Persona AI
                <span style="font-size:16px;font-weight:800;background:#111827;color:#ffffff;padding:5px 14px;border-radius:8px;vertical-align:middle;margin-left:10px;letter-spacing:0.3px;">By Shubham Joshi</span>
            </div>
            <div style="font-family:'Courier New',monospace;font-size:13px;font-weight:700;color:#4b5563;margin-top:6px;">
                MULTIMODAL FIRST-IMPRESSION &amp; HUMAN-CALIBRATED AI TWIN LAB
            </div>
        </div>
    </div>
    """

def build_card_html(p, visitor_id, voice_summary, boxed_photo):
    logo_html = _get_logo(52)
    photo_html = '<div class="bio-photo"><span>[CAM_CAPTURE]</span><span style="font-size:10px;margin-top:4px;">NO PHOTO</span></div>'
    if boxed_photo is not None:
        buf = io.BytesIO()
        boxed_photo.convert("RGB").save(buf, format="JPEG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        photo_html = f'<img src="data:image/jpeg;base64,{img_b64}" class="bio-photo" />'

    return f"""
    <div class="bio-card">
        <div class="bio-top">
            <div class="school-brand">
                {logo_html}
                <div>
                    <div class="bio-title">SHRI VAISHNAV ACADEMY</div>
                    <div class="bio-subtitle">AI BEHAVIORAL &amp; VISION EXHIBITION</div>
                </div>
            </div>
            <span class="bio-tag">{visitor_id}</span>
        </div>
        <div class="assumption-banner">NOTICE: INITIAL AI ASSUMPTION ONLY &mdash; AWAITING HUMAN CALIBRATION</div>
        <div class="bio-body">
            {photo_html}
            <div style="flex:1;">
                <div class="bio-name">{p.initial_vibe}</div>
                <div class="bio-specs">
                    <span class="spec-box">AGE: <b>{p.age_range}</b></span>
                    <span class="spec-box">GENDER: <b>{p.gender.upper()}</b></span>
                    <span class="spec-box">VOICE: <b>{voice_summary}</b></span>
                </div>
                <div class="metric-item">
                    <div class="metric-head"><span>OVERALL ACADEMIC</span><span>BETTER THAN {p.study_stat}%</span></div>
                    <div class="metric-track"><div class="metric-fill" style="width:{p.study_stat}%;"></div></div>
                </div>
                <div class="metric-item">
                    <div class="metric-head"><span>DISCIPLINE INDEX</span><span>HIGHER THAN {p.discipline_stat}%</span></div>
                    <div class="metric-track"><div class="metric-fill" style="width:{p.discipline_stat}%;"></div></div>
                </div>
                <div class="metric-item">
                    <div class="metric-head"><span>PHYSIOLOGICAL VITALITY</span><span>{p.health_score}%</span></div>
                    <div class="metric-track"><div class="metric-fill-health" style="width:{p.health_score}%;"></div></div>
                </div>
            </div>
        </div>
        <div class="bio-alert"><strong>DIAGNOSTIC NOTE:</strong> {p.health_tip}</div>
        <div class="bio-footer"><span>VISUAL: {p.facial_notes}</span><span>TYPE: AI ASSUMPTION</span></div>
    </div>
    """
