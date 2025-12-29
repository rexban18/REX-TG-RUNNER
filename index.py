from flask import Flask, request, jsonify
import requests
import json
import os
from urllib.parse import quote

app = Flask(__name__)

# --- API Keys (Environment variables se) ---
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "5d674a828b8a56d044729dd5e1efd7a214071bdf")

# API URLs
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FLUX_IMAGE_URL = "https://text2img.hideme.eu.org/image"
SERPER_URL = "https://google.serper.dev/search"

@app.route('/')
def home():
    return jsonify({
        "message": "Prime API hosted on Vercel",
        "status": "active",
        "endpoints": {
            "/api/llama": "Llama 3.3 Model",
            "/api/deepseek": "DeepSeek R1 Model",
            "/api/gpt-oss": "GPT OSS 120B",
            "/api/search": "Google Search",
            "/api/image": "Generate Images",
            "/api/domain": "Domain Analysis"
        },
        "docs": "Use /api/{endpoint}?param=value"
    })

# AI Endpoints
@app.route('/api/llama', methods=['GET'])
def ai_llama():
    message = request.args.get('message', '')
    if not message:
        return jsonify({"error": "Missing 'message' parameter"}), 400
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": message}]
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]
            return jsonify({
                "status": "success",
                "model": "llama-3.3-70b",
                "message": message,
                "reply": reply
            })
        return jsonify({"error": "No response"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/deepseek', methods=['GET'])
def ai_deepseek():
    message = request.args.get('message', '')
    if not message:
        return jsonify({"error": "Missing 'message' parameter"}), 400
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [{"role": "user", "content": message}],
        "reasoning": {"enabled": True}
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if "choices" in data:
            reply_data = data["choices"][0]["message"]
            result = {
                "status": "success",
                "model": "deepseek-r1",
                "message": message,
                "reply": reply_data.get("content", "")
            }
            if "reasoning_details" in reply_data:
                result["reasoning"] = reply_data["reasoning_details"]
            return jsonify(result)
        return jsonify({"error": "No response"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/gpt-oss', methods=['GET'])
def ai_gpt_oss():
    message = request.args.get('message', '')
    if not message:
        return jsonify({"error": "Missing 'message' parameter"}), 400
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-oss-120b:free",
        "messages": [{"role": "user", "content": message}],
        "reasoning": {"enabled": True}
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if "choices" in data:
            reply_data = data["choices"][0]["message"]
            result = {
                "status": "success",
                "model": "gpt-oss-120b",
                "message": message,
                "reply": reply_data.get("content", "")
            }
            if "reasoning_details" in reply_data:
                result["reasoning"] = reply_data["reasoning_details"]
            return jsonify(result)
        return jsonify({"error": "No response"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Search Endpoint
@app.route('/api/search', methods=['GET'])
def google_search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {"q": query, "num": 10}
    
    try:
        response = requests.post(SERPER_URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        results = []
        if "organic" in data:
            for item in data["organic"][:10]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
        
        return jsonify({
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Image Generation
@app.route('/api/image', methods=['GET'])
def generate_image():
    prompt = request.args.get('prompt', '')
    if not prompt:
        return jsonify({"error": "Missing 'prompt' parameter"}), 400
    
    try:
        encoded_prompt = quote(prompt)
        url = f"{FLUX_IMAGE_URL}?prompt={encoded_prompt}&model=flux"
        
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            # Return direct image URL
            return jsonify({
                "status": "success",
                "prompt": prompt,
                "image_url": url,
                "direct_download": url
            })
        else:
            return jsonify({"error": "Failed to generate image"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Domain Analysis (Simplified for Vercel)
@app.route('/api/domain', methods=['GET'])
def domain_analysis():
    domain = request.args.get('domain', '')
    if not domain:
        return jsonify({"error": "Missing 'domain' parameter"}), 400
    
    try:
        import socket
        
        # Clean domain
        if domain.startswith(('http://', 'https://')):
            domain = domain.split("//")[1]
        domain = domain.split("/")[0].split(":")[0]
        
        # Get IP
        ip = socket.gethostbyname(domain)
        
        # Get subdomains (simple version)
        subdomains = []
        try:
            import requests as req
            crt_url = f"https://crt.sh/?q=%25.{domain}&output=json"
            crt_response = req.get(crt_url, timeout=10)
            if crt_response.status_code == 200:
                found = set()
                for entry in crt_response.json()[:50]:  # Limit
                    name = entry.get('name_value', '')
                    for sub in name.split("\n"):
                        if domain in sub:
                            found.add(sub.strip())
                subdomains = sorted(list(found))[:15]
        except:
            subdomains = ["Error fetching"]
        
        return jsonify({
            "status": "success",
            "domain": domain,
            "ip": ip,
            "subdomains": subdomains,
            "subdomain_count": len(subdomains)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel ke liye required
if __name__ == '__main__':
    app.run(debug=False)