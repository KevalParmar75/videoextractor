import streamlit as st
import yt_dlp
import base64

# --- CSS Styling with Blur + Theme Toggle ---
def set_background(blur_level=5, dark_theme=False):
    theme_color = "#0e1117" if dark_theme else "#ffffff"
    text_color = "#ffffff" if dark_theme else "#000000"
    blur_css = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{get_base64_image('background.jpg')}");
        background-size: cover;
        background-attachment: fixed;
        backdrop-filter: blur({blur_level}px);
        -webkit-backdrop-filter: blur({blur_level}px);
        color: {text_color};
    }}
    </style>
    '''
    st.markdown(blur_css, unsafe_allow_html=True)

# Encode image for inline CSS
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Download video using yt-dlp
def download_video(url):
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return f"✅ Downloaded: {info.get('title')}"
    except Exception as e:
        return f"❌ Error: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="Universal Video Downloader", layout="centered")

st.title("📥 Universal Video Downloader")
st.markdown("Download videos from almost any platform using yt-dlp.")

# Sidebar controls
st.sidebar.title("⚙️ Settings")
theme_mode = st.sidebar.radio("Theme", ["Light", "Dark"])
blur = st.sidebar.slider("Background Blur", min_value=0, max_value=20, value=8)

# Set dynamic background and theme
set_background(blur_level=blur, dark_theme=(theme_mode == "Dark"))

# Input field
video_url = st.text_input("🎯 Enter Video URL")

if st.button("🔽 Download Video"):
    if video_url.strip() == "":
        st.warning("Please enter a video URL.")
    else:
        with st.spinner("Downloading..."):
            result = download_video(video_url)
            st.success(result)
