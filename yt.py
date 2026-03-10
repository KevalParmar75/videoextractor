import streamlit as st
import yt_dlp
import base64
from scrapling import Scraper

# -------------------------------
# Background Styling
# -------------------------------
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


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# -------------------------------
# Scrapling Video Extractor
# -------------------------------
def extract_video_sources(url):

    scraper = Scraper()
    page = scraper.get(url)

    video_links = set()

    # HTML5 videos
    for v in page.css("video"):
        if v.attr("src"):
            video_links.add(v.attr("src"))

    # Source tags
    for s in page.css("source"):
        if s.attr("src"):
            video_links.add(s.attr("src"))

    # iframe embeds
    for iframe in page.css("iframe"):
        if iframe.attr("src"):
            video_links.add(iframe.attr("src"))

    # raw links containing video formats
    for link in page.css("a"):
        href = link.attr("href")
        if href and any(ext in href for ext in [".mp4", ".m3u8", ".webm"]):
            video_links.add(href)

    return list(video_links)


# -------------------------------
# yt-dlp Downloader
# -------------------------------
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


# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="Universal Video Extractor", layout="centered")

st.title("🎥 Universal Video Extractor")
st.markdown("Extract and download videos from almost any website.")

# Sidebar
st.sidebar.title("⚙️ Settings")

theme_mode = st.sidebar.radio("Theme", ["Light", "Dark"])
blur = st.sidebar.slider("Background Blur", 0, 20, 8)

set_background(blur_level=blur, dark_theme=(theme_mode == "Dark"))

video_url = st.text_input("🔗 Enter Page URL")


if st.button("🔍 Extract Videos"):

    if not video_url:
        st.warning("Enter a URL first")

    else:

        with st.spinner("Scraping page..."):

            videos = extract_video_sources(video_url)

            if videos:

                st.success(f"Found {len(videos)} video sources")

                for v in videos:
                    st.write(v)

                    if st.button(f"Download {v[:30]}"):
                        result = download_video(v)
                        st.success(result)

            else:

                st.warning("No direct video found. Trying yt-dlp...")

                result = download_video(video_url)
                st.success(result)        
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
