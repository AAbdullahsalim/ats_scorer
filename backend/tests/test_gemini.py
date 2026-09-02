"""Find which Gemini model actually responds to JSON generation."""
from dotenv import load_dotenv; load_dotenv('.env')
import os, warnings
import google.generativeai as genai

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))

# Models to try (in order of preference)
candidates = [
    'gemini-flash-latest',
    'gemini-flash-lite-latest',
    'gemini-3.1-flash-lite',
    'gemini-3.5-flash',
    'gemini-3.5-flash-lite',
    'gemini-3.1-flash-lite-preview',
    'gemini-3-flash-preview',
]

print("Testing Gemini models for JSON generation:\n")
for model_name in candidates:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(
                'Return a JSON object with a single field "status" set to "ok"',
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 100,
                    "response_mime_type": "application/json"
                }
            )
        text = resp.text if resp.text else "(empty)"
        print(f"OK   {model_name}: {text[:70]}")
    except Exception as e:
        err = str(e)[:100]
        print(f"FAIL {model_name}: {err}")
