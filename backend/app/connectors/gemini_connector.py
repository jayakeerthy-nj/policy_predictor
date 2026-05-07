import json

import httpx

from app.core.config import settings


class GeminiConnector:
    def generate_scenario_explanation(self, payload: dict) -> str:
        if not settings.gemini_api_key:
            return (
                "Gemini key not configured. Baseline reflects current indicators, "
                "shock amplifies volatility, and policy-adjusted scenario tempers adverse effects."
            )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
        )
        prompt = (
            "You are an economic policy analyst. Based on this JSON data: "
            f"{json.dumps(payload)}\n\n"
            "1. Briefly explain the baseline, shock, and policy-adjusted impacts.\n"
            "2. Provide a Final Verdict for the layman clearly stating:\n"
            "   - Benefits if the policy gets implemented.\n"
            "   - Disadvantages or risks to the common person."
        )
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            with httpx.Client(timeout=20) as client:
                resp = client.post(url, json=body)
                resp.raise_for_status()
                data = resp.json()
                return (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "Explanation unavailable.")
                )
        except Exception:
            return "Gemini call failed; generated fallback explanation for scenario outputs."

