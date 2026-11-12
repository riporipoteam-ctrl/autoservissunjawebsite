"""Verify that GitHub Pages serves the updated Auto Servis Šunja site.

Example: python tools/verify_live_site.py
This checks the public deployment, not the repository files.
"""
import sys
import time
import urllib.error
import urllib.request

BASE = "https://autosunja.sitey.my"
VERSION = "20.0"


def get(path):
    url = BASE + path
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SunjaDeploymentCheck/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"{path}: HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")


def verify():
    # Query strings defeat stale edge caches while native Pages deploys catch up.
    stamp = str(int(time.time()))
    html = get("/?deployment_check=" + stamp)
    if f"css/style.css?v={VERSION}" not in html:
        raise AssertionError("Live HTML is older than v20.0")
    if f"js/main.js?v={VERSION}" not in html:
        raise AssertionError("Live HTML uses an old JavaScript version")
    if 'id="preloader"' in html or 'id="globeLoading"' in html:
        raise AssertionError("Live HTML still contains a blocking loader")
    if 'gallery-tile-link' not in html or 'map-quick-link' not in html:
        raise AssertionError("New first-tap gallery/map markup not published")

    css = get(f"/css/style.css?v={VERSION}&deployment_check={stamp}")
    if "/* v20.0: instant, compact and loader-free */" not in css:
        raise AssertionError("Updated stylesheet not deployed")
    if "#preloader" in css:
        raise AssertionError("Old loader CSS still deployed")

    js = get(f"/js/main.js?v={VERSION}&deployment_check={stamp}")
    if "document.addEventListener('click', function (event)" not in js:
        raise AssertionError("First-tap navigation JavaScript not deployed")
    if "jQuery" in js:
        raise AssertionError("Old jQuery handlers still deployed")

    print("PASS: live HTML, CSS and JavaScript are v20.0, with no loading screen.")
    return True


if __name__ == "__main__":
    last = ""
    # GitHub Pages publication and edge cache updates may trail the commit.
    for attempt in range(1, 13):
        try:
            verify()
            sys.exit(0)
        except (AssertionError, RuntimeError, urllib.error.URLError, TimeoutError) as exc:
            last = str(exc)
            print(f"Attempt {attempt}/12: {last}", flush=True)
            if attempt < 12:
                time.sleep(20)
    print("FAILED: could not confirm live deployment. Latest issue: " + last)
    sys.exit(1)
