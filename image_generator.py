# image_generator.py
import os
import uuid
import base64
from google import genai
from google.genai import types

STATIC_AI_DIR = os.path.join(os.path.dirname(__file__), 'static', 'ai_images')
os.makedirs(STATIC_AI_DIR, exist_ok=True)

# 올리브영 1위 베스트셀러 썸네일 성공 방정식 & 전략적 프롬프트 프리셋
STYLE_PROMPTS = {
    # 1. 올리브영 스튜디오 시그니처 1:1 대표 컷 (화이트/아이보리 미니멀 클린 배경 + 단상자+본품 풀세트 연출 + 초고해상도 패키징 선명도)
    "studio": (
        "A hyper-realistic top-tier K-beauty commercial hero product photograph of {brand} {name}. "
        "Olive Young No.1 Bestseller signature aesthetic: Pure pristine studio setting with minimalist neutral stone or ivory pedestal, "
        "crisp studio softbox lighting highlighting the sleek product silhouette, crystal-clear label typography and exact brand packaging details: {details}. "
        "Clean, clutter-free, luminous glass skin vibe, razor-sharp focus on texture and cap, ultra-clean professional catalog photography, 8k resolution, photorealistic."
    ),
    
    # 2. 올리브영 기획세트 & 볼륨업 구성 (본품 + 리필/추가 증정 1+1 기획세트 혜택 강조 샷)
    "bundle": (
        "A premium K-beauty promotional bundle packaging shot of {brand} {name}. "
        "Olive Young Special Value Set aesthetic: The main cosmetic bottle prominently featured next to its matching outer paper gift box and bonus travel sachet or refill ampoule. "
        "Visual details: {details}. Bright soft gradient pastel background, award-winning beauty product styling, crisp reflections, commercial e-commerce advertising shot, 8k resolution."
    ),

    # 3. 핵심 유효성분 & 수분/텍스처 임팩트 (물방울, 시카/비타민 원물, 맑은 수분 파동 텍스처 컷)
    "texture": (
        "An eye-catching commercial beauty product close-up of {brand} {name}. "
        "Surrounded by ultra-crisp refreshing micro water droplets, glowing translucent serum texture swirl, and subtle botanical elements matching its core ingredient. "
        "Packaging details: {details}. Vibrant yet clean Korean skincare aesthetic, bright energetic daylight reflection, high conversion advertising photography, 8k resolution."
    ),

    # 4. 라이프스타일 욕실/화장대 감성 컷 (자연광 + 우드/대리석 파우더룸)
    "lifestyle": (
        "An aesthetic lifestyle cosmetic photograph of Korean beauty product {brand} {name}. "
        "Placed on a modern clean marble and wood bathroom vanity bathed in gentle morning sunlight. "
        "Packaging & Label details: {details}. Fresh green eucalyptus accent in background, soft bokeh, luxury Korean spa mood, photorealistic commercial shot, 4k."
    )
}

def generate_ai_product_image(brand, name, visual_description=None, style="studio", api_key=None):
    """
    Generates a high-converting, realistic Olive Young style AI product image using Gemini Imagen 3.
    """
    details = visual_description if visual_description else f"{brand} {name} authentic cosmetic packaging with crisp logo typography and signature colorway"
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
