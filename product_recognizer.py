# product_recognizer.py
import os
import json
import re
from google import genai
from google.genai import types

RECOGNITION_PROMPT = """
You are an expert K-Beauty product identifier and visual OCR parser.
Analyze the provided product image in extreme detail. Read all visible text on the packaging, label, bottle, or box.

Identify and extract:
1. Exact Brand Name (e.g. Anua, VT, Round Lab, Torriden, Numbuzin, Mediheal, etc.)
2. Exact Product Title in Korean and English (read all letters printed on the bottle/box)
3. Best Search Query to find this exact product on Olive Young or Daiso Mall.
4. Highly detailed visual description of the packaging (bottle shape, container color, label text, typography, cap style, liquid texture) to generate a realistic twin AI product photograph.

Return ONLY a valid JSON object in the following format (no markdown code fences):
{
    "brand": "Brand Name",
    "product_name": "Full Product Name",
    "search_query": "Best Search Keyword",
    "visual_description": "Detailed visual description of bottle, color, text, label style"
}
"""

def recognize_product_from_image(image_bytes, mime_type="image/jpeg", api_key=None):
    """
    Uses Gemini Multimodal Vision to recognize product, read label text, and return exact details.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
    if not api_key:
        raise ValueError("Gemini API Key가 필요합니다.")
        
    client = genai.Client(api_key=api_key)
    
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image_part, RECOGNITION_PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    raw_text = response.text.strip()
    # Clean code blocks if present
    cleaned = re.sub(r"^```json\s*", "", raw_text)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    
    try:
        data = json.loads(cleaned)
        return data
    except Exception as parse_err:
        print(f"Error parsing Gemini Vision JSON response: {parse_err}. Raw text: {raw_text}")
        return {
            "brand": "Recognized Product",
            "product_name": raw_text[:100],
            "search_query": raw_text[:50],
            "visual_description": raw_text[:200]
        }
