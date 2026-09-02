import os
import warnings
from dotenv import load_dotenv

load_dotenv('.env')

# Suppress the deprecation warnings so the output is clean
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import google.generativeai as genai
    
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        print('ERROR: GEMINI_API_KEY not found in .env')
        exit(1)
        
    print(f'Using API Key starting with: {key[:10]}...')
    genai.configure(api_key=key)
    
    try:
        print('Testing Gemini model (gemini-3.5-flash-lite)...')
        model = genai.GenerativeModel('gemini-3.5-flash-lite')
        
        resp = model.generate_content(
            'Return a JSON object with a single field "status" set to "success". Return ONLY valid JSON.',
            generation_config={
                'temperature': 0.1, 
                'max_output_tokens': 100, 
                'response_mime_type': 'application/json'
            }
        )
        print('\n--- GEMINI RESPONSE ---')
        print(resp.text)
        print('-----------------------')
        print('SUCCESS: Gemini is working perfectly!')
        
    except Exception as e:
        print(f'\nERROR: Gemini call failed!\n{e}')
