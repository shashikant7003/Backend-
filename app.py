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
    
    # 🌐 Cobalt Public API Instance (Super Fast & Stable)
    cobalt_url = "https://api.cobalt.tools/"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": video_url,
        "videoQuality": "1080",  # Default best quality
        "filenamePattern": "basic"
    }
    
    try:
        # Cobalt API ko request bhej rahe hain
        response = requests.post(cobalt_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_data = response.json()
            # Cobalt direct download link 'url' parameter mein deta hai
            download_link = res_data.get('url')
            
            if download_link:
                return jsonify({'success': True, 'download_url': download_link})
        
        # Agar status 200 nahi hai ya link nahi mila
        return jsonify({'error': 'Cobalt API could not fetch stream. Try again.'}), 400
            
    except Exception as e:
        return jsonify({'error': f"Backend error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

