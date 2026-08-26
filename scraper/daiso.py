# scraper/daiso.py

import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.daisomall.co.kr/",
    "Origin": "https://www.daisomall.co.kr"
}

CDN_HOST = "https://cdn.daisomall.co.kr"

def search_products(keyword):
    """
    Searches products on Daiso Mall using the SearchGoods JSON API.
    """
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.daisomall.co.kr/ssn/search/SearchGoods?keyword={encoded_keyword}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Error: Daiso search returned status {response.status_code}")
            return []
            
        data = response.json()
        result_list = data.get("resultSet", {}).get("result", [])
        if len(result_list) <= 1:
            print("No product section found in search results.")
            return []
            
        # Section 1 contains resultDocuments
        docs = result_list[1].get("resultDocuments", [])
        products = []
        
        for doc in docs:
            pd_no = doc.get("pdNo")
            if not pd_no:
                continue
                
            name = doc.get("exhPdNm") or doc.get("pdNm") or ""
            price = int(doc.get("pdPrc", 0))
            
            img_url = doc.get("pdImgUrl") or ""
            if img_url and img_url.startswith("/"):
                img_url = CDN_HOST + img_url
                
            brand = doc.get("brndNm") or "Daiso"
            
            products.append({
                "source": "Daiso Mall",
                "goods_no": str(pd_no),
                "brand": brand,
                "name": name,
                "original_price": price,
                "sale_price": price,
                "image_url": img_url,
                "url": f"https://www.daisomall.co.kr/pd/pdr/SCR_PDR_0001?pdNo={pd_no}"
            })
            
        return products
    except Exception as e:
        print(f"Error searching Daiso Mall: {e}")
        return []

def get_daiso_bestsellers():
    """
    Fetches Daiso Mall beauty and skincare products for Daiso's dedicated carousel.
    """
    prods = search_products("뷰티")
    if len(prods) < 10:
        prods.extend(search_products("화장품"))
    unique = {}
    for p in prods:
        if p['goods_no'] not in unique:
            unique[p['goods_no']] = p
    return list(unique.values())[:20]


def fetch_product_detail(goods_id):
    """
    Fetches details of a Daiso product using the goods_id (pdNo).
    Parses product details from ld+json script tags.
    """
    url = f"https://www.daisomall.co.kr/pd/pdr/SCR_PDR_0001?pdNo={goods_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Error: Daiso detail returned status {response.status_code} for {goods_id}")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Parse LD+JSON product schema
        product_data = None
        ld_scripts = soup.find_all("script", type="application/ld+json")
        for script in ld_scripts:
            try:
                script_data = json.loads(script.string or "{}")
                if script_data.get("@type") == "Product":
                    product_data = script_data
                    break
            except Exception:
                continue
                
        if not product_data:
            print(f"Product schema not found on detail page for {goods_id}")
            return None
            
        name = product_data.get("name", "")
        brand = product_data.get("brand", {}).get("name") or "Daiso"
        price = int(product_data.get("offers", {}).get("price", 3000))
        description_text = product_data.get("description", "")
        
        # Images
        image_list = product_data.get("image", [])
        if isinstance(image_list, str):
            image_list = [image_list]
            
        main_img = image_list[0] if image_list else ""
        if main_img and main_img.startswith("/"):
            main_img = CDN_HOST + main_img
            
        sub_images = []
        for img in image_list:
            if img.startswith("/"):
                img = CDN_HOST + img
            if img not in sub_images:
                sub_images.append(img)
                
        # Parse additional properties for weight
        weight = 0.05  # Default weight (50g)
        specs = {}
        
        props = product_data.get("additionalProperty", [])
        for prop in props:
            p_name = prop.get("name", "")
            p_val = prop.get("value", "")
            specs[p_name] = p_val
            
            if "중량" in p_name or "용량" in p_name or "크기" in p_name:
                match = re.search(r"(\d+(?:\.\d+)?)\s*(ml|g|kg|l|밀리리터|그램)", p_val, re.IGNORECASE)
                if match:
                    val_num = float(match.group(1))
                    unit = match.group(2).lower()
                    if unit in ["g", "ml", "밀리리터", "그램"]:
                        weight = val_num / 1000.0
                    elif unit in ["kg"]:
                        weight = val_num
                        
        # Description HTML section in Daiso
        desc_container = soup.select_one(".goods_description, #prdInfo, #artcList, .contEditor, .detail_info")
        description_html = str(desc_container) if desc_container else ""
        if not description_text and desc_container:
            description_text = desc_container.get_text(separator="\n", strip=True)
            
        return {
            "source": "Daiso Mall",
            "goods_no": str(goods_id),
            "brand": brand,
            "name": name,
            "original_price": price,
            "sale_price": price,
            "image_url": main_img,
            "sub_images": sub_images,
            "description_text": description_text,
            "description_html": description_html,
            "weight": round(weight, 3),
            "specs": specs,
            "url": url
        }
    except Exception as e:
        print(f"Error fetching detail for Daiso product {goods_id}: {e}")
        return None

if __name__ == "__main__":
    print("Testing Daiso scraper...")
    res = search_products("리들샷")
    print(f"Found {len(res)} products.")
    if res:
        print(res[0])
