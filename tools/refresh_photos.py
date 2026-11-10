#!/usr/bin/env python3
"""Auto fresh-photos for autosunja.sitey.my.

Runs from GitHub Actions (see .github/workflows/fresh-photos.yml).
Pulls the shop's newest TikTok posts (@autoservissunja), mirrors the
images into assets/photos/, and keeps photos.json pools (hero,
heroMobile, gallery) limited to posts at most 60 days old.
Fail-soft: if every source fails, nothing changes and the run passes.
"""
import json, os, re, subprocess, sys, time
from datetime import datetime, timezone, timedelta
from io import BytesIO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_JSON = os.path.join(ROOT, "photos.json")
PHOTO_DIR = os.path.join(ROOT, "assets", "photos")
HANDLE = "autoservissunja"
MAX_AGE_DAYS = 60
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

def log(*a):
    print("[refresh]", *a, flush=True)

def from_ytdlp():
    url = f"https://www.tiktok.com/@{HANDLE}"
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings",
         "--socket-timeout", "30", url],
        capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError("yt-dlp exit " + str(out.returncode))
    data = json.loads(out.stdout)
    posts = []
    for e in data.get("entries") or []:
        pid = str(e.get("id") or "")
        ts = e.get("timestamp")
        if not pid or not ts:
            continue
        thumbs = e.get("thumbnails") or []
        img = None
        if thumbs:
            img = sorted(thumbs, key=lambda t: (t.get("width") or 0))[-1].get("url")
        if not img:
            continue
        posts.append({"id": pid, "ts": int(ts), "img": img,
                      "title": e.get("title") or "",
                      "url": e.get("webpage_url") or f"https://www.tiktok.com/@{HANDLE}/photo/{pid}"})
    return posts

def from_tikwm():
    import requests
    r = requests.get("https://www.tikwm.com/api/user/posts",
                     params={"unique_id": HANDLE, "count": 35}, headers=UA, timeout=40)
    r.raise_for_status()
    posts = []
    for v in (r.json().get("data") or {}).get("videos") or []:
        pid = str(v.get("video_id") or "")
        ts = v.get("create_time")
        if not pid or not ts:
            continue
        img = None
        if v.get("images"):
            img = v["images"][0]
        img = img or v.get("origin_cover") or v.get("cover")
        if not img:
            continue
        is_photo = bool(v.get("images"))
        posts.append({"id": pid, "ts": int(ts), "img": img,
                      "title": v.get("title") or "",
                      "url": f"https://www.tiktok.com/@{HANDLE}/{'photo' if is_photo else 'video'}/{pid}"})
    return posts

def fetch_title(pid):
    """Full metadata for one post (flat listings often lack real titles)."""
    try:
        out = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "-J", "--no-warnings",
             "--socket-timeout", "20", f"https://www.tiktok.com/@{HANDLE}/photo/{pid}"],
            capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            return ""
        d = json.loads(out.stdout)
        t = d.get("title") or ""
        if len(re.sub(r"[#@]\S+", "", t).strip()) < 4:
            t = (d.get("description") or "").split("\n")[0]
        return clean_title(t, "")
    except Exception:
        return ""

def clean_title(raw, date_s):
    t = re.sub(r"[#@]\S+", "", raw or "")
    t = re.sub(r"\s+", " ", t).strip(" -–—|")
    if len(t) < 4:
        t = "U radionici"
    return t[:48]

def main():
    posts, source = [], None
    for name, fn in (("yt-dlp", from_ytdlp), ("tikwm", from_tikwm)):
        try:
            posts = fn()
            if posts:
                source = name
                break
            log(name, "returned no posts")
        except Exception as ex:
            log(name, "failed:", str(ex)[:160])
    if not posts:
        log("all sources failed; leaving the site unchanged")
        return 0
    log("source:", source, "| posts fetched:", len(posts))

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    fresh = []
    for p in posts:
        dt = datetime.fromtimestamp(p["ts"], timezone.utc)
        if dt >= cutoff:
            p["date"] = dt.strftime("%Y-%m-%d")
            fresh.append(p)
    fresh.sort(key=lambda p: -p["ts"])
    log("posts within", MAX_AGE_DAYS, "days:", len(fresh))

    with open(PHOTOS_JSON, encoding="utf-8") as f:
        pools = json.load(f)

    def post_id(entry):
        m = re.search(r"/(\d{10,})(?:[/?#]|$)", entry.get("href", ""))
        return m.group(1) if m else None

    known = set()
    for pool in ("hero", "heroMobile", "gallery"):
        for e in pools.get(pool, []):
            pid = post_id(e)
            if pid:
                known.add(pid)

    # enrich titles: real captions for new posts, and repair generic ones
    for p in fresh:
        if clean_title(p["title"], p["date"]) == "U radionici":
            better = fetch_title(p["id"])
            if better and better != "U radionici":
                p["title"] = better
        want = clean_title(p["title"], p["date"])
        if want != "U radionici":
            for pool in ("hero", "heroMobile", "gallery"):
                for e in pools.get(pool, []):
                    if post_id(e) == p["id"] and e.get("title") == "U radionici":
                        e["title"] = want

    import requests
    from PIL import Image
    os.makedirs(PHOTO_DIR, exist_ok=True)
    added = 0
    for p in fresh:
        if p["id"] in known:
            continue
        try:
            resp = requests.get(p["img"], headers=UA, timeout=40)
            resp.raise_for_status()
            im = Image.open(BytesIO(resp.content)).convert("RGB")
        except Exception as ex:
            log("download failed for", p["id"], str(ex)[:120])
            continue
        tag = p["date"].replace("-", "") + "-" + p["id"][-6:]
        portrait = im.copy()
        if portrait.width > 860:
            portrait = portrait.resize((860, round(portrait.height * 860 / portrait.width)), Image.LANCZOS)
        pfile = f"tt-{tag}.webp"
        portrait.save(os.path.join(PHOTO_DIR, pfile), "WEBP", quality=84)
        wide = im.copy()
        tw, th = 1600, 1000
        s = max(tw / wide.width, th / wide.height)
        wide = wide.resize((round(wide.width * s), round(wide.height * s)), Image.LANCZOS)
        x = (wide.width - tw) // 2
        y = (wide.height - th) // 2
        wide = wide.crop((x, y, x + tw, y + th))
        wfile = f"tt-wide-{tag}.webp"
        wide.save(os.path.join(PHOTO_DIR, wfile), "WEBP", quality=82)
        title = clean_title(p["title"], p["date"])
        pools.setdefault("gallery", []).insert(0, {"src": f"assets/photos/{pfile}", "href": p["url"], "title": title, "date": p["date"]})
        pools.setdefault("hero", []).insert(0, {"src": f"assets/photos/{wfile}", "href": p["url"], "title": title, "date": p["date"]})
        pools.setdefault("heroMobile", []).insert(0, {"src": f"assets/photos/{pfile}", "href": p["url"], "title": title, "date": p["date"]})
        known.add(p["id"])
        added += 1
        log("added", p["id"], p["date"], title)

    # prune entries older than the cutoff (keep pool minimums with the newest)
    removed = 0
    minimums = {"hero": 1, "heroMobile": 1, "gallery": 5}
    for pool, minimum in minimums.items():
        entries = pools.get(pool, [])
        entries.sort(key=lambda e: e.get("date", ""), reverse=True)
        keep, drop = [], []
        for e in entries:
            d = e.get("date")
            fresh_e = False
            if d:
                try:
                    fresh_e = datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc) >= cutoff
                except ValueError:
                    fresh_e = False
            if fresh_e or len(keep) < minimum:
                keep.append(e)
            else:
                drop.append(e)
        pools[pool] = keep
        for e in drop:
            removed += 1
            fp = os.path.join(ROOT, e.get("src", ""))
            if os.path.isfile(fp):
                os.remove(fp)
                log("retired", e["src"])

    with open(PHOTOS_JSON, "w", encoding="utf-8") as f:
        json.dump(pools, f, ensure_ascii=False, indent=1)
    log("done. added:", added, "| retired:", removed,
        "| pool sizes:", {k: len(pools.get(k, [])) for k in minimums})
    return 0

if __name__ == "__main__":
    sys.exit(main())
