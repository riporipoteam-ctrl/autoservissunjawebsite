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

BASE = "https://autosunja.com"
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

    # Verify the actual publicly hosted Google Search Console token and
    # crawler discovery files, not merely the source branch.
    verification = '<meta name="google-site-verification" content="SeUD1UgHTyjOPnkiG7U72gulqS9yaYa_5TpK-j-glJw" />'
    if verification not in html.split("</head>", 1)[0]:
        raise AssertionError("Search Console verification token absent from live HTML head")
    for resource in ("robots.txt", "sitemap.xml"):
        live = get("/" + resource + "?deployment_check=" + stamp)
        source = (ROOT / resource).read_bytes()
        if hashlib.sha256(live).digest() != hashlib.sha256(source).digest():
            raise AssertionError(f"Live {resource} differs from GitHub source")

    for asset, version in (("css/style.css", css_version), ("js/main.js", js_version)):
        live_bytes = get(f"/{asset}?v={version}&deployment_check={stamp}")
        source_bytes = (ROOT / asset).read_bytes()
        if hashlib.sha256(live_bytes).digest() != hashlib.sha256(source_bytes).digest():
            raise AssertionError(f"{asset} does not match the main-branch commit")

    # No native HTML <video> element on the intro: those may expose a play
    # overlay on Safari and let visitors pause the brand animation.
    if '<video' in html or 'id="sunjaIntroVideo"' in html:
        raise AssertionError("Native media player has returned to the intro")

    # The sharper 30fps brand animation is sampled only from the owner's MP4
    # at the established 120% speed, with the full original upload preserved.
    animation = "assets/video/sunja-logo-sharp-smooth-v36.webp"
    original = "assets/video/sunja-logo-intro-user-uploaded-v33.mp4"
    if f'src="{animation}"' not in html:
        raise AssertionError("Live page does not use the non-interactive animation image")
    for asset, expected in (
        (animation, "faffcf735b6ea397938644154b0e11bcd24a0345183066096d20e0c4dbd0a8f1"),
        (original, "73e0c3297813c72d219d7770e65f0b3e05f2c1a7fa6dbe96d79378118ba4ac45"),
    ):
        local_bytes = (ROOT / asset).read_bytes()
        live_bytes = get(f"/{asset}?deployment_check={stamp}")
        for label, payload in (("repository", local_bytes), ("live", live_bytes)):
            if hashlib.sha256(payload).hexdigest() != expected:
                raise AssertionError(f"{label} {asset} does not match expected original source")

    print(
        f"PASS: live CSS v{css_version}, JS v{js_version}, no HTML video player; "
        "30fps 5.03s optimized animation and original MP4 match GitHub byte-for-byte."
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
