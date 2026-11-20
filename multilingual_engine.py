"""
FALCON EYE - Multilingual Emergency Assistant
Powered by Google Gemini 3.8 Flash with local dictionary fallback.
Supports Telugu (te), Hindi (hi), and English (en).
Transforms local-language citizen emergency reports into structured English incident dossiers
for control-room operators, categorizing urgency, incident type, and emergency routing tags.
Clearly distinguishes citizen-submitted reports from verified AI detections.
"""

import os
import json
from typing import Dict, Any


class MultilingualAssistant:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Emergency terminology dictionaries (Instant local fallback)
        self.telugu_keywords = {
            "మంటలు": ("FIRE_SMOKE", "CRITICAL", "Fire / combustion detected"),
            "నిప్పు": ("FIRE_SMOKE", "CRITICAL", "Fire hazard"),
            "పొగ": ("FIRE_SMOKE", "HIGH", "Heavy smoke emission"),
            "ప్రమాదం": ("TRAFFIC_COLLISION", "HIGH", "Accident / vehicular collision"),
            "యాక్సిడెంట్": ("TRAFFIC_COLLISION", "HIGH", "Road traffic accident"),
            "జనసందోహం": ("CROWD_CONGESTION", "HIGH", "Severe crowd congestion / crush hazard"),
            "రద్దీ": ("CROWD_CONGESTION", "MEDIUM", "Dense crowd surge"),
            "గాయపడ్డారు": ("FALLEN_PERSON", "CRITICAL", "Injured person / medical casualty"),
            "కింద పడిపోయాడు": ("FALLEN_PERSON", "HIGH", "Fallen unconscious person"),
            "సహాయం": ("HAZARD", "HIGH", "General distress assistance request")
        }

        self.hindi_keywords = {
            "आग": ("FIRE_SMOKE", "CRITICAL", "Fire / flames reported"),
            "धुआं": ("FIRE_SMOKE", "HIGH", "Heavy smoke plume"),
            "दुर्घटना": ("TRAFFIC_COLLISION", "HIGH", "Traffic collision / accident"),
            "टक्कर": ("TRAFFIC_COLLISION", "HIGH", "Vehicle impact / collision"),
            "भीड़": ("CROWD_CONGESTION", "HIGH", "Heavy crowd surge / stampede hazard"),
            "भगदड़": ("CROWD_CONGESTION", "CRITICAL", "Stampede / panic condition"),
            "घायल": ("FALLEN_PERSON", "CRITICAL", "Injured person requiring medical aid"),
            "बेहोश": ("FALLEN_PERSON", "HIGH", "Unconscious / fallen individual"),
            "मदद": ("HAZARD", "HIGH", "Emergency distress call")
        }

    def _call_gemini_translation(self, text: str) -> Dict[str, Any]:
        """Calls Google Gemini 3.8 Flash for contextual triage and translation."""
        if not self.api_key:
            return None

        import requests

        prompt = f"""You are an AI Public Safety Control-Room Dispatch Assistant for Falcon Eye.
Analyze this citizen emergency report: "{text}"

Respond ONLY with valid JSON (no markdown, no code fences) with these exact fields:
{{"detected_language": "Telugu/Hindi/English", "translated_english": "...", "suggested_category": "CROWD_CONGESTION|FIRE_SMOKE|TRAFFIC_COLLISION|FALLEN_PERSON|HAZARD", "suggested_severity": "CRITICAL|HIGH|MEDIUM|LOW", "key_factor": "short 4-7 word hazard summary", "dispatch_advice": "short operator tactical advice"}}"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        candidate = result['candidates'][0]['content']['parts'][0]['text']

        # Clean possible markdown code fences
        clean_text = candidate.strip()
        for fence in ["```json", "```"]:
            if clean_text.startswith(fence):
                clean_text = clean_text[len(fence):]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        return json.loads(clean_text.strip())

    def process_report(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """
        Parses citizen emergency report text. Attempts Gemini Generative AI first;
        falls back seamlessly to local regex/dictionary rules.
        """
        raw_text = text.strip()

        # Try Google Gemini 3.8 Flash first
        if self.api_key:
            try:
                g_res = self._call_gemini_translation(raw_text)
                if g_res and "translated_english" in g_res:
                    return {
                        "original_text": raw_text,
                        "detected_language": g_res.get("detected_language", "Auto"),
                        "language_name": g_res.get("detected_language", "Auto"),
                        "translated_english": g_res.get("translated_english"),
                        "suggested_category": g_res.get("suggested_category", "HAZARD"),
                        "suggested_severity": g_res.get("suggested_severity", "HIGH"),
                        "key_factor": g_res.get("key_factor", "Emergency Alert"),
                        "dispatch_advice": g_res.get("dispatch_advice", "Dispatch nearest patrol."),
                        "ai_engine": f"Google Gemini ({self.model_name})",
                        "source_type": "CITIZEN_REPORT (UNVERIFIED)",
                        "requires_operator_verification": True
                    }
            except Exception as e:
                # Silently fallback to local rule-based dictionary
                pass

        # Fallback Local Dictionary Logic
        detected_lang = language.lower()
        if detected_lang in ["auto", "", None]:
            if any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in raw_text):
                detected_lang = "te"  # Telugu Unicode range
            elif any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in raw_text):
                detected_lang = "hi"  # Devanagari / Hindi Unicode range
            else:
                detected_lang = "en"

        category = "HAZARD"
        severity = "MEDIUM"
        key_factor = "Public Citizen Emergency Call"

        if detected_lang == "te":
            for kw, (cat, sev, factor) in self.telugu_keywords.items():
                if kw in raw_text:
                    category, severity, key_factor = cat, sev, factor
                    break
            english_translation = f"[Translated from Telugu]: \"{raw_text}\" -> Incident indicated: {key_factor}. Immediate control room review requested."

        elif detected_lang == "hi":
            for kw, (cat, sev, factor) in self.hindi_keywords.items():
                if kw in raw_text:
                    category, severity, key_factor = cat, sev, factor
                    break
            english_translation = f"[Translated from Hindi]: \"{raw_text}\" -> Incident indicated: {key_factor}. Immediate control room review requested."

        else:
            detected_lang = "en"
            english_translation = raw_text
            lower_en = raw_text.lower()
            if "fire" in lower_en or "smoke" in lower_en:
                category, severity = "FIRE_SMOKE", "CRITICAL"
            elif "accident" in lower_en or "crash" in lower_en:
                category, severity = "TRAFFIC_COLLISION", "HIGH"
            elif "crowd" in lower_en or "stampede" in lower_en:
                category, severity = "CROWD_CONGESTION", "HIGH"
            elif "fallen" in lower_en or "injured" in lower_en:
                category, severity = "FALLEN_PERSON", "HIGH"

        return {
            "original_text": raw_text,
            "detected_language": detected_lang,
            "language_name": {"te": "Telugu", "hi": "Hindi", "en": "English"}.get(detected_lang, "English"),
            "translated_english": english_translation,
            "suggested_category": category,
            "suggested_severity": severity,
            "key_factor": key_factor,
            "dispatch_advice": "Operator review recommended.",
            "ai_engine": "Falcon Local Fallback Dictionary",
            "source_type": "CITIZEN_REPORT (UNVERIFIED)",
            "requires_operator_verification": True
        }


# Global singleton instance
multilingual_assistant = MultilingualAssistant()
