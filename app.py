"""AI Commerce & Creative Studio — independent portfolio prototype.

Shopify endpoints are local mock endpoints. No live Shopify store is contacted.
"""
from __future__ import annotations

import json
import os
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
from shopify_admin import configured as shopify_live_configured, products as live_shopify_products, ShopifyError

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
DB_PATH = Path(os.getenv("DATABASE_PATH", BASE / "studio.db"))
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False

PRODUCTS = [
    {"id":"sofa-01","handle":"serein-modular-sofa","title":"Serein Modular Sofa","category":"Seating","price":12800,"compare_at":14600,"variants":[{"id":"sand","label":"Oat boucle","swatch":"#c7bca8"},{"id":"clay","label":"Burnt clay","swatch":"#9b6655"}],"description":"Deep, generous proportions and a softly sculpted silhouette, designed to settle naturally into the room.","image":"https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=1100&q=85","image_credit":"Sven Brandsma / Unsplash","tags":["modular","living room","new arrival"],"featured":True},
    {"id":"chair-02","handle":"forma-lounge-chair","title":"Forma Lounge Chair","category":"Seating","price":4650,"compare_at":None,"variants":[{"id":"oak","label":"Natural oak","swatch":"#a58b6a"},{"id":"walnut","label":"Smoked walnut","swatch":"#614b3c"}],"description":"A low, relaxed chair with a considered frame and textured upholstery.","image":"https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=1100&q=85","image_credit":"Unsplash contributor","tags":["chair","oak","living room"],"featured":True},
    {"id":"table-03","handle":"arc-dining-table","title":"Arc Dining Table","category":"Tables","price":8900,"compare_at":None,"variants":[{"id":"oak","label":"European oak","swatch":"#b69b76"},{"id":"ash","label":"Smoked ash","swatch":"#6d5a49"}],"description":"A quietly architectural dining table with softened edges and a generous top.","image":"https://images.unsplash.com/photo-1617806118233-18e1de247200?auto=format&fit=crop&w=1100&q=85","image_credit":"Unsplash contributor","tags":["dining","oak","tables"],"featured":True},
    {"id":"lamp-04","handle":"ora-pendant-light","title":"Ora Pendant Light","category":"Lighting","price":2150,"compare_at":None,"variants":[{"id":"ivory","label":"Ivory","swatch":"#e8dfcf"},{"id":"bronze","label":"Aged bronze","swatch":"#76604c"}],"description":"A warm, diffused glow shaped by a hand-finished shade.","image":"https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1100&q=85","image_credit":"Unsplash contributor","tags":["lighting","pendant","warm light"],"featured":True},
    {"id":"mirror-05","handle":"still-arch-mirror","title":"Still Arch Mirror","category":"Decor","price":1790,"compare_at":None,"variants":[{"id":"brass","label":"Brushed brass","swatch":"#b99a66"},{"id":"black","label":"Soft black","swatch":"#323330"}],"description":"A slender arched mirror that brings depth and a little more light.","image":"https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1100&q=85","image_credit":"Unsplash contributor","tags":["mirror","hallway","decor"],"featured":False},
    {"id":"rug-06","handle":"tide-wool-rug","title":"Tide Wool Rug","category":"Textiles","price":3200,"compare_at":None,"variants":[{"id":"natural","label":"Natural / 200 × 300","swatch":"#d3c8b5"},{"id":"stone","label":"Stone / 200 × 300","swatch":"#aaa99f"}],"description":"A tactile, hand-loomed ground with a subtle tonal rhythm.","image":"https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1100&q=85","image_credit":"Unsplash contributor","tags":["rug","wool","textiles"],"featured":False},
    {"id":"vase-07","handle":"form-study-vessel","title":"Form Study Vessel","category":"Objects","price":640,"compare_at":None,"variants":[{"id":"chalk","label":"Chalk","swatch":"#e5dece"},{"id":"umber","label":"Umber","swatch":"#786250"}],"description":"A sculptural stoneware object, made to hold a branch or stand on its own.","image":"https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=1100&q=85","image_credit":"Unsplash contributor","tags":["ceramic","vessel","object"],"featured":False},
    {"id":"side-08","handle":"line-side-table","title":"Line Side Table","category":"Tables","price":2450,"compare_at":None,"variants":[{"id":"oak","label":"Natural oak","swatch":"#b69b76"},{"id":"black","label":"Ebonised oak","swatch":"#393a35"}],"description":"A useful, light-footed table for the quiet space beside a reading chair.","image":"https://images.unsplash.com/photo-1499933374294-4584851497cc?auto=format&fit=crop&w=1100&q=85","image_credit":"Unsplash contributor","tags":["side table","oak","living room"],"featured":False},
]

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY, data TEXT NOT NULL, stock INTEGER NOT NULL DEFAULT 12, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, items TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL DEFAULT 'demo-confirmed', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS campaigns(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, objective TEXT DEFAULT '', audience TEXT DEFAULT '', product TEXT DEFAULT '', platform TEXT DEFAULT 'Instagram', copy TEXT DEFAULT '{}', creative_ids TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'Draft', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS designs(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, format TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS automation_history(id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS contact_messages(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL);
        """)
        columns={row["name"] for row in con.execute("PRAGMA table_info(campaigns)").fetchall()}
        if "creative_ids" not in columns: con.execute("ALTER TABLE campaigns ADD COLUMN creative_ids TEXT NOT NULL DEFAULT '[]'")
        for product in PRODUCTS:
            con.execute("INSERT OR IGNORE INTO products(id,data,stock,updated_at) VALUES(?,?,?,?)", (product["id"], json.dumps(product), 12, now()))
        if con.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0] == 0:
            stamp=now(); copy={"headline":"Designed for living.","caption":"A quieter point of view on the pieces we live with. Explore the AURA LIVING autumn edit.","cta":"Discover the collection"}
            con.execute("INSERT INTO campaigns(name,objective,audience,product,platform,copy,creative_ids,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",("Designed for Living","Introduce the fictional autumn collection","Design-conscious homeowners","Serein Modular Sofa","Instagram",json.dumps(copy),"[]","Draft",stamp,stamp))

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def err(message, code=400): return jsonify({"error":message}), code

@app.get("/")
def index(): return send_from_directory(BASE / "static", "index.html")

@app.get("/api/health")
def health(): return jsonify({"ok":True,"project":"AI Commerce & Creative Studio","mode":"independent prototype","shopify":"connected" if shopify_live_configured() else "demo only","ai":"live" if os.getenv("OPENAI_API_KEY") else "demo copy mode"})

@app.get("/api/shopify/live/status")
def live_shopify_status():
    return jsonify({"configured":shopify_live_configured(),"mode":"live Admin API available" if shopify_live_configured() else "SQLite demo mode","api_version":"2026-07","message":"Read-only product query; credentials are server-side." if shopify_live_configured() else "Add the Shopify client ID, client secret, and store domain in the server environment to connect."})

@app.get("/api/shopify/live/products")
def live_shopify_product_list():
    if not shopify_live_configured(): return err("Live Shopify is not configured. Demo catalogue remains available at /api/shopify/products.",503)
    try:
        items=live_shopify_products(request.args.get("first",12,type=int))
    except ShopifyError as exc:
        return err(str(exc),502)
    # Return only storefront-safe product fields; never expose Admin credentials or customer/order data.
    safe=[]
    for item in items:
        safe.append({"id":item.get("id"),"title":item.get("title"),"handle":item.get("handle"),"status":item.get("status"),"product_type":item.get("productType"),"image":item.get("featuredImage"),"variants":item.get("variants",{}).get("nodes",[])})
    return jsonify({"products":safe,"count":len(safe),"source":"Shopify Admin GraphQL API"})

@app.get("/api/shopify/products")
def get_products():
    q=request.args.get("q","").strip().lower(); category=request.args.get("category",""); sort=request.args.get("sort","featured")
    with db() as con: rows=con.execute("SELECT data,stock FROM products").fetchall()
    items=[]
    for row in rows:
        item=json.loads(row["data"]); item["inventory_quantity"]=row["stock"]
        if q and q not in (item["title"]+" "+item["category"]+" "+" ".join(item["tags"])).lower(): continue
        if category and category != "All" and item["category"] != category: continue
        items.append(item)
    if sort=="price-low": items.sort(key=lambda p:p["price"])
    elif sort=="price-high": items.sort(key=lambda p:-p["price"])
    elif sort=="title": items.sort(key=lambda p:p["title"])
    return jsonify({"products":items,"count":len(items),"source":"SQLite demo catalogue"})

@app.get("/api/shopify/collections")
def get_collections():
    with db() as con: rows=con.execute("SELECT data FROM products").fetchall()
    grouped={}
    for row in rows:
        p=json.loads(row["data"]); grouped.setdefault(p["category"],[]).append({"id":p["id"],"title":p["title"],"handle":p["handle"],"price":p["price"],"image":p["image"]})
    return jsonify({"collections":[{"title":name,"handle":name.lower().replace(" ","-"),"products":items,"count":len(items)} for name,items in grouped.items()],"source":"Derived local collections"})

@app.get("/api/shopify/inventory")
def get_inventory():
    with db() as con: rows=con.execute("SELECT id,data,stock,updated_at FROM products ORDER BY id").fetchall()
    return jsonify({"inventory":[{"product_id":r["id"],"title":json.loads(r["data"])["title"],"available":r["stock"],"updated_at":r["updated_at"]} for r in rows],"source":"SQLite demo inventory"})

@app.get("/api/shopify/orders")
def get_orders():
    with db() as con: rows=con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify({"orders":[{**dict(r),"items":json.loads(r["items"])} for r in rows],"source":"Local demo orders"})

@app.get("/api/shopify/customers")
def get_customers():
    with db() as con: rows=con.execute("SELECT email,COUNT(*) order_count,COALESCE(SUM(total),0) demo_total,MAX(created_at) last_order FROM orders GROUP BY email ORDER BY last_order DESC").fetchall()
    return jsonify({"customers":[dict(r) for r in rows],"source":"Derived from local demo orders; no Shopify customer sync"})

@app.post("/api/shopify/products")
def create_product():
    data=request.get_json(silent=True) or {}; required=["title","category","price","description"]
    if any(not data.get(k) for k in required): return err("title, category, price, and description are required")
    data.update({"id":data.get("id") or "custom-"+str(int(datetime.now().timestamp())),"handle":data.get("handle") or data["title"].lower().replace(" ","-"),"variants":data.get("variants") or [{"id":"default","label":"Default","swatch":"#c7bca8"}],"tags":data.get("tags") or [],"image":data.get("image") or "","featured":False})
    with db() as con: con.execute("INSERT INTO products(id,data,stock,updated_at) VALUES(?,?,?,?)",(data["id"],json.dumps(data),int(data.get("inventory_quantity",0)),now()))
    return jsonify({"product":data,"source":"SQLite demo catalogue"}),201

@app.patch("/api/shopify/inventory/<product_id>")
def update_inventory(product_id):
    data=request.get_json(silent=True) or {}
    try: stock=max(0,int(data["available"]))
    except (KeyError,TypeError,ValueError): return err("available must be a non-negative integer")
    with db() as con: cur=con.execute("UPDATE products SET stock=?,updated_at=? WHERE id=?",(stock,now(),product_id))
    if not cur.rowcount:return err("Product not found",404)
    return jsonify({"product_id":product_id,"available":stock,"source":"SQLite demo inventory"})

@app.post("/api/shopify/sync")
def sync(): return jsonify({"ok":True,"mode":"mock","message":"Demo catalogue sync completed locally. Configure SHOPIFY_STORE_DOMAIN and SHOPIFY_ADMIN_ACCESS_TOKEN to implement a live Admin API adapter.","synced":len(PRODUCTS),"at":now()})

@app.post("/api/shopify/webhook")
def webhook():
    payload=request.get_json(silent=True) or {}
    with db() as con: con.execute("INSERT INTO automation_history(event,detail,created_at) VALUES(?,?,?)",("Mock Shopify webhook",json.dumps(payload)[:2000],now()))
    return jsonify({"received":True,"verified":False,"note":"Local demo only: HMAC verification must be implemented before accepting live Shopify webhooks."}),202

@app.post("/api/shopify/orders")
def create_order():
    data=request.get_json(silent=True) or {}; items=data.get("items",[])
    if not items: return err("Your demo cart is empty")
    total=0; normalized=[]
    with db() as con:
        for line in items:
            row=con.execute("SELECT data,stock FROM products WHERE id=?",(str(line.get("product_id")),)).fetchone()
            if not row: return err("A product in your cart is unavailable",404)
            product=json.loads(row["data"]); qty=max(1,min(20,int(line.get("quantity",1))))
            if row["stock"] < qty: return err(f"Only {row['stock']} available for {product['title']}",409)
            total += product["price"]*qty; normalized.append({"product_id":product["id"],"title":product["title"],"quantity":qty,"unit_price":product["price"],"variant":line.get("variant","Default")})
        cur=con.execute("INSERT INTO orders(email,items,total,status,created_at) VALUES(?,?,?,?,?)",(data.get("email","demo@example.com"),json.dumps(normalized),total,"demo-confirmed",now()))
        for line in normalized: con.execute("UPDATE products SET stock=stock-?,updated_at=? WHERE id=?",(line["quantity"],now(),line["product_id"]))
        order_id=cur.lastrowid
    return jsonify({"order":{"id":order_id,"items":normalized,"total":total,"currency":"AED","status":"demo-confirmed","created_at":now()},"note":"Checkout simulation only. No payment was taken."}),201

@app.post("/api/creative/generate")
def generate_copy():
    data=request.get_json(silent=True) or {}; product=data.get("product","Serein Modular Sofa"); campaign=data.get("campaign","Designed for Living"); audience=data.get("audience","Design-conscious homeowners"); platform=data.get("platform","Instagram"); style=data.get("style","Editorial"); mood=data.get("mood","Quiet confidence"); lighting=data.get("lighting","Soft afternoon light"); background=data.get("background","Warm contemporary interior"); composition=data.get("composition","Room-led, product in context"); aspect=data.get("aspect","4:5 portrait")
    prompt=f"Commercial product photograph for fictional AURA LIVING. Feature {product} in a {background}. Direction: {style}, {mood}. Lighting: {lighting}. Composition: {composition}. Aspect ratio: {aspect}. Campaign: {campaign}. Material fidelity, believable scale, natural shadows, refined art direction, realistic photography. No text, logos, watermark, extra furniture, or distorted details."
    result={"headline":"A softer way to come home.","description":f"Meet {product}: considered proportions, tactile materials, and the comfort of a room made your own.","caption":f"{campaign}, shaped around the things that make a space feel like home. Discover {product} at AURA LIVING.","cta":"Discover the collection","hashtags":["#AuraLiving","#DesignedForLiving","#ConsideredInteriors","#HomeWithIntention"],"seo":f"Explore {product} by AURA LIVING. Thoughtful home decor and furniture for a more considered space.","image_prompt":prompt,"mode":"demo copy mode"}
    key=os.getenv("OPENAI_API_KEY")
    if key:
        body={"model":os.getenv("OPENAI_TEXT_MODEL","gpt-4o-mini"),"temperature":0.75,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":"You are a concise luxury home-decor ecommerce creative. Return valid JSON only with keys headline, description, caption, cta, hashtags (array), seo. Avoid unverifiable claims."},{"role":"user","content":json.dumps({"product":product,"campaign":campaign,"audience":audience,"platform":platform,"style":style,"mood":mood})}]}
        req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=25) as res: content=json.loads(res.read())["choices"][0]["message"]["content"]
            result.update(json.loads(content)); result["image_prompt"]=prompt; result["mode"]="OpenAI text API"
        except (urllib.error.URLError, KeyError, ValueError, TimeoutError) as ex:
            app.logger.warning("OpenAI copy request failed: %s",ex); result["mode"]="demo copy fallback (AI request unavailable)"
    return jsonify(result)

@app.post("/api/creative/image")
def generate_image():
    if not os.getenv("OPENAI_API_KEY"): return err("Image API is not configured. Demo mode creates a prompt only; upload your own licensed image to design with it.",501)
    data=request.get_json(silent=True) or {}; prompt=data.get("prompt","")
    if not prompt: return err("prompt is required")
    if data.get("variation"): prompt += " Create a fresh variation of this visual direction; retain the same product and campaign identity, but vary framing, crop, and secondary styling details."
    body={"model":os.getenv("OPENAI_IMAGE_MODEL","gpt-image-1"),"prompt":prompt,"size":"1024x1024","quality":"medium"}
    req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+os.getenv("OPENAI_API_KEY"),"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as res: data=json.loads(res.read())["data"][0]
        return jsonify({"image":data.get("b64_json"),"url":data.get("url"),"mode":"OpenAI image API","revised_prompt":data.get("revised_prompt",prompt)})
    except (urllib.error.URLError,KeyError,ValueError,TimeoutError) as ex: app.logger.exception("Image API request failed"); return err("Image API request failed. Check server logs and API account availability.",502)

@app.get("/api/campaigns")
def get_campaigns():
    with db() as con: rows=con.execute("SELECT * FROM campaigns ORDER BY updated_at DESC").fetchall()
    return jsonify({"campaigns":[{**dict(r),"copy":json.loads(r["copy"]),"creative_ids":json.loads(r["creative_ids"])} for r in rows]})

@app.post("/api/campaigns")
def save_campaign():
    d=request.get_json(silent=True) or {}; name=d.get("name","").strip()
    if not name:return err("Campaign name is required")
    stamp=now(); status=d.get("status","Draft")
    if status not in ["Draft","In Review","Approved","Published"]: return err("Invalid campaign status")
    with db() as con:
        if d.get("id"):
            con.execute("UPDATE campaigns SET name=?,objective=?,audience=?,product=?,platform=?,copy=?,creative_ids=?,status=?,updated_at=? WHERE id=?",(name,d.get("objective",""),d.get("audience",""),d.get("product",""),d.get("platform","Instagram"),json.dumps(d.get("copy",{})),json.dumps(d.get("creative_ids",[])),status,stamp,d["id"]))
            row=con.execute("SELECT * FROM campaigns WHERE id=?",(d["id"],)).fetchone()
        else:
            cur=con.execute("INSERT INTO campaigns(name,objective,audience,product,platform,copy,creative_ids,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(name,d.get("objective",""),d.get("audience",""),d.get("product",""),d.get("platform","Instagram"),json.dumps(d.get("copy",{})),json.dumps(d.get("creative_ids",[])),status,stamp,stamp)); row=con.execute("SELECT * FROM campaigns WHERE id=?",(cur.lastrowid,)).fetchone()
    return jsonify({"campaign":{**dict(row),"copy":json.loads(row["copy"]),"creative_ids":json.loads(row["creative_ids"] )}}),201

@app.post("/api/campaigns/<int:campaign_id>/creatives")
def attach_creative(campaign_id):
    data=request.get_json(silent=True) or {}
    try: creative_id=int(data["design_id"])
    except (KeyError,TypeError,ValueError): return err("design_id must be an integer")
    with db() as con:
        campaign=con.execute("SELECT creative_ids FROM campaigns WHERE id=?",(campaign_id,)).fetchone()
        design=con.execute("SELECT id FROM designs WHERE id=?",(creative_id,)).fetchone()
        if not campaign:return err("Campaign not found",404)
        if not design:return err("Saved creative not found",404)
        ids=json.loads(campaign["creative_ids"])
        if creative_id not in ids: ids.append(creative_id)
        con.execute("UPDATE campaigns SET creative_ids=?,updated_at=? WHERE id=?",(json.dumps(ids),now(),campaign_id))
    return jsonify({"campaign_id":campaign_id,"creative_ids":ids})

@app.delete("/api/campaigns/<int:campaign_id>")
def delete_campaign(campaign_id):
    with db() as con: cur=con.execute("DELETE FROM campaigns WHERE id=?",(campaign_id,))
    if not cur.rowcount:return err("Campaign not found",404)
    return jsonify({"deleted":True})

@app.get("/api/designs")
def get_designs():
    with db() as con: rows=con.execute("SELECT * FROM designs ORDER BY id DESC").fetchall()
    return jsonify({"designs":[{**dict(r),"payload":json.loads(r["payload"])} for r in rows]})

@app.post("/api/designs")
def save_design():
    d=request.get_json(silent=True) or {}
    if not d.get("name") or not d.get("payload"):return err("name and payload are required")
    with db() as con: cur=con.execute("INSERT INTO designs(name,format,payload,created_at) VALUES(?,?,?,?)",(d["name"],d.get("format","Instagram Post"),json.dumps(d["payload"]),now()))
    return jsonify({"id":cur.lastrowid,"name":d["name"],"format":d.get("format","Instagram Post")}),201

@app.delete("/api/designs/<int:design_id>")
def delete_design(design_id):
    with db() as con:
        cur=con.execute("DELETE FROM designs WHERE id=?",(design_id,))
        if cur.rowcount:
            for row in con.execute("SELECT id,creative_ids FROM campaigns").fetchall():
                ids=json.loads(row["creative_ids"])
                if design_id in ids: con.execute("UPDATE campaigns SET creative_ids=?,updated_at=? WHERE id=?",(json.dumps([x for x in ids if x!=design_id]),now(),row["id"]))
    if not cur.rowcount:return err("Design not found",404)
    return jsonify({"deleted":True})

@app.get("/api/analytics")
def analytics():
    with db() as con:
        orders=con.execute("SELECT COUNT(*) n,COALESCE(SUM(total),0) revenue FROM orders").fetchone(); campaigns=con.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]; designs=con.execute("SELECT COUNT(*) FROM designs").fetchone()[0]
        top=con.execute("SELECT data,stock FROM products ORDER BY stock ASC LIMIT 4").fetchall()
    return jsonify({"label":"Demo / Simulated Data","revenue_aed":orders["revenue"],"orders":orders["n"],"conversion_rate":2.7,"average_order_value":orders["revenue"]/orders["n"] if orders["n"] else 0,"product_views":1842,"campaigns":campaigns,"saved_creatives":designs,"top_products":[{"title":json.loads(r["data"])["title"],"stock":r["stock"]} for r in top],"campaign_performance":[{"name":"Designed for Living","reach":12400,"engagement_rate":3.8},{"name":"The Quiet Edit","reach":8900,"engagement_rate":4.1}],"creative_performance":[{"name":"Serein — room-led","click_rate":2.4},{"name":"Ora — detail crop","click_rate":1.9}]})

@app.post("/api/automations/run")
def run_automation():
    d=request.get_json(silent=True) or {}; event=d.get("event","Generate campaign copy")
    messages={"Generate product description":"Product description drafted in demo mode.","Generate SEO copy":"SEO description prepared from catalogue data.","Generate social caption":"Social caption created using the copy workflow.","Create campaign variations":"Campaign variation set prepared. Review before use.","Low-stock check":"Inventory checked against the demo threshold of 4 units.","Prepare publishing assets":"Publishing checklist prepared. Nothing was published."}
    detail=messages.get(event,"Demo automation step recorded. No external action was taken.")
    with db() as con: cur=con.execute("INSERT INTO automation_history(event,detail,created_at) VALUES(?,?,?)",(event,detail,now())); row=con.execute("SELECT * FROM automation_history WHERE id=?",(cur.lastrowid,)).fetchone()
    return jsonify(dict(row)),201

@app.post("/api/contact")
def contact_message():
    d=request.get_json(silent=True) or {}; name=str(d.get("name","")).strip(); email=str(d.get("email","")).strip(); message=str(d.get("message","")).strip()
    if not name or not email or "@" not in email or not message:return err("Name, valid email, and message are required")
    if len(message)>4000:return err("Message must be 4,000 characters or fewer")
    with db() as con: cur=con.execute("INSERT INTO contact_messages(name,email,message,created_at) VALUES(?,?,?,?)",(name,email,message,now()))
    return jsonify({"received":True,"id":cur.lastrowid,"note":"Stored locally for this portfolio demo. No email was sent."}),201

@app.get("/api/automations/history")
def automation_history():
    with db() as con: rows=con.execute("SELECT * FROM automation_history ORDER BY id DESC LIMIT 30").fetchall()
    return jsonify({"history":[dict(r) for r in rows]})

@app.get("/api/docs/shopify")
def shopify_docs():
    return jsonify({"mode":"local demo plus optional live product reader","base_url":"/api/shopify","endpoints":["GET /products","POST /products","GET /collections","GET /inventory","PATCH /inventory/<product_id>","GET /orders","POST /orders","GET /customers","POST /sync","POST /webhook"],"live_endpoints":["GET /api/shopify/live/status","GET /api/shopify/live/products"],"live_setup":{"SHOPIFY_STORE_DOMAIN":"your-store.myshopify.com","SHOPIFY_CLIENT_ID":"server only","SHOPIFY_CLIENT_SECRET":"server only"},"note":"Local commerce endpoints use SQLite simulation. The optional Shopify Admin GraphQL adapter reads products only and requires a store-owner client-credentials grant. Live orders, customers, checkout and webhooks are not connected."})

init_db()
if __name__ == "__main__": app.run(host=os.getenv("HOST","127.0.0.1"),port=int(os.getenv("PORT","5000")),debug=os.getenv("FLASK_DEBUG")=="1")
