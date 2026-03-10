import streamlit as st
import yt_dlp
import base64

# Safe Scrapling import (prevents cloud crash)
try:
    from scrapling.fetchers import Fetcher
except:
    Fetcher = None


# -------------------------------
# Background Styling
# -------------------------------
def set_background(blur_level=5, dark_theme=False):

    text_color = "#ffffff" if dark_theme else "#000000"

    try:
        bg = get_base64_image("background.jpg")
    except:
        bg = ""

    blur_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg}");
        background-size: cover;
        background-attachment: fixed;
        backdrop-filter: blur({blur_level}px);
        -webkit-backdrop-filter: blur({blur_level}px);
        color: {text_color};
    }}
    </style>
    """

    st.markdown(blur_css, unsafe_allow_html=True)


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# -------------------------------
# Scrapling Video Extractor
# -------------------------------
def extract_video_sources(url):

    if Fetcher is None:
        return []

    try:
        fetcher = Fetcher()
        page = fetcher.get(url)

        video_links = set()

        for v in page.css("video"):
            if v.attr("src"):
                video_links.add(v.attr("src"))

        for s in page.css("source"):
            if s.attr("src"):
                video_links.add(s.attr("src"))

        for iframe in page.css("iframe"):
            if iframe.attr("src"):
                video_links.add(iframe.attr("src"))

        for link in page.css("a"):
            href = link.attr("href")
            if href and any(ext in href for ext in [".mp4", ".m3u8", ".webm"]):
                video_links.add(href)

        return list(video_links)

    except:
        return []


# -------------------------------
# yt-dlp extractor
# -------------------------------
def extract_with_ytdlp(url):

    ydl_opts = {
        "quiet": True,
        "skip_download": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])

        videos = []

        for f in formats:
            if f.get("url"):
                videos.append({
                    "quality": f.get("format_note", "unknown"),
                    "url": f.get("url")
                })

        return videos, info.get("title", "Video")

    except Exception as e:
        return [], str(e)


# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="Universal Video Extractor", layout="centered")

st.title("🎥 Universal Video Extractor")
st.markdown("Extract videos from almost any website.")

# Sidebar settings
st.sidebar.title("⚙️ Settings")

theme_mode = st.sidebar.radio("Theme", ["Light", "Dark"])
blur = st.sidebar.slider("Background Blur", 0, 20, 8)

set_background(blur_level=blur, dark_theme=(theme_mode == "Dark"))

video_url = st.text_input("🔗 Enter Page URL")


if st.button("🔍 Extract Videos"):

    if not video_url:
        st.warning("Please enter a URL")
        st.stop()

    with st.spinner("Scanning page..."):

        # First try Scrapling
        videos = extract_video_sources(video_url)

        if videos:

            st.success(f"Found {len(videos)} direct video sources")

            for v in videos:
                st.video(v)
                st.markdown(f"[⬇ Download Video]({v})")

        else:

            st.warning("No direct video found. Trying yt-dlp...")

            videos, title = extract_with_ytdlp(video_url)

            if videos:

                st.success(f"Video detected: {title}")

                for v in videos[:10]:

                    st.write(f"Quality: {v['quality']}")
                    st.markdown(f"[⬇ Download]({v['url']})")

            else:

                st.error("No video streams detected.")
