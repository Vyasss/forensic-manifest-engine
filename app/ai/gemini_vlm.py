# gemini_vlm.py - FINAL, STABLE VERSION (Uses requests for direct HTTP call)

import os
import time
import re 
import base64 # Required for encoding image data
import requests # Required for direct API call
from dotenv import load_dotenv
from PIL import Image
from google.api_core.exceptions import GoogleAPICallError 
from io import BytesIO # Required for processing image bytes

load_dotenv()

def get_vlm_reasoning_score(image_path: str) -> float:
    """
    Use Gemini VLM for AI detection, using a stable HTTP approach 
    to bypass SDK environment conflicts and ensure reliable scoring.
    """
    
    MODEL_NAME = "gemini-2.5-flash"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
    API_KEY = os.getenv("GEMINI_API_KEY", "") 
    
    SAFER_FALLBACK = 0.5 
    
    # --- Data Preparation (Encode Image to Base64) ---
    try:
        img = Image.open(image_path)
        buffer = BytesIO()
        # Save as JPEG for efficient transfer, even if original was PNG
        img.convert('RGB').save(buffer, format="JPEG", quality=85)
        encoded_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        mime_type = "image/jpeg"
    except Exception as e:
        print(f"❌ Error during image preparation/encoding: {e}")
        return SAFER_FALLBACK

    prompt = """
You are an expert forensic analyst detecting AI-generated images.
Analyze this image for signs of AI generation or manipulation. Look for:

🎨 AI Generation Indicators (increase score):
- Overly smooth/plastic textures (especially skin, fabric, wood)
- Perfect symmetry or unnatural patterns
- Impossible lighting/reflections (multiple light sources, wrong shadows)

📸 Real Photo Indicators (decrease score):
- Natural sensor noise and grain
- Realistic compression artifacts
- Consistent lighting physics

Rate from 0.0 (Definitely real photo) to 1.0 (Definitely AI-generated/edited).
Respond with ONLY a number between 0.0 and 1.0. No explanation.
"""
    
    payload = {
        "contents": [
            {"role": "user", "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": mime_type, "data": encoded_image_data}}
            ]}
        ]
    }
    
    # --- API Call with Requests and Exponential Backoff ---
    max_retries = 3
    base_delay = 1.0 
    
    for attempt in range(max_retries):
        try:
            print(f"🤖 Calling Gemini VLM (HTTP Attempt {attempt + 1})...")
            
            response = requests.post(
                f"{API_URL}?key={API_KEY}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=20 # Added timeout for stability
            )
            response.raise_for_status() 
            
            result = response.json()
            
            # --- Result Parsing ---
            raw_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
            
            try:
                score = float(raw_response)
                score = min(max(score, 0.0), 1.0)
                print(f"✅ VLM Parsed Score: {score:.3f}")
                return score
            except ValueError:
                numbers = re.findall(r'0\.\d+|1\.0|0\.0', raw_response)
                if numbers:
                    score = float(numbers[0])
                    print(f"✅ VLM Extracted Score: {score:.3f}")
                    return score
                return SAFER_FALLBACK

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
            else:
                print(f"❌ Final API Error after {max_retries} attempts: {e}")
                return SAFER_FALLBACK
        
        except Exception as e:
            print(f"❌ General VLM Error: {e}")
            return SAFER_FALLBACK
            
    return SAFER_FALLBACK