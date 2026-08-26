# translator.py

import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# Define the Pydantic schema for structured output
class ListingDetails(BaseModel):
    brand_english: str = Field(description="The brand name translated/transliterated to English. E.g. '라운드랩' -> 'Round Lab'")
    title: str = Field(description="SEO optimized e-commerce product name in English: [Brand Name] + [Product Name] + [Key specs like volume (e.g. 50ml), skin type, main benefit] + keywords (e.g. K-Beauty, Korean Cosmetics). Max 80 characters.")
    description: str = Field(description="Clear, well-formatted English description of the product. Include: 1) What it is, 2) Key features/ingredients, 3) How to use.")
    tags: List[str] = Field(description="List of 5-8 relevant hashtags in English, starting with #. E.g. ['#kbeauty', '#roundlab', '#toner']")

def translate_and_optimize(brand: str, name: str, description_text: str, api_key: str = None) -> ListingDetails:
    """
    Translates product info from Korean to English and optimizes it for global e-commerce listing
    using Gemini structured output.
    """
    # Use provided key or fall back to env variable
    api_key_to_use = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key_to_use:
        # Return fallback mock if no API key is set
        print("Warning: No GEMINI_API_KEY found. Using local translation fallback.")
        return get_fallback_translation(brand, name, description_text)
        
    try:
        client = genai.Client(api_key=api_key_to_use)
        
        prompt = f"""
        You are an expert global e-commerce merchandiser specializing in Korean beauty (K-Beauty) cosmetics.
        Your task is to translate and optimize the following Korean product details into a high-converting English listing.
        
        Korean Brand Name: {brand}
        Korean Product Name: {name}
        
        Korean Product Description text:
        {description_text[:2500]}
        
        Instructions:
        1. Translate the brand name to its official or common English spelling.
        2. Create an SEO-friendly e-commerce Title (Max 80 characters). Make it highly searchable by combining: Brand + Product Name + Size/Weight + Key Benefits + 'K-Beauty'.
        3. Translate the description to professional English. Make it easy to read with bullet points for key features and usage instructions. Remove any shipping or return policy details specific to the Korean domestic market.
        4. Generate relevant hashtags.
        """
        
        # Use gemini-2.5-flash as the fast and standard model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ListingDetails,
                temperature=0.2
            ),
        )
        
        # The SDK automatically parses the JSON response into the Pydantic schema
        # but let's double check if we can access the parsed object directly.
        # Yes, response.parsed contains the instantiated Pydantic object when response_schema is specified.
        if response.parsed:
            return response.parsed
            
        # Fallback if parsing didn't happen automatically (depending on SDK version)
        import json
        data = json.loads(response.text)
        return ListingDetails(**data)
        
    except Exception as e:
        print(f"Error in Gemini translation: {e}")
        return get_fallback_translation(brand, name, description_text)

def get_fallback_translation(brand: str, name: str, description_text: str) -> ListingDetails:
    """
    Simple heuristic translation fallback in case Gemini API is unavailable or has errors.
    """
    # Simple dictionary for common Korean brand names to English
    brand_dict = {
        "라운드랩": "Round Lab",
        "독도": "Dokdo",
        "어누아": "Anua",
        "조선미녀": "Beauty of Joseon",
        "구달": "Goodal",
        "메디힐": "Mediheal",
        "코스알엑스": "COSRX",
        "스킨푸드": "Skinfood",
        "토리든": "Torriden",
        "다이소": "Daiso",
        "올리브영": "Olive Young",
        "필리밀리": "Fillimilli"
    }
    
    brand_eng = brand_dict.get(brand, brand)
    
    # Replace some common terms in title
    name_eng = name
    replacements = {
        "토너": "Toner",
        "세럼": "Serum",
        "크림": "Cream",
        "폼클렌징": "Cleansing Foam",
        "클렌징": "Cleansing",
        "썬크림": "Sunscreen",
        "선크림": "Sunscreen",
        "마스크팩": "Mask Sheet",
        "앰플": "Ampoule",
        "패드": "Pad",
        "리들샷": "Reedle Shot"
    }
    for ko, eng in replacements.items():
        name_eng = name_eng.replace(ko, eng)
        
    seo_title = f"{brand_eng} {name_eng} | Korean Cosmetics K-Beauty"
    if len(seo_title) > 80:
        seo_title = seo_title[:77] + "..."
        
    desc_eng = f"Product Brand: {brand_eng}\nProduct Name: {name_eng}\n\n[Product Description]\n(Original Korean Description follows)\n{description_text[:500]}"
    
    return ListingDetails(
        brand_english=brand_eng,
        title=seo_title,
        description=desc_eng,
        tags=["#kbeauty", f"#{brand_eng.lower().replace(' ', '')}", "#koreancosmetics"]
    )
