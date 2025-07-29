# TikTok Video Downloader

A production-ready TikTok video downloader web application built with Flask and yt-dlp. Download TikTok videos without watermarks in MP4 format or extract MP3 audio.

## Features

- 🎥 Download TikTok videos without watermark
- 🎵 Extract MP3 audio from TikTok videos
- 📱 Mobile-responsive design
- ⚡ Fast download with progress animation
- 🔗 Support for all TikTok URL formats
- 🚀 REST API endpoint for bot integration
- 🔍 SEO optimized with comprehensive meta tags

## Deployment on Render

### Quick Deploy

1. **Fork/Clone this repository**
2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Build Settings**:
   - **Build Command**: `pip install -r requirements_github.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
   - **Environment**: `Python 3`

4. **Environment Variables**:
   - `SESSION_SECRET`: Generate a random secret key
   - `PORT`: Auto-provided by Render
   - `DEBUG`: Set to `False` for production

### Manual Deployment

```bash
# Clone the repository
git clone https://github.com/armaanvirk002/Repo.git
cd Repo

# Install dependencies
pip install -r requirements_github.txt

# Run locally
python main.py
```

## File Structure

```
├── main.py              # Flask application
├── templates/
│   ├── index.html       # Main page
│   └── 404.html         # Error page
├── static/
│   ├── script.js        # Client-side JavaScript
│   ├── style.css        # Custom styles
│   └── logo.svg         # App logo
├── downloads/           # Temporary files (auto-cleanup)
├── requirements_github.txt  # Python dependencies
├── render.yaml          # Render configuration
├── Procfile            # Process configuration
├── robots.txt          # SEO robots file
└── sitemap.xml         # SEO sitemap

## API Usage

### Download Endpoint

```bash
POST /bot-download
Content-Type: application/json

{
  "url": "https://www.tiktok.com/@username/video/1234567890"
}
```

**Response:**
```json
{
  "video_url": "https://your-app.onrender.com/serve/filename.mp4",
  "audio_url": "https://your-app.onrender.com/serve/filename.mp3",
  "title": "Video Title",
  "author": "Username",
  "thumbnail": "https://thumbnail-url.jpg",
  "duration": 30,
  "success": true
}
```

## Supported URL Formats

- `https://www.tiktok.com/@user/video/123456789`
- `https://vm.tiktok.com/abc123`
- `https://vt.tiktok.com/abc123`
- `https://www.tiktok.com/t/abc123`
- And more TikTok URL variations

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `10000` |
| `SESSION_SECRET` | Flask secret key | Required |
| `DEBUG` | Debug mode | `False` |

## Production Features

- ✅ Gunicorn WSGI server
- ✅ Auto file cleanup (10 minutes)
- ✅ Error handling and logging
- ✅ Mobile-responsive UI
- ✅ SEO optimization
- ✅ REST API for bots
- ✅ CORS support

## License

MIT License

## Support

For issues and questions, please create an issue on GitHub.