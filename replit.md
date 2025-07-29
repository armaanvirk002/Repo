# TikTok Video Downloader

## Overview

This is a production-ready TikTok video downloader web application built with Flask and yt-dlp. The application allows users to download TikTok videos without watermarks in MP4 format or extract MP3 audio from TikTok videos. It features a responsive web interface optimized for both mobile and desktop users, along with a REST API endpoint for bot integration.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple Flask-based web architecture with the following key characteristics:

- **Frontend**: Server-side rendered HTML templates using Jinja2 with TailwindCSS for styling
- **Backend**: Flask web framework with Python
- **Video Processing**: yt-dlp library for downloading and processing TikTok videos
- **File Management**: Local file system with automatic cleanup using threading timers
- **Deployment**: Designed for cloud deployment (Render.com) with local development support

## Key Components

### Web Application (main.py)
- Flask application serving as the main entry point
- URL validation for TikTok links using regex patterns
- Video processing using yt-dlp library
- File management with automatic deletion after 10 minutes
- REST API endpoint (`/bot-download`) for programmatic access

### Frontend Templates
- **index.html**: Main landing page with URL input and download interface
- **404.html**: Custom error page for handling not found requests
- Responsive design using TailwindCSS framework
- Mobile-optimized interface with glass morphism effects

### Static Assets
- **script.js**: Client-side JavaScript for URL validation and clipboard functionality
- **style.css**: Custom CSS animations and styling enhancements
- Font Awesome icons for UI elements

### Configuration Files
- **robots.txt**: SEO optimization for search engine crawlers
- **README.md**: Documentation and deployment instructions

## Data Flow

1. **User Input**: User pastes or types a TikTok URL into the web interface
2. **URL Validation**: Client-side and server-side validation of TikTok URL format
3. **Video Processing**: yt-dlp downloads and processes the video
4. **File Storage**: Temporary files stored in `/downloads` directory
5. **User Download**: Files served to user via Flask send_file
6. **Cleanup**: Automatic file deletion after 10 minutes using threading timers

### API Flow (/bot-download)
1. POST request with TikTok URL
2. Video processing and metadata extraction
3. JSON response with download URLs, title, author, and thumbnail

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for Python
- **yt-dlp**: YouTube and TikTok video downloading library
- **TailwindCSS**: CSS framework via CDN
- **Font Awesome**: Icon library via CDN

### Python Standard Library
- **os**: File system operations and environment variables
- **threading**: Timer functionality for file cleanup
- **re**: Regular expressions for URL validation
- **json**: JSON response handling
- **urllib.parse**: URL parsing utilities
- **datetime**: Time-based operations

## Deployment Strategy

### Local Development
- Python application runs directly with `python main.py`
- Uses port 5000 by default with debug mode enabled
- File uploads stored in local `downloads` directory

### Production Deployment (Render.com)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Port Configuration**: Uses `PORT` environment variable or defaults to 10000
- **Host Configuration**: Binds to `0.0.0.0` for cloud deployment
- **Environment Variables**: 
  - `SESSION_SECRET`: Flask session encryption key
  - `PORT`: Application port (provided by Render)

### SEO and Performance Optimizations
- Enhanced SEO meta tags with optimized titles and descriptions
- OpenGraph and Twitter Card integration with proper image references
- Custom SVG logo for branding and social sharing
- Optimized for mobile and desktop performance
- Auto-cleanup prevents storage bloat
- Responsive design for all screen sizes
- Canonical URLs and proper favicon implementation

### Security Considerations
- URL validation prevents malicious input
- Session secret for Flask security
- Temporary file cleanup prevents disk space issues
- No user data persistence minimizes privacy concerns