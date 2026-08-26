# scraper/oliveyoung.py

import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.oliveyoung.co.kr/store/main/main.do",
    "Origin": "https://www.oliveyoung.co.kr"
}

def parse_cookies(cookie_str: str) -> dict:
    """
    Parses a browser cookie string into a dictionary.
    """
    cookies = {}
    if not cookie_str:
        return cookies
    for item in cookie_str.split(";"):
        item = item.strip()
        if "=" in item:
            k, v = item.split("=", 1)
            cookies[k] = v
    return cookies

def get_request_params(custom_cookies_str=None, custom_ua=None):
    """
    Constructs headers and cookies for requests.
    """
    headers = DEFAULT_HEADERS.copy()
    if custom_ua:
        headers["User-Agent"] = custom_ua
        
    cookies = parse_cookies(custom_cookies_str)
    return headers, cookies

def search_products(keyword, custom_cookies_str=None, custom_ua=None):
    """
    Searches products on Olive Young and returns basic metadata.
    """
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.oliveyoung.co.kr/store/search/getSearchList.do?query={encoded_keyword}"
    
    headers, cookies = get_request_params(custom_cookies_str, custom_ua)
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        products = []
        
        items = soup.select("ul.cate_prd_list li")
        if not items:
            items = soup.select(".prd_info")
            
        for item in items:
            try:
                link_elem = item.select_one("a.prd_thumb, a.prd_info_area")
                if not link_elem:
                    link_elem = item.select_one("a")
                if not link_elem:
                    continue
                
                goods_no = item.get("data-ref-goodsno")
                if not goods_no and link_elem.get("href"):
                    href = link_elem.get("href")
                    match = re.search(r"goodsNo=([^&]+)", href)
                    if match:
                        goods_no = match.group(1)
                    else:
                        js_match = re.search(r"moveGoodsDetail\('([^']+)'\)", href)
                        if js_match:
                            goods_no = js_match.group(1)
                
                if not goods_no:
                    continue
                
                # Brand
                brand_elem = item.select_one(".tx_brand, .tx_brand_name, .brand")
                brand = brand_elem.get_text(strip=True) if brand_elem else "Generic"
                
                # Name
                name_elem = item.select_one(".tx_name, .prd_name, .tx_prd_name")
                name = name_elem.get_text(strip=True) if name_elem else ""
                if not name:
                    continue
                
                # Image
                img_elem = item.select_one("img")
                img_url = ""
                if img_elem:
                    img_url = img_elem.get("data-original") or img_elem.get("src") or ""
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                
                # Price
                org_price_elem = item.select_one(".tx_org, .price-1")
                cur_price_elem = item.select_one(".tx_cur, .price-2")
                
                org_price_str = org_price_elem.get_text(strip=True) if org_price_elem else ""
                cur_price_str = cur_price_elem.get_text(strip=True) if cur_price_elem else ""
                
                org_price = int(re.sub(r"[^\d]", "", org_price_str)) if org_price_str and re.sub(r"[^\d]", "", org_price_str) else None
                cur_price = int(re.sub(r"[^\d]", "", cur_price_str)) if cur_price_str and re.sub(r"[^\d]", "", cur_price_str) else 0
                
                if org_price is None or org_price == 0:
                    org_price = cur_price
                
                products.append({
                    "source": "Olive Young",
                    "goods_no": goods_no,
                    "brand": brand,
                    "name": name,
                    "original_price": org_price,
                    "sale_price": cur_price,
                    "image_url": img_url,
                    "url": f"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo={goods_no}"
                })
            except Exception as e:
                print(f"Error parsing Olive Young item: {e}")
                continue
                
        return products
    except Exception as e:
        print(f"Error fetching search results from Olive Young: {e}")
        return []

def scrape_category(cat_input, page_count=1, custom_cookies_str=None, custom_ua=None):
    """
    Scrapes category items from Olive Young by category ID or Category URL.
    """
    cat_no = str(cat_input).strip()
    if "dispCatNo=" in cat_no:
        match = re.search(r"dispCatNo=([^&]+)", cat_no)
        if match:
            cat_no = match.group(1)
    cat_no = re.sub(r"[^\d]", "", cat_no)
    if not cat_no:
        cat_no = "10000010001"
        
    headers, cookies = get_request_params(custom_cookies_str, custom_ua)
    all_products = []
    
    for page in range(1, page_count + 1):
        url = f"https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo={cat_no}&fltDispCatNo=&prdSort=1&pageIdx={page}&rowsPerPage=48"
        try:
            res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
            if res.status_code != 200:
                print(f"Category fetch failed on page {page}: {res.status_code}")
                break
                
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select("ul.cate_prd_list li, .prd_info")
            if not items:
                break
                
            for item in items:
                try:
                    link_elem = item.select_one("a.prd_thumb, a.prd_info_area") or item.select_one("a")
                    if not link_elem:
                        continue
                    
                    goods_no = item.get("data-ref-goodsno")
                    if not goods_no and link_elem.get("href"):
                        href = link_elem.get("href")
                        match = re.search(r"goodsNo=([^&]+)", href)
                        if match:
                            goods_no = match.group(1)
                        else:
                            js_match = re.search(r"moveGoodsDetail\('([^']+)'\)", href)
                            if js_match:
                                goods_no = js_match.group(1)
                    
                    if not goods_no:
                        continue
                        
                    brand_elem = item.select_one(".tx_brand, .tx_brand_name, .brand")
                    brand = brand_elem.get_text(strip=True) if brand_elem else "Generic"
                    
                    name_elem = item.select_one(".tx_name, .prd_name, .tx_prd_name")
                    name = name_elem.get_text(strip=True) if name_elem else ""
                    if not name:
                        continue
                        
                    img_elem = item.select_one("img")
                    img_url = ""
                    if img_elem:
                        img_url = img_elem.get("data-original") or img_elem.get("src") or ""
                        if img_url.startswith("//"):
                            img_url = "https:" + img_url
                            
                    org_price_elem = item.select_one(".tx_org, .price-1")
                    cur_price_elem = item.select_one(".tx_cur, .price-2")
                    
                    org_price_str = org_price_elem.get_text(strip=True) if org_price_elem else ""
                    cur_price_str = cur_price_elem.get_text(strip=True) if cur_price_elem else ""
                    
                    org_price = int(re.sub(r"[^\d]", "", org_price_str)) if org_price_str and re.sub(r"[^\d]", "", org_price_str) else None
                    cur_price = int(re.sub(r"[^\d]", "", cur_price_str)) if cur_price_str and re.sub(r"[^\d]", "", cur_price_str) else 0
                    
                    if org_price is None or org_price == 0:
                        org_price = cur_price
                        
                    all_products.append({
                        "source": "Olive Young",
                        "goods_no": goods_no,
                        "brand": brand,
                        "name": name,
                        "original_price": org_price,
                        "sale_price": cur_price,
                        "image_url": img_url,
                        "url": f"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo={goods_no}"
                    })
                except Exception:
                    continue
        except Exception as err:
            print(f"Error scraping category page {page}: {err}")
            break
            
    return all_products


def fetch_product_detail(goods_no, custom_cookies_str=None, custom_ua=None):
    """
    Fetches detailed product info for Olive Young product by goodsNo.
    """
    url = f"https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo={goods_no}"
    headers, cookies = get_request_params(custom_cookies_str, custom_ua)
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Title/Brand
        brand_elem = soup.select_one("p.prd_brand, #moveBrandShop")
        brand = brand_elem.get_text(strip=True) if brand_elem else "Generic"
        
        name_elem = soup.select_one("p.prd_name, .prd_title")
        name = name_elem.get_text(strip=True) if name_elem else ""
        
        # Prices
        org_price_elem = soup.select_one(".price-1 strike, .price-1")
        cur_price_elem = soup.select_one(".price-2 .val, .price-2")
        
        org_price_str = org_price_elem.get_text(strip=True) if org_price_elem else ""
        cur_price_str = cur_price_elem.get_text(strip=True) if cur_price_elem else ""
        
        org_price = int(re.sub(r"[^\d]", "", org_price_str)) if org_price_str and re.sub(r"[^\d]", "", org_price_str) else None
        cur_price = int(re.sub(r"[^\d]", "", cur_price_str)) if cur_price_str and re.sub(r"[^\d]", "", cur_price_str) else 0
        
        if org_price is None or org_price == 0:
            org_price = cur_price
            
        # Main Image
        main_img_elem = soup.select_one("#mainImg, .prd_img img, .prd_detail_img img")
        main_img = main_img_elem.get("src") if main_img_elem else ""
        if main_img and main_img.startswith("//"):
            main_img = "https:" + main_img
            
        # Sub Images
        sub_images = []
        thumb_elems = soup.select(".prd_thumb_list img, .prd_detail_thumb img")
        for thumb in thumb_elems:
            src = thumb.get("src") or thumb.get("data-original")
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                if src not in sub_images:
                    sub_images.append(src)
                    
        if main_img and main_img not in sub_images:
            sub_images.insert(0, main_img)
            
        # Descriptions
        desc_container = soup.select_one("#prdInfo, #artcList, .contEditor, .detail_info_wrap")
        description_html = str(desc_container) if desc_container else ""
        description_text = desc_container.get_text(separator="\n", strip=True) if desc_container else ""
        
        # Specs / Weight
        specs = {}
        spec_table = soup.select_one(".table_specification, .prd_detail_info, table")
        if spec_table:
            rows = spec_table.select("tr")
            for row in rows:
                th = row.select_one("th")
                td = row.select_one("td")
                if th and td:
                    specs[th.get_text(strip=True)] = td.get_text(strip=True)
                    
        weight = 0.1 # default weight (100g)
        weight_found = False
        
        for key, val in specs.items():
            if "용량" in key or "중량" in key:
                match = re.search(r"(\d+(?:\.\d+)?)\s*(ml|g|kg|l|밀리리터|그램|킬로그램)", val, re.IGNORECASE)
                if match:
                    val_num = float(match.group(1))
                    unit = match.group(2).lower()
                    if unit in ["g", "ml", "밀리리터", "그램"]:
                        weight = val_num / 1000.0
                    elif unit in ["kg", "킬로그램"]:
                        weight = val_num
                    weight_found = True
                    break
                    
        if not weight_found:
            match = re.search(r"(\d+(?:\.\d+)?)\s*(ml|g|kg|l|밀리리터|그램|킬로그램)", name, re.IGNORECASE)
            if match:
                val_num = float(match.group(1))
                unit = match.group(2).lower()
                if unit in ["g", "ml", "밀리리터", "그램"]:
                    weight = val_num / 1000.0
                elif unit in ["kg", "킬로그램"]:
                    weight = val_num
        
        return {
            "source": "Olive Young",
            "goods_no": goods_no,
            "brand": brand,
            "name": name,
            "original_price": org_price,
            "sale_price": cur_price,
            "image_url": main_img,
            "sub_images": sub_images,
            "description_text": description_text,
            "description_html": description_html,
            "weight": round(weight, 3),
            "specs": specs,
            "url": url
        }
    except Exception as e:
        print(f"Error fetching detail for Olive Young product {goods_no}: {e}")
        return None
