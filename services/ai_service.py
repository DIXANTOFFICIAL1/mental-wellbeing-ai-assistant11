import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("models/text-bison-001")


def extract_json(text):
    """
    Extract JSON object safely from AI response
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group())
    raise ValueError("No valid JSON found")


def analyze_wellbeing(mood, text):
    prompt = f"""
You are an AI mental well-being support assistant.
This is NOT medical advice.

Analyze the user's input and return ONLY valid JSON.
Do not include markdown or extra text.

JSON format:
{{
  "stress_level": "Low | Moderate | High",
  "stress_score": number between 0 and 100,
  "reasoning": "1-2 sentences explaining why this stress level was detected",
  "daily_plan": {{
    "morning": "specific activity",
    "afternoon": "specific activity",
    "evening": "specific activity"
  }},
  "recommendations": ["tip1", "tip2", "tip3"]
}}

User mood: {mood}
User message: {text}
"""

    try:
        response = model.generate_content(prompt)
        data = extract_json(response.text)

        color_map = {
            "Low": "green",
            "Moderate": "orange",
            "High": "red"
        }

        return {
            "level": f"{data['stress_level']} Stress",
            "score": int(data["stress_score"]),
            "color": color_map.get(data["stress_level"], "orange"),
            "reasoning": data["reasoning"],
            "plan": data["daily_plan"],
            "tips": data["recommendations"]
        }

    except Exception:
     
        return rule_based_fallback(mood, text)


def rule_based_fallback(mood, text):
    text_lower = text.lower()

    stress_score = 25

    if any(word in text_lower for word in ["worried", "anxious", "pressure", "overwhelmed"]):
        stress_score = 55

    if any(word in text_lower for word in ["exhausted", "burnout", "panic", "hopeless", "depressed"]):
        stress_score = 80

    if stress_score < 40:
        level = "Low"
        plan = {
            "morning": "Continue your positive routine and light exercise",
            "afternoon": "Stay focused on productive activities",
            "evening": "Relax with a hobby or calming music"
        }
        tips = [
            "Maintain healthy habits",
            "Practice gratitude",
            "Stay socially connected"
        ]

    elif stress_score < 70:
        level = "Moderate"
        plan = {
            "morning": "Stretching and hydration",
            "afternoon": "Short breaks between tasks",
            "evening": "Reduce screen time before sleep"
        }
        tips = [
            "Improve sleep routine",
            "Prioritize tasks",
            "Practice mindful breathing"
        ]

    else:
        level = "High"
        plan = {
            "morning": "Slow breathing exercises and a short walk",
            "afternoon": "Limit workload and take rest",
            "evening": "Journaling or guided relaxation"
        }
        tips = [
            "Reach out to someone you trust",
            "Avoid overworking",
            "Seek professional support if needed"
        ]

    return {
        "level": f"{level} Stress",
        "score": stress_score,
        "color": "green" if level == "Low" else "orange" if level == "Moderate" else "red",
        "reasoning": "Analysis based on emotional keywords and intensity detected in the user's input.",
        "plan": plan,
        "tips": tips
    }
