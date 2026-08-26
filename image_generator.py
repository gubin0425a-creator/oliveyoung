# image_generator.py
import os
import uuid
import base64
from google import genai
from google.genai import types

STATIC_AI_DIR = os.path.join(os.path.dirname(__file__), 'static', 'ai_images')
os.makedirs(STATIC_AI_DIR, exist_ok=True)

STYLE_PROMPTS = {
    "studio": "A high-end luxury commercial studio product photograph of Korean cosmetic {brand} {name}. Packaging & Label details: {details}. Sitting on a sleek minimalist podium, soft diffused studio lighting, clean glass skin aesthetic, crystal clear focus, 4k resolution",
    "lifestyle": "An aesthetic lifestyle photograph of Korean beauty product {brand} {name}. Packaging & Label details: {details}. Placed on a natural wood vanity, surrounded by fresh botanical leaves and gentle morning sunlight, premium commercial shot, 4k",
    "water": "A refreshing commercial product shot of Korean skincare {brand} {name}. Packaging & Label details: {details}. With crystal clear water droplets and gentle water splash background, ultra detailed, clean K-beauty aesthetic, 4k"
}

def generate_ai_product_image(brand, name, visual_description=None, style="studio", api_key=None):
    """
    Generates a unique, highly realistic twin AI product image using Gemini Imagen 3.
    Preserves exact packaging typography, color, and design.
    Returns relative URL path (/static/ai_images/filename.png).
    """
    details = visual_description if visual_description else f"{brand} {name} cosmetic packaging with clear logo and clean design"
    prompt_template = STYLE_PROMPTS.get(style, STYLE_PROMPTS["studio"])
    prompt = prompt_template.format(brand=brand or "K-Beauty", name=name or "Cosmetic Product", details=details)
    
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
    if not api_key:
        raise ValueError("Gemini API Key가 필요합니다.")
        
    try:
        client = genai.Client(api_key=api_key)
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )
        
        if result.generated_images:
            img_bytes = result.generated_images[0].image.image_bytes
            filename = f"ai_prod_{uuid.uuid4().hex[:10]}.png"
            filepath = os.path.join(STATIC_AI_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(img_bytes)
                
            return f"/static/ai_images/{filename}"
        else:
            raise Exception("이미지 생성 결과가 없습니다.")
    except Exception as e:
        print(f"Error in generate_ai_product_image: {e}")
        raise e
