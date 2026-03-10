# VideoRip — Universal Video Extractor

> A Streamlit-based web app that extracts and downloads videos from virtually any website using a 4-phase extraction pipeline.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Extraction Pipeline](#extraction-pipeline)
- [Supported Sites](#supported-sites)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)

---

## Overview

VideoRip is a locally-run video extraction tool with a clean dark UI. Paste any video page URL and it will attempt to find and surface all available video streams, download links, and media sources — using progressively more powerful methods until it finds something.

It is powered by **yt-dlp**, **Playwright**, **Scrapling**, and a custom regex-based HTML scraper, all wrapped in a polished Streamlit interface.

---

## Features

- **4-phase extraction pipeline** — tries progressively deeper methods so fast sites stay fast
- **yt-dlp integration** — supports 1,000+ sites natively out of the box
- **Playwright JS rendering** — runs a real headless Chromium browser for JavaScript-heavy SPAs
- **Network request interception** — captures video stream URLs as the browser loads them
- **PasteDownload.com fallback** — automates the PasteDownload UI to handle sites nothing else can crack.
- **Regex HTML scraper** — hunts for video URLs in `<video>` tags, `data-src` attributes, JSON blobs, iframes, and bare URLs
- **Quality filter** — filter results by Video+Audio, Video only, or Audio only
- **Dark cinematic UI** — clean, minimal interface with result cards, quality badges, and download links

---

## Requirements

| Dependency | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.35.0 | Web UI framework |
| `yt-dlp` | ≥ 2024.5.1 | Primary video extractor (1,000+ sites) |
| `scrapling` | ≥ 0.2.0 | Stealthy HTTP fetcher with CSS selectors |
| `playwright` | ≥ 1.44.0 | Headless Chromium for JS rendering & PasteDownload automation |

Python standard library modules used (no install needed): `re`, `urllib`, `html`, `json`, `time`, `base64`

---

## Installation

### 1. Clone or download the project

```bash
git clone https://github.com/KevalParmar75/videoextractor.git
cd videorip
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright's Chromium browser

This is a **separate step** required for JS rendering and PasteDownload fallback. Without it, phases 3 and 4 of the pipeline will be silently skipped.

```bash
playwright install chromium
```

> **Note:** This downloads a ~150MB Chromium binary. It only needs to be done once.

### 4. Run the app

```bash
streamlit run yt.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Usage

1. **Paste a URL** — Copy any video page URL and paste it into the input field
2. **Choose a filter** *(optional)* — Use the dropdown to show only Video+Audio, Video only, or Audio only streams
3. **Click Extract Videos** — The app runs through its pipeline and displays results
4. **Download** — Click any `↓ Open / Download` link to open the stream in a new tab or trigger a download

---

## How It Works

VideoRip runs a **4-phase waterfall pipeline**. Each phase only activates if the previous one found nothing, so common sites resolve instantly in phase 1 while obscure JS-heavy sites fall through to the deeper methods.

```
Phase 1: yt-dlp
    ↓ (if no results)
Phase 2: Static HTML scrape
    ↓ (if no results)
Phase 3: Playwright JS render + network intercept
    ↓ (if no results)
Phase 4: PasteDownload.com automation
```

---

## Extraction Pipeline

### Phase 1 — yt-dlp

The first and fastest method. yt-dlp natively supports over 1,000 video platforms including YouTube, Vimeo, Twitter, Reddit, Dailymotion, and many more. It extracts all available format streams along with quality, codec, file size, and thumbnail metadata.

**Options enabled:**
- `geo_bypass` — attempts to bypass geographic restrictions
- `nocheckcertificate` — ignores SSL errors on some sites
- `extractor_retries: 3` — retries on transient failures

If yt-dlp succeeds, the pipeline stops here.

---

### Phase 2 — Static HTML Scrape

If yt-dlp has no extractor for the site, the raw HTML is fetched using a browser-spoofing `urllib` request. The HTML is then scanned with a multi-pattern regex engine looking for video URLs in five different ways:

| Pattern | What it finds |
|---|---|
| `<video src=...>` / `<source src=...>` | Standard HTML5 video tags |
| `data-src`, `data-video-url` | Lazy-loaded video attributes |
| JSON blobs | `"url": "...mp4..."` patterns in inline scripts |
| `<iframe src=...>` | Embedded YouTube, Vimeo, Dailymotion players |
| Bare URLs | Any `.mp4`, `.m3u8`, `.mpd`, `.webm` URL anywhere in source |

If Scrapling is installed, it is also used here as a more capable alternative to raw `urllib`.

---

### Phase 3 — Playwright JS Render + Network Intercept

For JavaScript-heavy Single Page Applications (SPAs) where the video URL is generated at runtime, a headless Chromium browser is launched via Playwright.

**What it does:**
- Opens the page in a real browser with a spoofed user-agent
- Intercepts every outgoing network request and response, flagging any with video MIME types or video-like URL patterns
- Waits for the page to reach `networkidle` state, then waits an additional 3 seconds for lazy-loaded players
- Attempts to auto-click common play button selectors (`.vjs-play-control`, `[aria-label*='play']`, etc.) to trigger stream loading
- Queries `video.src` and `video.currentSrc` directly from the live DOM via JavaScript
- Scrapes the fully rendered HTML one more time for any remaining URLs

---

### Phase 4 — PasteDownload.com Automation

For sites that even Playwright's direct render can't handle, VideoRip automates **PasteDownload.com** — a third-party service that runs its own server-side browser to resolve these streams.

**What it does:**
1. Opens `pastedownload.com/universal-video-downloader/` in headless Chromium
2. Fills the URL input with your video URL
3. Clicks the Download button
4. Waits up to 25 seconds for download links to appear
5. Scrapes all anchor tags from the result page, filtering for links that match video file extensions, CDN/storage domains, or download-related text

> **Note:** Links from PasteDownload may expire within minutes to hours, as they often contain short-lived signed tokens. Download promptly after extraction.

---

## Supported Sites

**Natively via yt-dlp (Phase 1):**

YouTube, Vimeo, Twitter/X, Reddit, Facebook, Instagram, TikTok, Dailymotion, Twitch, SoundCloud, Bilibili, Rumble, Odnoklassniki, and 1,000+ more. See the [full yt-dlp supported sites list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

**Via Playwright + PasteDownload fallback (Phases 3 & 4):**

JavaScript-rendered SPAs and niche adult/social video platforms not covered by yt-dlp, supported by PasteDownload's server-side rendering.

**Not supported:**
- Content behind a login wall that requires your personal session cookies
- DRM-protected streams (Widevine, PlayReady)
- Private videos you do not have access to

---

## Troubleshooting

**`playwright install chromium` fails**

Make sure you have sufficient disk space (~300MB) and that your Python environment has write access. On some Linux systems you may need to run:

```bash
playwright install-deps chromium
```

**Phase 3/4 never runs**

Playwright must be both installed (`pip install playwright`) and have Chromium downloaded (`playwright install chromium`). If either step is missing, phases 3 and 4 are silently skipped and a tip is shown in the UI.

**PasteDownload returns no links**

PasteDownload's UI changes periodically. If the automation stops working, it likely means their page structure has been updated. The selectors in `extract_via_pastedownload()` in `app.py` may need to be adjusted.

**yt-dlp returns "Unsupported URL"**

The site has no yt-dlp extractor. The pipeline will automatically fall through to phases 2, 3, and 4.

**Got links but they return 403**

The stream URL contains a session-bound signed token. This means the URL is only valid within an active browser session on that site. Use the PasteDownload result directly and download immediately — the link will expire.

---

## Limitations

- **No DRM support** — Widevine and PlayReady encrypted streams cannot be extracted
- **No login support** — Content behind authentication walls requires your cookies; this is not currently implemented
- **PasteDownload dependency** — Phase 4 relies on a third-party service that may change or go offline
- **Token expiry** — Stream URLs for some sites expire within minutes; download promptly
- **Playwright required for JS sites** — Without Chromium installed, JS-heavy SPAs will not be extractable
- **Personal use only** — Respect copyright and the terms of service of any platform you use this with

---

*VideoRip*
