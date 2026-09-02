"""Test Groq and Gemini model availability."""
from dotenv import load_dotenv; load_dotenv('.env')
import os

# Test Groq
groq_key = os.getenv('GROQ_API_KEY', '')
print("=== GROQ TESTS ===")
try:
    from groq import Groq
    client = Groq(api_key=groq_key)
    models_to_test = ['qwen/qwen3.6-27b', 'groq/compound-mini', 'groq/compound', 'openai/gpt-oss-120b']
    for model in models_to_test:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{'role': 'user', 'content': 'Return a valid JSON object with field name set to "test"'}],
                temperature=0.1,
                max_tokens=100,
                response_format={'type': 'json_object'},
            )
            content = resp.choices[0].message.content
            print(f"OK   {model}: {content[:60]}")
        except Exception as e:
            print(f"FAIL {model}: {str(e)[:100]}")
except Exception as e:
    print(f"Groq client error: {e}")

# Test Gemini
print("\n=== GEMINI TESTS ===")
gemini_key = os.getenv('GEMINI_API_KEY', '')
try:
    import warnings, google.generativeai as genai
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        genai.configure(api_key=gemini_key)
    
    for model_name in ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-flash-latest']:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(
                'Return a JSON object with field name set to "test"',
                generation_config={"temperature": 0.1, "max_output_tokens": 100, "response_mime_type": "application/json"}
            )
            print(f"OK   {model_name}: {resp.text[:60]}")
        except Exception as e:
            print(f"FAIL {model_name}: {str(e)[:100]}")
except Exception as e:
    print(f"Gemini client error: {e}")
