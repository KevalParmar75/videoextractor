import streamlit as st
import yt_dlp
import os
import ssl
import certifi
import base64

# Optional: fix SSL issues
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['SSL_CERT_FILE'] = certifi.where()

# 🔧 Background with blur via CSS layering
def set_background_with_blur(image_file=None, image_url=None, blur_px=5):
    if image_file:
        img_bytes = image_file.read()
        encoded = base64.b64encode(img_bytes).decode()
        image_uri = f"data:image/jpeg;base64,{encoded}"
    elif image_url:
        image_uri = image_url
    else:
        image_uri = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"

    st.markdown(
        f"""
        <style>
        /* Background layer */
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

        /* Content styling */
        .stApp {{
            background: transparent;
        }}
        </style>
        <div class="bg-container"></div>
        """,
        unsafe_allow_html=True
    )

# Sidebar: Background controls
st.sidebar.header("🎨 Background Settings")
bg_source = st.sidebar.radio("Select background source:", ["Upload Image", "Image URL"])
uploaded_file = None
bg_url = None

if bg_source == "Upload Image":
    uploaded_file = st.sidebar.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
else:
    bg_url = st.sidebar.text_input(
        "Enter Image URL:",
        value="https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
    )

# Blur slider
blur_value = st.sidebar.slider("Background Blur (px)", min_value=0, max_value=20, value=5)

# Apply background
set_background_with_blur(image_file=uploaded_file, image_url=bg_url, blur_px=blur_value)

# Downloader function
def download_video(url, download_type):
    if download_type == 'MP3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }
    else:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if download_type == 'MP3':
            filename = os.path.splitext(filename)[0] + ".mp3"
        return filename

# App UI
st.title("🎥 YouTube Downloader with Blurred Background")
st.write("Paste a video link and choose your preferred format.")

url = st.text_input("Enter video URL:")
option = st.selectbox("Choose format:", ["MP4 (Video)", "MP3 (Audio)"])
download_btn = st.button("Download")

if download_btn and url:
    with st.spinner("Downloading... Please wait."):
        try:
            filetype = "MP3" if "MP3" in option else "MP4"
            downloaded_file = download_video(url, filetype)
            st.success(f"Downloaded successfully: {downloaded_file}")
            with open(downloaded_file, "rb") as f:
                st.download_button(
                    label=f"Download {filetype}",
                    data=f,
                    file_name=downloaded_file,
                    mime="audio/mpeg" if filetype == "MP3" else "video/mp4"
                )
        except Exception as e:
            st.error(f"Download failed: {e}")
