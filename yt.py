import streamlit as st
import yt_dlp
import base64
import re
import urllib.request
import urllib.parse
import json
import html
from urllib.parse import urljoin, urlparse

# Safe Scrapling import
try:
    from scrapling.fetchers import Fetcher, StealthyFetcher, PlayWrightFetcher
    SCRAPLING_AVAILABLE = True
except Exception:
    Fetcher = StealthyFetcher = PlayWrightFetcher = None
    SCRAPLING_AVAILABLE = False


# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VideoRip · Universal Extractor",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ─────────────────────────────────────────────
# CSS Styling  (dark cinematic)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #0a0a0f !important;
    color: #e8e6f0 !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Ambient gradient orbs ── */
[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    top: -30vh; left: -20vw;
    width: 70vw; height: 70vh;
    background: radial-gradient(ellipse, rgba(99,31,200,0.18) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}
[data-testid="stApp"]::after {
    content: '';
    position: fixed;
    bottom: -20vh; right: -15vw;
    width: 60vw; height: 60vh;
    background: radial-gradient(ellipse, rgba(220,38,120,0.12) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}

/* ── Block container ── */
[data-testid="block-container"] {
    max-width: 780px !important;
    padding: 3rem 2rem 6rem !important;
    position: relative; z-index: 1;
}

/* ── Hero title ── */
.hero {
    text-align: center;
    padding: 2rem 0 2.5rem;
}
.hero h1 {
    font-size: clamp(2.4rem, 6vw, 3.8rem);
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #c084fc 0%, #f472b6 50%, #fb923c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}
.hero p {
    margin-top: .75rem;
    font-family: 'DM Mono', monospace;
    font-size: .85rem;
    color: #6b6880;
    letter-spacing: .04em;
}

/* ── Input area ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
    color: #e8e6f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: .92rem !important;
    padding: .85rem 1.1rem !important;
    transition: border-color .2s, box-shadow .2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(192,132,252,0.5) !important;
    box-shadow: 0 0 0 3px rgba(192,132,252,0.12) !important;
}
[data-testid="stTextInput"] label {
    font-size: .78rem !important;
    color: #6b6880 !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: .85rem 2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: .04em !important;
    cursor: pointer !important;
    transition: opacity .2s, transform .15s !important;
    margin-top: .4rem !important;
}
[data-testid="stButton"] > button:hover {
    opacity: .88 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    margin: 2rem 0;
}

/* ── Result cards ── */
.result-header {
    display: flex; align-items: center; gap: .6rem;
    margin: 1.8rem 0 1rem;
}
.result-header .badge {
    background: rgba(124,58,237,0.25);
    border: 1px solid rgba(124,58,237,0.4);
    color: #c084fc;
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    padding: .25rem .65rem;
    border-radius: 100px;
    letter-spacing: .06em;
}
.result-header h3 {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e8e6f0;
}

.video-card {
    background: rgba(255,255,255,0.033);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: .85rem;
    transition: border-color .2s;
}
.video-card:hover { border-color: rgba(192,132,252,0.3); }
.video-card .meta {
    display: flex; gap: .5rem; flex-wrap: wrap;
    margin-bottom: .65rem;
}
.video-card .tag {
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    padding: .2rem .55rem;
    border-radius: 6px;
    letter-spacing: .04em;
}
.tag-quality  { background: rgba(251,146,60,0.15);  color: #fb923c; border: 1px solid rgba(251,146,60,0.25); }
.tag-type     { background: rgba(99,31,200,0.15);   color: #a78bfa; border: 1px solid rgba(99,31,200,0.25); }
.tag-source   { background: rgba(34,197,94,0.12);   color: #4ade80; border: 1px solid rgba(34,197,94,0.2); }

.video-card .dl-link {
    display: inline-flex; align-items: center; gap: .4rem;
    font-family: 'DM Mono', monospace;
    font-size: .8rem;
    color: #c084fc;
    text-decoration: none;
    border: 1px solid rgba(192,132,252,0.3);
    border-radius: 8px;
    padding: .35rem .8rem;
    transition: background .2s, color .2s;
}
.video-card .dl-link:hover {
    background: rgba(192,132,252,0.12);
    color: #e879f9;
}

/* ── Title display ── */
.video-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e6f0;
    margin-bottom: 1rem;
    padding: .9rem 1.2rem;
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #7c3aed;
    border-radius: 0 10px 10px 0;
}

/* ── Status messages ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: .85rem !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    font-family: 'DM Mono', monospace !important;
    color: #6b6880 !important;
    font-size: .85rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #e8e6f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: .88rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    margin-top: 4rem;
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    color: #3d3a4d;
    letter-spacing: .05em;
}

/* ── Progress hint ── */
.step-list {
    list-style: none;
    padding: 0;
    margin: .5rem 0;
}
.step-list li {
    display: flex; align-items: center; gap: .6rem;
    font-family: 'DM Mono', monospace;
    font-size: .8rem;
    color: #6b6880;
    padding: .3rem 0;
}
.step-list li .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #7c3aed;
    flex-shrink: 0;
}
.step-list li.active { color: #c084fc; }
.step-list li.done   { color: #4ade80; }
.step-list li.done .dot { background: #4ade80; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

VIDEO_EXTENSIONS = (
    ".mp4", ".webm", ".ogg", ".ogv", ".mov", ".avi", ".mkv",
    ".flv", ".wmv", ".m4v", ".3gp", ".ts", ".m3u8", ".mpd",
)

def looks_like_video(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in VIDEO_EXTENSIONS)

def make_absolute(base_url: str, url: str) -> str:
    if url.startswith("//"):
        scheme = urlparse(base_url).scheme
        return f"{scheme}:{url}"
    if url.startswith("http"):
        return url
    return urljoin(base_url, url)


def extract_from_html_text(page_text: str, base_url: str) -> list[dict]:
    """Regex-based extraction — works even without Scrapling."""
    found = []
    seen = set()

    # <video src=...> and <source src=...>
    for match in re.finditer(
        r'<(?:video|source)[^>]+src=["\']([^"\']+)["\']', page_text, re.I
    ):
        u = make_absolute(base_url, html.unescape(match.group(1)))
        if u not in seen:
            seen.add(u); found.append({"url": u, "type": "html-tag", "quality": "unknown"})

    # data-src, data-video-url, etc.
    for match in re.finditer(
        r'data-(?:src|video[-_]?url|stream)=["\']([^"\']+)["\']', page_text, re.I
    ):
        u = make_absolute(base_url, html.unescape(match.group(1)))
        if looks_like_video(u) and u not in seen:
            seen.add(u); found.append({"url": u, "type": "data-attr", "quality": "unknown"})

    # JSON blobs: "url":"...mp4..." patterns
    for match in re.finditer(
        r'"(?:url|src|stream_url|video_url|playback_url|hls_url|dash_url)":\s*"(https?[^"]+)"',
        page_text, re.I
    ):
        u = html.unescape(match.group(1)).replace("\\u0026", "&").replace("\\/", "/")
        if (looks_like_video(u) or "m3u8" in u or "mpd" in u) and u not in seen:
            seen.add(u); found.append({"url": u, "type": "json-blob", "quality": "auto"})

    # <iframe src=...>
    for match in re.finditer(r'<iframe[^>]+src=["\']([^"\']+)["\']', page_text, re.I):
        u = make_absolute(base_url, html.unescape(match.group(1)))
        if any(x in u for x in ["youtube", "vimeo", "dailymotion", "twitch", "embed"]):
            if u not in seen:
                seen.add(u); found.append({"url": u, "type": "iframe-embed", "quality": "unknown"})

    # Plain .mp4 / .m3u8 / .mpd URLs anywhere in the source
    for match in re.finditer(
        r'https?://[^\s"\'<>]+?\.(?:mp4|webm|m3u8|mpd|ogg|ogv|mov)[^\s"\'<>]*',
        page_text, re.I
    ):
        u = match.group(0).rstrip(".,;)}")
        if u not in seen:
            seen.add(u); found.append({"url": u, "type": "bare-url", "quality": "auto"})

    return found


def fetch_page_source(url: str) -> str | None:
    """Fetch raw HTML via stdlib (no external deps)."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def extract_scrapling(url: str) -> list[dict]:
    if not SCRAPLING_AVAILABLE:
        return []
    try:
        fetcher = Fetcher(auto_match=False)
        page = fetcher.get(url, stealthy_headers=True)
        text = str(page.html_content) if hasattr(page, "html_content") else str(page)
        return extract_from_html_text(text, url)
    except Exception:
        return []


def extract_with_ytdlp(url: str) -> tuple[list[dict], str, str | None]:
    """Returns (formats, title, thumbnail)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "format": "bestvideo+bestaudio/best",
        # Try to bypass geo/age restrictions
        "geo_bypass": True,
        "nocheckcertificate": True,
        # Accept cookies from browser if available
        "extractor_retries": 3,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        seen_urls = set()

        for f in info.get("formats", []):
            furl = f.get("url", "")
            if not furl or furl in seen_urls:
                continue
            seen_urls.add(furl)

            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            has_video = vcodec not in (None, "none")
            has_audio = acodec not in (None, "none")

            quality = f.get("format_note") or f.get("quality") or "unknown"
            height = f.get("height")
            if height:
                quality = f"{height}p"

            ftype = "video+audio" if (has_video and has_audio) else \
                    "video"        if has_video else \
                    "audio"        if has_audio else "manifest"

            ext = f.get("ext", "")
            formats.append({
                "url": furl,
                "quality": str(quality),
                "type": ftype,
                "ext": ext,
                "filesize": f.get("filesize"),
            })

        # Sort: video+audio first, then by quality desc
        formats.sort(key=lambda x: (x["type"] != "video+audio", x["quality"]), reverse=False)

        title = info.get("title", "Untitled")
        thumb = info.get("thumbnail")
        return formats, title, thumb

    except Exception as e:
        return [], str(e), None


def fmt_size(b) -> str:
    if not b:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero">
  <h1>VideoRip</h1>
  <p>UNIVERSAL VIDEO EXTRACTOR · PASTE ANY URL</p>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────
video_url = st.text_input(
    "PAGE URL",
    placeholder="https://example.com/watch?v=...",
    label_visibility="visible",
)

col1, col2 = st.columns([3, 1])
with col1:
    extract_btn = st.button("⚡  Extract Videos", use_container_width=True)
with col2:
    quality_filter = st.selectbox(
        "Show",
        ["All", "Video+Audio", "Video only", "Audio only"],
        label_visibility="collapsed",
    )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ── Extraction logic ────────────────────────────
if extract_btn:
    if not video_url.strip():
        st.warning("⚠️  Please enter a URL first.")
        st.stop()

    url = video_url.strip()

    # ── Phase 1: yt-dlp ────────────────────────
    with st.spinner("🔍  Probing with yt-dlp…"):
        ytdlp_formats, title_or_err, thumbnail = extract_with_ytdlp(url)

    # ── Phase 2: HTML scrape ───────────────────
    html_formats: list[dict] = []
    if not ytdlp_formats:
        with st.spinner("🕷  Scraping page source…"):
            if SCRAPLING_AVAILABLE:
                html_formats = extract_scrapling(url)
            if not html_formats:
                raw = fetch_page_source(url)
                if raw:
                    html_formats = extract_from_html_text(raw, url)


    # ─────────────────────────────────────────────
    # Display results
    # ─────────────────────────────────────────────

    if ytdlp_formats:

        st.markdown(f'<div class="video-title">🎬 {html.escape(title_or_err)}</div>',
                    unsafe_allow_html=True)

        if thumbnail:
            st.image(thumbnail, use_container_width=True)

        # Filter
        def keep(f):
            if quality_filter == "Video+Audio": return f["type"] == "video+audio"
            if quality_filter == "Video only":  return f["type"] == "video"
            if quality_filter == "Audio only":  return f["type"] == "audio"
            return True

        filtered = [f for f in ytdlp_formats if keep(f)]

        st.markdown(f"""
        <div class="result-header">
          <span class="badge">yt-dlp</span>
          <h3>{len(filtered)} stream{"s" if len(filtered)!=1 else ""} found</h3>
        </div>
        """, unsafe_allow_html=True)

        for f in filtered[:30]:
            size_str = fmt_size(f["filesize"])
            type_cls = {
                "video+audio": "tag-source",
                "video": "tag-quality",
                "audio": "tag-type",
            }.get(f["type"], "tag-type")

            st.markdown(f"""
            <div class="video-card">
              <div class="meta">
                <span class="tag tag-quality">{html.escape(f['quality'])}</span>
                <span class="tag {type_cls}">{html.escape(f['type'])}</span>
                {'<span class="tag tag-type">' + html.escape(f['ext']) + '</span>' if f['ext'] else ''}
                {'<span class="tag tag-source">' + html.escape(size_str) + '</span>' if size_str else ''}
              </div>
              <a class="dl-link" href="{html.escape(f['url'])}" target="_blank" rel="noopener">
                ↓ &nbsp;Open / Download
              </a>
            </div>
            """, unsafe_allow_html=True)

        if len(ytdlp_formats) > 30:
            st.caption(f"Showing 30 of {len(ytdlp_formats)} streams.")

    elif html_formats:

        st.markdown(f"""
        <div class="result-header">
          <span class="badge">HTML scrape</span>
          <h3>{len(html_formats)} video source{"s" if len(html_formats)!=1 else ""} found</h3>
        </div>
        """, unsafe_allow_html=True)

        for f in html_formats[:20]:
            label = f.get("type", "").replace("-", " ")
            st.markdown(f"""
            <div class="video-card">
              <div class="meta">
                <span class="tag tag-type">{html.escape(label)}</span>
              </div>
              <code style="font-family:'DM Mono',monospace;font-size:.75rem;color:#6b6880;
                           display:block;margin-bottom:.6rem;word-break:break-all;">
                {html.escape(f['url'][:120])}{"…" if len(f['url'])>120 else ""}
              </code>
              <a class="dl-link" href="{html.escape(f['url'])}" target="_blank" rel="noopener">
                ↓ &nbsp;Open / Download
              </a>
            </div>
            """, unsafe_allow_html=True)

        # Try to preview the first playable one
        playable = next((f for f in html_formats if looks_like_video(f["url"])), None)
        if playable:
            with st.expander("▶  Preview first video"):
                st.video(playable["url"])

    else:
        st.error(
            "No video streams detected. The site may require JavaScript rendering, "
            "authentication, or DRM. Try pasting the direct stream URL if you have it."
        )
        with st.expander("ℹ️  Debug info"):
            st.code(title_or_err if not ytdlp_formats else "No error", language="text")


# ── Footer ────────────────────────────────────
st.markdown("""
<div class="footer">
  VideoRip · powered by yt-dlp & scrapling · for personal use only
</div>
""", unsafe_allow_html=True)
