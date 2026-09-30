"""
vlm.py — Vision Language Model description generator.
Uses Gemini Vision (primary) → Groq (fallback) → Rule-based (offline fallback)
"""

import base64
import os
from config import (
    VLM_PROVIDER,
    GEMINI_API_KEY,
    GROQ_API_KEY,
    ENABLE_GROQ_FALLBACK,
    ENABLE_RULE_BASED_FALLBACK,
)


def describe(image_path: str, damage_type: str, severity: str,
             coverage_pct: float = 0.0, num_detections: int = 1,
             analysis_notes: str = "") -> str:
    """
    Generate a natural language description of road damage.
    """
    provider = VLM_PROVIDER.lower().strip()

    if provider == "gemini":
        if not GEMINI_API_KEY:
            return _try_groq_then_rule(image_path, damage_type, severity, coverage_pct, num_detections)
        return _describe_with_gemini(image_path, damage_type, severity, coverage_pct, num_detections, analysis_notes)

    elif provider == "groq":
        if not GROQ_API_KEY:
            return _describe_rule_based(damage_type, severity, coverage_pct, num_detections)
        return _describe_with_groq(image_path, damage_type, severity, coverage_pct, num_detections)

    else:
        return _describe_rule_based(damage_type, severity, coverage_pct, num_detections)


def _try_groq_then_rule(image_path, damage_type, severity, coverage_pct, num_detections=1):
    if ENABLE_GROQ_FALLBACK and GROQ_API_KEY:
        return _describe_with_groq(image_path, damage_type, severity, coverage_pct, num_detections)
    return _describe_rule_based(damage_type, severity, coverage_pct, num_detections)


def _describe_with_gemini(image_path: str, damage_type: str, severity: str,
                           coverage_pct: float, num_detections: int = 1,
                           analysis_notes: str = "") -> str:
    try:
        import google.generativeai as genai

        if not os.path.exists(image_path):
            return _describe_rule_based(damage_type, severity, coverage_pct, num_detections)

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")

        image_part = {"mime_type": mime_type, "data": image_bytes}

        multi = f"{num_detections} instance(s)" if num_detections > 1 else "an instance"
        notes_ctx = f"\nDetection system notes: {analysis_notes}" if analysis_notes else ""

        prompt = (
            f"You are a road damage assessment officer writing an official complaint report for "
            f"a municipal corporation in India.\n\n"
            f"The automated system detected: {damage_type} with {severity} severity, "
            f"finding {multi} covering approximately {coverage_pct:.1f}% of the road surface.{notes_ctx}\n\n"
            f"Write exactly 2-3 sentences for the complaint report describing:\n"
            f"1. What specific road damage is visible in this image\n"
            f"2. The risk it poses to vehicles, motorcycles, and pedestrians\n"
            f"3. The urgency of municipal repair action needed\n\n"
            f"Rules: Write in formal English. Be specific about what you see. "
            f"Do NOT start with 'I' or 'The image shows'. "
            f"Mention the number of damage instances if more than 1. "
            f"Keep it factual and professional."
        )

        response = model.generate_content([image_part, prompt])
        description = response.text.strip()
        print("✅ Gemini VLM description generated")
        return description

    except ImportError:
        print("⚠️  google-generativeai not installed")
        return _try_groq_then_rule(image_path, damage_type, severity, coverage_pct, num_detections)
    except Exception as e:
        print(f"⚠️  Gemini VLM error: {e}")
        return _try_groq_then_rule(image_path, damage_type, severity, coverage_pct, num_detections)


def _describe_with_groq(image_path: str, damage_type: str, severity: str,
                         coverage_pct: float, num_detections: int = 1) -> str:
    try:
        from groq import Groq

        if not os.path.exists(image_path):
            return _describe_rule_based(damage_type, severity, coverage_pct, num_detections)

        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")

        client = Groq(api_key=GROQ_API_KEY)

        multi = f"{num_detections} instances" if num_detections > 1 else "an instance"
        prompt = (
            f"You are writing an official municipal road complaint report in India. "
            f"Detected: {damage_type} ({severity} severity), {multi}, "
            f"covering {coverage_pct:.1f}% of the road surface.\n\n"
            f"Write 2-3 sentences for the complaint describing the visible damage, "
            f"the risk to road users, and why urgent municipal action is needed. "
            f"Formal English. Do not start with 'I' or 'The image shows'."
        )

        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}},
                    {"type": "text", "text": prompt},
                ],
            }],
            max_tokens=250,
        )

        description = response.choices[0].message.content.strip()
        print("✅ Groq VLM description generated")
        return description

    except Exception as e:
        print(f"⚠️  Groq VLM error: {e}")
        return _describe_rule_based(damage_type, severity, coverage_pct, num_detections)


def _describe_rule_based(damage_type: str, severity: str, coverage_pct: float,
                          num_detections: int = 1) -> str:
    sev_word   = {"LOW": "minor", "MEDIUM": "moderate", "HIGH": "severe"}.get(severity, "notable")
    sev_action = {
        "LOW":    "monitoring and routine maintenance",
        "MEDIUM": "scheduled repair within the next two weeks",
        "HIGH":   "immediate emergency repair",
    }.get(severity, "prompt repair")

    multi_str = f"{num_detections} instances of " if num_detections > 1 else ""

    templates = {
        "Pothole": (
            f"{multi_str.capitalize() or 'A'} {sev_word} pothole{'s have' if num_detections > 1 else ' has'} "
            f"been identified on the road surface, affecting approximately {coverage_pct:.1f}% of the visible road area. "
            f"{'These potholes pose' if num_detections > 1 else 'This pothole poses'} a direct hazard to vehicle "
            f"tyres, suspensions, and passenger safety, particularly for two-wheelers. "
            f"The municipal road maintenance authority must undertake {sev_action} immediately."
        ),
        "Alligator Crack": (
            f"Extensive {sev_word} alligator (fatigue) cracking has been observed across "
            f"{coverage_pct:.1f}% of the road surface, indicating advanced structural pavement failure. "
            f"This web-like pattern of interconnected cracks allows water infiltration, accelerates "
            f"subbase deterioration, and creates uneven surfaces dangerous for vehicles. "
            f"Municipal action requires {sev_action}, likely including full resurfacing."
        ),
        "Longitudinal Crack": (
            f"A {sev_word} longitudinal crack running parallel to the traffic direction "
            f"covers {coverage_pct:.1f}% of the road surface. "
            f"Such cracks widen under traffic load and thermal stress, allowing water penetration "
            f"into the subbase layer and accelerating structural deterioration. "
            f"Crack sealing with appropriate compound and {sev_action} is recommended."
        ),
        "Transverse Crack": (
            f"A {sev_word} transverse crack perpendicular to the traffic direction has been detected "
            f"across {coverage_pct:.1f}% of the road surface. "
            f"These thermal or load-induced cracks progress rapidly under heavy traffic and monsoon conditions. "
            f"Municipal road authority should undertake {sev_action} with crack sealing to prevent "
            f"further structural damage."
        ),
    }

    return templates.get(
        damage_type,
        f"Road damage classified as '{damage_type}' ({sev_word} severity) has been detected, "
        f"covering {coverage_pct:.1f}% of the visible road surface with {num_detections} instance(s). "
        f"Municipal inspection and {sev_action} is recommended."
    )


if __name__ == "__main__":
    print(f"VLM Provider:   {VLM_PROVIDER}")
    print(f"Gemini key set: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"Groq key set:   {'✅' if GROQ_API_KEY else '❌'}")

    cases = [
        ("Pothole", "HIGH", 12.4, 3),
        ("Alligator Crack", "MEDIUM", 7.2, 1),
        ("Longitudinal Crack", "LOW", 2.1, 1),
    ]
    for damage, sev, cov, n in cases:
        desc = _describe_rule_based(damage, sev, cov, n)
        print(f"\n[{damage} | {sev} | {cov}% | {n} inst]")
        print(f"  {desc}")
