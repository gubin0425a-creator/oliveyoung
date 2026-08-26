# app.py
# -*- coding: utf-8 -*-

import os
import uuid
import json
import time
import threading
import socket
from datetime import datetime
from flask import Flask, request, jsonify, render_template, make_response, redirect, send_file

AUTO_CONFIG_FILE = os.path.join(DATA_DIR, 'auto_config.json')

def load_auto_config():
    return load_json(AUTO_CONFIG_FILE, {
        "enabled": True,
        "schedule_times": ["09:00", "17:00"],
        "interval_minutes": 60,
        "categories": ["10000010001"],
        "auto_translate": True,
        "last_run": None,
        "total_auto_collected": 0
    })


def save_auto_config(config):
    save_json(AUTO_CONFIG_FILE, config)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


from scraper.oliveyoung import search_products as search_oy, fetch_product_detail as fetch_oy_detail, scrape_category as scrape_oy_category, get_best_sellers as get_oy_bestsellers

from scraper.daiso import search_products as search_ds, fetch_product_detail as fetch_ds_detail

import base64
from translator import translate_and_optimize
from calculator import calculate_target_price
from exporter import export_to_shopee_excel, export_to_shopify_csv
from image_generator import generate_ai_product_image
from product_recognizer import recognize_product_from_image



import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    # PyInstaller extracts resources to sys._MEIPASS
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
    # Put user files in the same directory as the executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    app = Flask(__name__)

DEVICES_FILE = os.path.join(BASE_DIR, 'devices.json')
QUEUES_FILE = os.path.join(BASE_DIR, 'queues.json')


def load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return default

def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving {path}: {e}")

# Load or init queues
# queues.json structure: { "sourcing_queue": {}, "listing_queue": {} }
def load_queues():
    return load_json(QUEUES_FILE, {"sourcing_queue": {}, "listing_queue": {}})

def save_queues(queues):
    save_json(QUEUES_FILE, queues)

def auto_scraper_loop():
    while True:
        try:
            config = load_auto_config()
            if config.get("enabled"):
                last_run_str = config.get("last_run")
                now_hm = datetime.now().strftime('%H:%M')
                scheduled_times = config.get("schedule_times", ["09:00", "17:00"])
                
                should_run = False
                if now_hm in scheduled_times and config.get("last_run_hm") != now_hm:
                    should_run = True
                    config["last_run_hm"] = now_hm
                elif not last_run_str:
                    should_run = True
                else:
                    try:
                        last_run_dt = datetime.strptime(last_run_str, '%Y-%m-%d %H:%M:%S')
                        if (datetime.now() - last_run_dt).total_seconds() >= interval_sec:
                            should_run = True
                    except Exception:
                        should_run = True
                        
                if should_run:

                    print("[AutoScraper] Starting periodic background auto-sourcing...")
                    categories = config.get("categories", ["10000010001"])
                    collected_count = 0
                    
                    for cat_id in categories:
                        prods = scrape_oy_category(cat_id, page_count=1)
                        if prods:
                            queues = load_queues()
                            src_q = queues.get("sourcing_queue", {})
                            list_q = queues.get("listing_queue", {})
                            
                            for p in prods[:24]:
                                gno = p['goods_no']
                                if gno not in src_q and gno not in list_q:
                                    detail = fetch_oy_detail(gno)
                                    if detail:
                                        p.update(detail)
                                    src_q[gno] = p
                                    collected_count += 1
                                    
                                    if config.get("auto_translate"):
                                        try:
                                            translated = translate_and_optimize(
                                                p['name'],
                                                p.get('description', ''),
                                                p.get('ingredients', ''),
                                                brand=p.get('brand', '')
                                            )
                                            p['english_title'] = translated.get('english_title', p['name'])
                                            p['english_description'] = translated.get('english_description', '')
                                            p['search_tags'] = translated.get('search_tags', '')
                                        except Exception:
                                            p['english_title'] = p['name']
                                            
                                        pricing = calculate_target_price(p['sale_price'], weight_kg=0.3, markup_ratio=1.5)
                                        p['calculated_price'] = pricing.get('final_price_target', 0)
                                        list_q[gno] = p
                                        
                            queues["sourcing_queue"] = src_q
                            queues["listing_queue"] = list_q
                            save_queues(queues)
                            
                    config["last_run"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    config["total_auto_collected"] = config.get("total_auto_collected", 0) + collected_count
                    save_auto_config(config)
                    print(f"[AutoScraper] Finished scheduled run. Auto-collected {collected_count} new items.")
        except Exception as e:
            print(f"[AutoScraper] Daemon loop error: {e}")
            
        time.sleep(30)

auto_thread = threading.Thread(target=auto_scraper_loop, daemon=True)
auto_thread.start()


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.before_request
def check_auth():
    if request.method == 'OPTIONS':
        res = make_response('', 200)
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        res.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return res

    if request.path.startswith('/api/'):
        return

    if request.path in ['/login', '/api/auth']:
        return
    if request.path.startswith('/static'):
        return
    device_id = request.cookies.get('device_id')
    devices = load_json(DEVICES_FILE, [])
    device = next((d for d in devices if d['id'] == device_id), None)
    if not device:
        return redirect('/login')
    device['last_used'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_json(DEVICES_FILE, devices)


@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/auth', methods=['POST'])
def auth_device():
    pwd = request.form.get('password', '').strip()
    if pwd != '635835':
        return jsonify({'success': False, 'msg': '마스터 암호가 일치하지 않습니다. (635835)'})
        
    devices = load_json(DEVICES_FILE, [])
    if len(devices) >= 9:
        return jsonify({'success': False, 'msg': '최대 등록 디바이스 한도(9대)를 초과했습니다. 관리자에게 문의하세요.'})
        
    new_id = str(uuid.uuid4())
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    device_name = request.form.get('device_name', f'Member Device #{len(devices)+1}').strip()
    
    devices.append({
        'id': new_id,
        'device_name': device_name,
        'product_name': user_agent[:45],
        'registered_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'last_used': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_json(DEVICES_FILE, devices)
    
    resp = make_response(jsonify({'success': True}))
    resp.set_cookie('device_id', new_id, max_age=60*60*24*365)
    return resp

@app.route('/api/logout', methods=['POST'])
def logout():
    device_id = request.cookies.get('device_id')
    devices = load_json(DEVICES_FILE, [])
    devices = [d for d in devices if d['id'] != device_id]
    save_json(DEVICES_FILE, devices)
    
    resp = make_response(jsonify({'success': True}))
    resp.delete_cookie('device_id')
    return resp

@app.route('/')
def index():
    devices = load_json(DEVICES_FILE, [])
    current_id = request.cookies.get('device_id')
    current_device = next((d for d in devices if d['id'] == current_id), None)
    return render_template('index.html', device=current_device, device_count=len(devices))

@app.route('/api/info')
def api_info():
    local_ip = get_local_ip()
    return jsonify({
        'local_ip': local_ip,
        'port': 8501,
        'network_url': f"http://{local_ip}:8501"
    })

@app.route('/api/auto_config', methods=['GET', 'POST'])
def api_auto_config():
    if request.method == 'POST':
        data = request.json or {}
        config = load_auto_config()
        config['enabled'] = bool(data.get('enabled', False))
        if 'interval_minutes' in data:
            config['interval_minutes'] = int(data['interval_minutes'])
        if 'categories' in data:
            config['categories'] = data['categories']
        if 'auto_translate' in data:
            config['auto_translate'] = bool(data['auto_translate'])
        save_auto_config(config)
        return jsonify({'success': True, 'config': config})
    else:
        return jsonify(load_auto_config())

@app.route('/api/auto_config/run_now', methods=['POST'])
def api_auto_run_now():
    try:
        config = load_auto_config()
        categories = config.get("categories", ["10000010001"])
        collected_count = 0
        
        bests = get_oy_bestsellers()
        queues = load_queues()
        src_q = queues.get("sourcing_queue", {})
        list_q = queues.get("listing_queue", {})
        
        for p in bests[:16]:
            gno = p['goods_no']
            if gno not in src_q and gno not in list_q:
                detail = fetch_oy_detail(gno)
                if detail:
                    p.update(detail)
                src_q[gno] = p
                collected_count += 1
                
                try:
                    translated = translate_and_optimize(
                        p['name'],
                        p.get('description', ''),
                        p.get('ingredients', ''),
                        brand=p.get('brand', '')
                    )
                    p['english_title'] = translated.get('english_title', p['name'])
                    p['english_description'] = translated.get('english_description', '')
                    p['search_tags'] = translated.get('search_tags', '')
                except Exception:
                    p['english_title'] = p['name']
                    
                pricing = calculate_target_price(p['sale_price'], weight_kg=0.3, markup_ratio=1.5)
                p['calculated_price'] = pricing.get('final_price_target', 0)
                list_q[gno] = p

        for cat_id in categories:
            prods = scrape_oy_category(cat_id, page_count=1)
            if prods:
                for p in prods[:16]:
                    gno = p['goods_no']
                    if gno not in src_q and gno not in list_q:
                        detail = fetch_oy_detail(gno)
                        if detail:
                            p.update(detail)
                        src_q[gno] = p
                        collected_count += 1
                        
                        try:
                            translated = translate_and_optimize(
                                p['name'],
                                p.get('description', ''),
                                p.get('ingredients', ''),
                                brand=p.get('brand', '')
                            )
                            p['english_title'] = translated.get('english_title', p['name'])
                            p['english_description'] = translated.get('english_description', '')
                            p['search_tags'] = translated.get('search_tags', '')
                        except Exception:
                            p['english_title'] = p['name']
                            
                        pricing = calculate_target_price(p['sale_price'], weight_kg=0.3, markup_ratio=1.5)
                        p['calculated_price'] = pricing.get('final_price_target', 0)
                        list_q[gno] = p
                        
        queues["sourcing_queue"] = src_q
        queues["listing_queue"] = list_q
        save_queues(queues)
        
        config["last_run"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        config["total_auto_collected"] = config.get("total_auto_collected", 0) + collected_count
        save_auto_config(config)
        
        return jsonify({'success': True, 'count': collected_count, 'message': f'신규 {collected_count}개 상품 즉시 수집 및 AI 번역 완료'})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})


from scraper.daiso import search_products as search_ds, fetch_product_detail as fetch_ds_detail, get_daiso_bestsellers

@app.route('/api/bestsellers', methods=['GET', 'POST'])
def api_bestsellers():
    cookies_str = request.args.get('cookies', '') or (request.json or {}).get('cookies', '')
    ua = request.args.get('ua', '') or (request.json or {}).get('ua', '')
    oy_bests = get_oy_bestsellers(custom_cookies_str=cookies_str, custom_ua=ua)
    ds_bests = get_daiso_bestsellers()
    return jsonify({
        'oliveyoung': oy_bests,
        'daiso': ds_bests
    })


@app.route('/api/queues')


def api_queues():
    return jsonify(load_queues())


@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json or {}
    query = data.get('query', '').strip()
    channel = data.get('channel', 'all')
    cookies_str = data.get('cookies', '')
    ua = data.get('ua', '')
    mode = data.get('mode', 'keyword')
    pages = int(data.get('pages', 1))
    
    results = []
    
    # Check if category mode or category URL
    is_cat = (mode == 'category') or ('dispCatNo=' in query) or (query.isdigit() and len(query) >= 8)
    
    if is_cat and channel in ['oy', 'all']:
        results.extend(scrape_oy_category(query, page_count=pages, custom_cookies_str=cookies_str, custom_ua=ua))
    else:
        if channel in ['oy', 'all']:
            results.extend(search_oy(query, custom_cookies_str=cookies_str, custom_ua=ua))
        if channel in ['ds', 'all']:
            results.extend(search_ds(query))
            
    return jsonify({'results': results})


@app.route('/api/sourcing/add', methods=['POST'])
def api_sourcing_add():
    data = request.json or {}
    products = data.get('products', [])
    cookies_str = data.get('cookies', '')
    ua = data.get('ua', '')
    
    queues = load_queues()
    sourcing = queues.get('sourcing_queue', {})
    
    for item in products:
        goods_no = item.get('goods_no')
        source = item.get('source')
        if not goods_no:
            continue
            
        # If detail not already in queue, fetch full details
        if goods_no not in sourcing:
            detail = None
            if source == 'Olive Young':
                detail = fetch_oy_detail(goods_no, custom_cookies_str=cookies_str, custom_ua=ua)
            else:
                detail = fetch_ds_detail(goods_no)
                
            if detail:
                sourcing[goods_no] = detail
                
    queues['sourcing_queue'] = sourcing
    save_queues(queues)
    return jsonify({'success': True})

@app.route('/api/sourcing/delete', methods=['POST'])
def api_sourcing_delete():
    data = request.json or {}
    goods_no = data.get('goods_no')
    
    queues = load_queues()
    if goods_no in queues['sourcing_queue']:
        del queues['sourcing_queue'][goods_no]
        save_queues(queues)
        return jsonify({'success': True})
    return jsonify({'success': False, 'msg': 'Item not found'})

@app.route('/api/sourcing/clear', methods=['POST'])
def api_sourcing_clear():
    queues = load_queues()
    queues['sourcing_queue'] = {}
    save_queues(queues)
    return jsonify({'success': True})

@app.route('/api/translate/single', methods=['POST'])
def api_translate_single():
    data = request.json or {}
    goods_no = data.get('goods_no')
    api_key = data.get('api_key', '')
    
    queues = load_queues()
    sourcing = queues.get('sourcing_queue', {})
    listing = queues.get('listing_queue', {})
    
    if goods_no not in sourcing:
        return jsonify({'success': False, 'msg': 'Item not found in sourcing queue'})
        
    item = sourcing[goods_no]
    
    # Translate
    trans = translate_and_optimize(
        brand=item.get('brand', ''),
        name=item.get('name', ''),
        description_text=item.get('description_text', ''),
        api_key=api_key
    )
    
    item['brand_english'] = trans.brand_english
    item['translated_title'] = trans.title
    item['translated_description'] = trans.description
    item['tags'] = trans.tags
    item['stock'] = 100
    item['calculated_price'] = 0.0
    
    # Move to listing queue
    listing[goods_no] = item
    del sourcing[goods_no]
    
    queues['sourcing_queue'] = sourcing
    queues['listing_queue'] = listing
    save_queues(queues)
    return jsonify({'success': True})

@app.route('/api/listing/update', methods=['POST'])
def api_listing_update():
    data = request.json or {}
    goods_no = data.get('goods_no')
    
    queues = load_queues()
    listing = queues.get('listing_queue', {})
    
    if goods_no not in listing:
        return jsonify({'success': False, 'msg': 'Item not found in listing queue'})
        
    listing[goods_no]['translated_title'] = data.get('title')
    listing[goods_no]['translated_description'] = data.get('description')
    listing[goods_no]['tags'] = data.get('tags', [])
    listing[goods_no]['weight'] = data.get('weight', 0.1)
    listing[goods_no]['stock'] = data.get('stock', 100)
    listing[goods_no]['calculated_price'] = data.get('calculated_price', 0.0)
    
    save_queues(queues)
    return jsonify({'success': True})

@app.route('/api/listing/delete', methods=['POST'])
def api_listing_delete():
    data = request.json or {}
    goods_no = data.get('goods_no')
    
    queues = load_queues()
    if goods_no in queues['listing_queue']:
        del queues['listing_queue'][goods_no]
        save_queues(queues)
        return jsonify({'success': True})
    return jsonify({'success': False, 'msg': 'Item not found'})

@app.route('/api/listing/clear', methods=['POST'])
def api_listing_clear():
    queues = load_queues()
    queues['sourcing_queue'] = {}
    queues['listing_queue'] = {}
    save_queues(queues)
    return jsonify({'success': True})

@app.route('/api/export/shopee', methods=['POST'])
def api_export_shopee():
    queues = load_queues()
    listing = list(queues.get('listing_queue', {}).values())
    
    shopee_file = os.path.join(BASE_DIR, 'shopee_mass_upload.xlsx')
    success = export_to_shopee_excel(listing, shopee_file)
    
    if success:
        return send_file(shopee_file, as_attachment=True, download_name='shopee_mass_upload.xlsx')
    return make_response("Failed to generate template", 500)

@app.route('/api/export/shopify', methods=['POST'])
def api_export_shopify():
    queues = load_queues()
    listing = list(queues.get('listing_queue', {}).values())
    
    shopify_file = os.path.join(BASE_DIR, 'shopify_products.csv')
    success = export_to_shopify_csv(listing, shopify_file)
    
    if success:
        return send_file(shopify_file, as_attachment=True, download_name='shopify_products.csv')
    return make_response("Failed to generate template", 500)

@app.route('/api/recognize_product_image', methods=['POST'])
def api_recognize_product_image():
    api_key = request.form.get('api_key') or (request.json or {}).get('api_key')
    
    try:
        if 'image' in request.files:
            file = request.files['image']
            image_bytes = file.read()
            mime_type = file.mimetype or "image/jpeg"
        elif request.json and 'image_data' in request.json:
            data_uri = request.json.get('image_data', '')
            if ',' in data_uri:
                header, base64_str = data_uri.split(',', 1)
                mime_type = header.split(';')[0].split(':')[1]
                image_bytes = base64.b64decode(base64_str)
            else:
                return jsonify({'success': False, 'msg': '올바른 이미지 형식이 아닙니다.'})
        else:
            return jsonify({'success': False, 'msg': '업로드할 이미지 파일이 업습니다.'})
                
        result = recognize_product_from_image(image_bytes, mime_type=mime_type, api_key=api_key)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})

@app.route('/api/generate_image', methods=['POST'])
def api_generate_image():
    data = request.json or {}
    brand = data.get('brand', '')
    name = data.get('name', '')
    visual_description = data.get('visual_description', '')
    style = data.get('style', 'studio')
    api_key = data.get('api_key', '')
    
    try:
        image_url = generate_ai_product_image(brand, name, visual_description=visual_description, style=style, api_key=api_key)
        return jsonify({'success': True, 'image_url': image_url})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)

