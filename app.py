

import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS  # Frontend se connect karne ke liye zaroori hai

app = Flask(__name__)
CORS(app)  # Yeh alag frontend ko access allow karega

def extract_video_id(url):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "shorts/" in url:
        return url.split("shorts/")[1].split("?")[0]
    return None

@app.route('/api/get-download-link', methods=['POST'])
def get_download_link():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL missing'}), 400
        
    video_url = data['url']
    video_id = extract_video_id(video_url)
    
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
        
    # Piped API to bypass block
    piped_api_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
    
    try:
        response = requests.get(piped_api_url, timeout=12)
        api_data = response.json()
        
        video_streams = api_data.get('videoStreams', [])
        download_link = None
        
        # Combined stream (Video + Audio) dhundna
        for stream in video_streams:
            if stream.get('videoOnly') is False:
                download_link = stream.get('url')
                break
                
        if not download_link and video_streams:
            download_link = video_streams[0].get('url')
            
        if download_link:
            return jsonify({'success': True, 'download_url': download_link})
        else:
            return jsonify({'error': 'No downloadable stream found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
