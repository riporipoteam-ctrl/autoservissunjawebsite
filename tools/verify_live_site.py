"""Check actual public Pages deployment against the current GitHub checkout.

Run: python tools/verify_live_site.py
Never compares against a hard-coded asset version; this also verifies CSS/JS
content hashes so a stale CDN response cannot pass just by matching a URL.
"""
import hashlib
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://autosunja.sitey.my"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def get(path):
    request = urllib.request.Request(
        BASE + path,
        headers={
            "User-Agent": "SunjaDeploymentCheck/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"{path}: HTTP {response.status}")
        return response.read()


def asset_version(html, asset_path):
    pattern = re.escape(asset_path) + r"\?v=([A-Za-z0-9._-]+)"
    match = re.search(pattern, html)
    if match is None:
        raise AssertionError(f"Cannot find cache version for {asset_path}")
    return match.group(1)


def verify():
    source_html = (ROOT / "index.html").read_text(encoding="utf-8")
    css_version = asset_version(source_html, "css/style.css")
    js_version = asset_version(source_html, "js/main.js")
    stamp = str(int(time.time()))

    html = get("/?deployment_check=" + stamp).decode("utf-8", "replace")
    if f"css/style.css?v={css_version}" not in html:
        raise AssertionError(f"Live CSS reference is not v{css_version}")
    if f"js/main.js?v={js_version}" not in html:
        raise AssertionError(f"Live JavaScript reference is not v{js_version}")
    if 'id="preloader"' in html or 'id="globeLoading"' in html:
        raise AssertionError("Live HTML still contains a blocking loader")
    if 'gallery-tile-link' not in html or 'map-quick-link' not in html:
        raise AssertionError("Updated gallery/map links not published")

    for asset, version in (("css/style.css", css_version), ("js/main.js", js_version)):
        live_bytes = get(f"/{asset}?v={version}&deployment_check={stamp}")
        source_bytes = (ROOT / asset).read_bytes()
        if hashlib.sha256(live_bytes).digest() != hashlib.sha256(source_bytes).digest():
            raise AssertionError(f"{asset} does not match the main-branch commit")

    # The owner specifically requested this exact uploaded animation. Verify
    # both publicly served media files byte-for-byte, not just the HTML src.
    media_assets = (
        ("assets/video/sunja-logo-intro-user-uploaded-v33.mp4",
         "73e0c3297813c72d219d7770e65f0b3e05f2c1a7fa6dbe96d79378118ba4ac45",
         'src="'),
        ("assets/video/sunja-user-uploaded-frames-fallback-v33.webp",
         "d254a8b4b1b99870d5feff3fb8b6a663e53e06268e23e5c346e9bae5a86e4e6e",
         'data-src="'),
    )
    for asset, expected_sha, attribute in media_assets:
        if attribute + asset + '"' not in html:
            raise AssertionError(f"Live HTML does not reference {asset}")
        source_bytes = (ROOT / asset).read_bytes()
        live_bytes = get(f"/{asset}?deployment_check={stamp}")
        for label, content in (("repository", source_bytes), ("live", live_bytes)):
            digest = hashlib.sha256(content).hexdigest()
            if digest != expected_sha:
                raise AssertionError(f"{label} {asset}: wrong original-upload checksum ({digest})")

    print(
        f"PASS: live HTML references CSS v{css_version} and JS v{js_version}; "
        "HTML/CSS/JS and exact uploaded MP4/WebP assets match the repository."
    )


if __name__ == "__main__":
    last = ""
    # GitHub Pages publication and CDN cache updates can lag the Git push.
    for attempt in range(1, 13):
        try:
            verify()
            sys.exit(0)
        except (AssertionError, RuntimeError, urllib.error.URLError, TimeoutError) as exc:
            last = str(exc)
            print(f"Attempt {attempt}/12: {last}", flush=True)
            if attempt < 12:
                time.sleep(20)
    print("FAILED: live deployment could not be confirmed: " + last)
    sys.exit(1)
