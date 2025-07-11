import streamlit as st
import yt_dlp
import os
import ssl
import certifi
import base64
from urllib.parse import urlparse

# =============================================
# SSL Configuration
# =============================================
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['SSL_CERT_FILE'] = certifi.where()

# =============================================
# Background Styling
# =============================================
def set_background_with_blur(image_file=None, image_url=None, blur_px=5):
    """
    Set a blurred background image for the app
    """
    if image_file:
        img_bytes = image_file.read()
        encoded = base64.b64encode(img_bytes).decode()
        image_uri = f"data:image/jpeg;base64,{encoded}"
    elif image_url:
        # Validate URL format
        try:
            result = urlparse(image_url)
            if all([result.scheme, result.netloc]):
                image_uri = image_url
            else:
                raise ValueError("Invalid URL")
        except:
            image_uri = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
    else:
        image_uri = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"

    st.markdown(
        f"""
        <style>
        .bg-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: url("{image_uri}");
            background-size: cover;
            background-position: center;
            filter: blur({blur_px}px);
            z-index: -1;
        }}
        .content-container {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 10px;
            margin-top: 2rem;
        }}
        .stApp {{
            background: transparent;
        }}
        </style>
        <div class="bg-container"></div>
        """,
        unsafe_allow_html=True
    )

# =============================================
# Downloader Function
# =============================================
def download_video_audio(url, download_type):
    """
    Download video or audio using yt-dlp
    Returns (filename, error_message)
    """
    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'MP3' else 'bestvideo+bestaudio/best',
        'ffmpeg_location': 'ffmpeg',  # Will use system PATH
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,  # Show progress
        'no_warnings': False,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    if download_type == 'MP3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Validate URL first
            info = ydl.extract_info(url, download=False)
            if not info:
                return None, "Could not extract video information"
            
            # Proceed with download
            ydl.download([url])
            filename = ydl.prepare_filename(info)
            
            if download_type == 'MP3':
                filename = os.path.splitext(filename)[0] + ".mp3"
                if not os.path.exists(filename):
                    return None, "MP3 conversion failed"
            
            return filename, None
            
    except yt_dlp.utils.DownloadError as e:
        return None, f"Download error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# =============================================
# Main App
# =============================================
def main():
    # Sidebar Configuration
    st.sidebar.header("🎨 Background Settings")
    bg_source = st.sidebar.radio("Select background source:", ["Default Image", "Upload Image", "Image URL"])
    
    uploaded_file = None
    bg_url = None
    
    if bg_source == "Upload Image":
        uploaded_file = st.sidebar.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    elif bg_source == "Image URL":
        bg_url = st.sidebar.text_input(
            "Enter Image URL:",
            value="https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
        )
    
    blur_value = st.sidebar.slider("Background Blur (px)", min_value=0, max_value=20, value=5)
    set_background_with_blur(image_file=uploaded_file, image_url=bg_url, blur_px=blur_value)

    # Main Content
    st.title("🎥 YouTube Downloader Pro")
    st.markdown("<div class='content-container'>", unsafe_allow_html=True)
    
    st.subheader("Download Videos or Audio")
    url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2 = st.columns(2)
    with col1:
        option = st.selectbox("Format:", ["MP4 (Video)", "MP3 (Audio)"])
    with col2:
        quality = st.selectbox("Quality:", ["Best", "720p", "480p", "360p"])
    
    if st.button("Start Download", type="primary"):
        if not url:
            st.warning("Please enter a YouTube URL")
        else:
            with st.spinner("Downloading... This may take a while for longer videos"):
                filetype = "MP3" if "MP3" in option else "MP4"
                downloaded_file, error = download_video_audio(url, filetype)
                
                if error:
                    st.error(f"❌ Download failed: {error}")
                    st.markdown("""
                    **Troubleshooting Tips:**
                    - Try a different video URL
                    - Check if the video is age-restricted
                    - Ensure your internet connection is stable
                    - Try again later (YouTube might be blocking requests)
                    """)
                else:
                    st.success(f"✅ Download complete: {os.path.basename(downloaded_file)}")
                    
                    with open(downloaded_file, "rb") as f:
                        btn = st.download_button(
                            label=f"Save {filetype} File",
                            data=f,
                            file_name=os.path.basename(downloaded_file),
                            mime="audio/mpeg" if filetype == "MP3" else "video/mp4",
                            key=f"download_{filetype}"
                        )
                    
                    # Clean up downloaded file
                    try:
                        os.remove(downloaded_file)
                    except:
                        pass
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Note: This tool is for personal use only. Please respect copyright laws.")

if __name__ == "__main__":
    main()
