import os
import logging
import threading
import time
import re
import json
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import yt_dlp
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

def is_valid_tiktok_url(url):
    """Validate if the URL is a valid TikTok URL"""
    tiktok_patterns = [
        r'https?://(?:www\.)?tiktok\.com/@[\w\.-]+/video/\d+',
        r'https?://(?:vm\.)?tiktok\.com/[\w\.-]+',
        r'https?://(?:vt\.)?tiktok\.com/[\w\.-]+',
        r'https?://(?:www\.)?tiktok\.com/t/[\w\.-]+',
        r'https?://m\.tiktok\.com/v/\d+\.html',
        r'https?://(?:www\.)?tiktok\.com/.*',
        r'https?://vm\.tiktok\.com/.*',
        r'https?://vt\.tiktok\.com/.*'
    ]
    
    for pattern in tiktok_patterns:
        if re.match(pattern, url):
            return True
    return False

def schedule_file_deletion(filepath, delay_minutes=10):
    """Schedule file deletion after specified minutes"""
    def delete_file():
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logging.info(f"Deleted file: {filepath}")
        except Exception as e:
            logging.error(f"Error deleting file {filepath}: {e}")
    
    timer = threading.Timer(delay_minutes * 60, delete_file)
    timer.start()
    logging.info(f"Scheduled deletion of {filepath} in {delay_minutes} minutes")

def get_video_info(url):
    """Extract video information using yt-dlp with multiple fallback strategies"""
    
    # Multiple configuration strategies to try
    strategies = [
        # Strategy 1: Full headers with cookies
        {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'referer': 'https://www.tiktok.com/',
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            },
            'cookiefile': None,
            'extractor_args': {
                'tiktok': {
                    'api_hostname': 'api.tiktokv.com'
                }
            }
        },
        # Strategy 2: Desktop Chrome with minimal headers
        {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
            'headers': {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        },
        # Strategy 3: Basic configuration
        {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    ]
    
    for i, ydl_opts in enumerate(strategies):
        try:
            logging.info(f"Trying extraction strategy {i+1}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    continue
                    
                logging.info(f"Strategy {i+1} successful")
                return {
                    'title': info.get('title', 'TikTok Video'),
                    'uploader': info.get('uploader', 'TikTok User'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0)
                }
        except Exception as e:
            logging.warning(f"Strategy {i+1} failed: {e}")
            continue
    
    logging.error("All extraction strategies failed")
    return None

def download_video(url, format_type='mp4'):
    """Download video using yt-dlp with multiple fallback strategies"""
    
    timestamp = str(int(time.time()))
    
    # Define base strategies for download
    base_strategies = [
        # Strategy 1: iPhone user agent
        {
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'referer': 'https://www.tiktok.com/',
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Sec-Fetch-Mode': 'navigate',
            },
            'extractor_args': {
                'tiktok': {
                    'api_hostname': 'api.tiktokv.com'
                }
            }
        },
        # Strategy 2: Desktop Chrome
        {
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
            'headers': {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        },
        # Strategy 3: Basic configuration
        {
            'quiet': True,
            'no_warnings': True,
        }
    ]
    
    for i, base_opts in enumerate(base_strategies):
        try:
            logging.info(f"Trying download strategy {i+1} for {format_type}")
            
            if format_type == 'mp4':
                filename = f"tiktok_video_{timestamp}.%(ext)s"
                ydl_opts = {
                    **base_opts,
                    'format': 'best[ext=mp4]/mp4/best',
                    'outtmpl': os.path.join(DOWNLOADS_DIR, filename),
                }
            else:  # mp3
                filename = f"tiktok_audio_{timestamp}.%(ext)s"
                ydl_opts = {
                    **base_opts,
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOADS_DIR, filename),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(DOWNLOADS_DIR):
                    if timestamp in file:
                        filepath = os.path.join(DOWNLOADS_DIR, file)
                        schedule_file_deletion(filepath)
                        logging.info(f"Download strategy {i+1} successful")
                        return filepath
                        
        except Exception as e:
            logging.warning(f"Download strategy {i+1} failed: {e}")
            continue
    
    logging.error(f"All download strategies failed for {format_type}")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_url():
    url = request.form.get('tiktok_url', '').strip()
    
    if not url:
        flash('Please enter a TikTok URL', 'error')
        return redirect(url_for('index'))
    
    if not is_valid_tiktok_url(url):
        flash('Please enter a valid TikTok URL', 'error')
        return redirect(url_for('index'))
    
    # Get video information
    video_info = get_video_info(url)
    if not video_info:
        # More detailed error message based on potential issues
        error_msg = 'Unable to process this TikTok video. This may be due to geographic restrictions, private video, or temporary service issues. Please try another video or wait a few moments.'
        flash(error_msg, 'error')
        return redirect(url_for('index'))
    
    return render_template('index.html', video_info=video_info, tiktok_url=url)

@app.route('/download/<format_type>')
def download(format_type):
    url = request.args.get('url')
    
    if not url or not is_valid_tiktok_url(url):
        return jsonify({'error': 'Invalid URL'}), 400
    
    if format_type not in ['mp4', 'mp3']:
        return jsonify({'error': 'Invalid format'}), 400
    
    filepath = download_video(url, format_type)
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': f'Failed to download {format_type.upper()}'}), 500
    
    filename = os.path.basename(filepath)
    # Create a more user-friendly filename
    clean_filename = f"tiktok_video.{format_type}" if format_type == 'mp4' else f"tiktok_audio.{format_type}"
    
    # Set proper MIME type and headers for direct download
    mimetype = 'video/mp4' if format_type == 'mp4' else 'audio/mpeg'
    
    response = send_file(
        filepath, 
        as_attachment=False,  # Don't force attachment, let JavaScript handle it
        download_name=clean_filename,
        mimetype=mimetype
    )
    
    # Add headers to support blob downloads
    response.headers['Content-Disposition'] = f'inline; filename="{clean_filename}"'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    
    return response

@app.route('/bot-download', methods=['POST'])
def bot_download():
    """API endpoint for bot downloads"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        
        if not is_valid_tiktok_url(url):
            return jsonify({'error': 'Invalid TikTok URL'}), 400
        
        # Get video information
        video_info = get_video_info(url)
        if not video_info:
            return jsonify({'error': 'Failed to extract video information'}), 500
        
        # Download both formats
        mp4_path = download_video(url, 'mp4')
        mp3_path = download_video(url, 'mp3')
        
        if not mp4_path or not mp3_path:
            return jsonify({'error': 'Failed to download video'}), 500
        
        # Generate download URLs (in production, these would be proper URLs)
        base_url = request.url_root.rstrip('/')
        mp4_filename = os.path.basename(mp4_path)
        mp3_filename = os.path.basename(mp3_path)
        
        return jsonify({
            'video_url': f"{base_url}/serve/{mp4_filename}",
            'audio_url': f"{base_url}/serve/{mp3_filename}",
            'title': video_info['title'],
            'author': video_info['uploader'],
            'thumbnail': video_info['thumbnail'],
            'duration': video_info['duration'],
            'success': True
        })
        
    except Exception as e:
        logging.error(f"Bot download error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/serve/<filename>')
def serve_file(filename):
    """Serve downloaded files"""
    filepath = os.path.join(DOWNLOADS_DIR, filename)
    if os.path.exists(filepath):
        # Determine file type and set appropriate filename
        if filename.endswith('.mp4'):
            clean_filename = "tiktok_video.mp4"
        elif filename.endswith('.mp3'):
            clean_filename = "tiktok_audio.mp3"
        else:
            clean_filename = filename
            
        return send_file(
            filepath, 
            as_attachment=True, 
            download_name=clean_filename,
            mimetype='application/octet-stream'
        )
    else:
        return "File not found", 404

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/robots.txt')
def robots():
    return send_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_file('sitemap.xml')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Default to Render's port
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'  # Production default
    app.run(host='0.0.0.0', port=port, debug=debug)
