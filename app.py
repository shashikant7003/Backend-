import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/get-download-link', methods=['POST'])
def get_download_link():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL missing'}), 400
        
    video_url = data['url']
    
    # 🌐 Alternate Fresh Cobalt API Instance (Bypasses the main api.cobalt.tools block)
    cobalt_url = "https://cobalt.xyz/api/json"  # Ya phir "https://co.wuk.sh/api/json" 
    
    # Agar direct endpoint work na kare, toh alternative backend check karte hain:
    # Hum standard sub-endpoint choose kar rahe hain jo dynamic processing karega
    fallback_url = "https://api.cobalt.tools/" 
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "url": video_url,
        "videoQuality": "720",  # 720p is highly stable for instant streaming/download
        "filenamePattern": "basic"
    }
    
    try:
        # Pehle active mirror test karte hain
        response = requests.post("https://co.wuk.sh/api/json", json=payload, headers=headers, timeout=12)
        
        # Agar pehla mirror load na le, toh alternate official proxy trigger karein
        if response.status_code != 200:
            response = requests.post(fallback_url, json=payload, headers=headers, timeout=12)
            
        if response.status_code == 200:
            res_data = response.json()
            download_link = res_data.get('url')
            
            if download_link:
                return jsonify({'success': True, 'download_url': download_link})
        
        # Details error capture mapping
        try:
            err_detail = response.json().get('text', 'API limit reached')
        except:
            err_detail = f"Status Code {response.status_code}"
            
        return jsonify({'error': f"Cobalt Proxy Error ({err_detail}). Please retry."}), 400
            
    except Exception as e:
        return jsonify({'error': f"Backend Engine Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
