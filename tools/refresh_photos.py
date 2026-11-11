#!/usr/bin/env python3
"""Auto fresh-photo sync for autosunja.sitey.my — v3.

Runs from GitHub Actions every 15 minutes. TikTok is the no-credential
primary source and supports multi-image photo posts. Instagram and
Facebook use the same pipeline: the official Meta Graph API is used when
repository secrets are configured, with a best-effort public yt-dlp
fallback when they are not.

Every imported image is self-hosted in assets/photos/, tagged with its
source/post/media identity, and added to the fresh hero/gallery pools.
One blocked social network never prevents the other sources from updating.
"""
import hashlib, json, os, re, subprocess, sys, unicodedata
from datetime import datetime, timezone, timedelta
from io import BytesIO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_JSON = os.path.join(ROOT, "photos.json")
PHOTO_DIR = os.path.join(ROOT, "assets", "photos")
HANDLE = "autoservissunja"
INSTAGRAM_HANDLE = "sunja_servis_peugeot"
FACEBOOK_URL = "https://www.facebook.com/share/1MTp82REEF/"
MAX_AGE_DAYS = 60
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
CATS = ["kljucevi", "dijagnostika", "elektrika", "veliki", "mali", "peugeot"]

def log(*a):
    print("[refresh]", *a, flush=True)

def norm(text):
    t = unicodedata.normalize("NFKD", (text or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.replace("dj", "d")

KEYWORDS = {
    "kljucevi": ["kljuc", "daljinsk", "immo", "immobil", "key", "remote", "fob"],
    "dijagnostika": ["dijagnost", "diagbox", "diagnos", "tester", "obd", "gresk"],
    "elektrika": ["elektrik", "elektronik", "ecu", "akumulator", "alternator", "instalac", "anlaser"],
    "veliki": ["zupcast", "remen", "glava motora", "kvacil", "veliki servis", "lanac"],
    "mali": ["ulje", "mali servis", "filter", "kocnic", "svjecic", "servis ulja"],
    "peugeot": ["peugeot", "puretech"],
}

def classify(raw):
    t = norm(raw)
    tokens = set(re.findall(r"[a-z0-9]+", t))
    for cat in CATS:
        for kw in KEYWORDS[cat]:
            if " " in kw:
                if kw in t:
                    return cat
            elif any(tok.startswith(kw) for tok in tokens):
                return cat
    return "opcenito"

def _media_record(source, post_id, ts, img, title, url, media_index=0):
    return {
        "id": str(post_id),
        "post_id": str(post_id),
        "media_id": f"{source}:{post_id}:{media_index}",
        "media_index": int(media_index),
        "source": source,
        "ts": int(ts),
        "img": img,
        "title": title or "",
        "raw": title or "",
        "url": url,
    }

def _gallery_dl_url_rows(raw):
    """Return (url, metadata) rows from gallery-dl -j output.

    gallery-dl can emit either one nested JSON document or JSON Lines,
    depending on version/configuration, so support both formats.
    """
    docs = []
    try:
        docs = [json.loads(raw)]
    except Exception:
        for line in (raw or "").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                docs.append(json.loads(line))
            except Exception:
                continue

    rows = []
    def walk(value):
        if isinstance(value, list):
            if len(value) >= 3 and value[0] == 3 and isinstance(value[1], str):
                rows.append((value[1], value[2] if isinstance(value[2], dict) else {}))
                return
            for child in value:
                walk(child)
    for doc in docs:
        walk(doc)
    return rows

def _gallery_dl(url, limit=None, timeout=90):
    cmd = [
        "gallery-dl", "--config-ignore", "--no-input", "--no-colors",
        "-j",
    ]
    if limit:
        cmd += ["--range", f"1-{int(limit)}"]
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError("gallery-dl exit " + str(out.returncode))
    return _gallery_dl_url_rows(out.stdout)

def expand_tiktok_photo(post_id, post_url, ts, title=""):
    """Resolve every image from one TikTok /photo/ post with gallery-dl."""
    try:
        rows = _gallery_dl(post_url, timeout=75)
    except Exception as ex:
        log("gallery-dl TikTok photo unavailable:", post_id, str(ex)[:100])
        return None

    images = []
    for url, meta in rows:
        ext = str(meta.get("extension") or "").lower().lstrip(".")
        post_type = str(meta.get("post_type") or meta.get("type") or "").lower()
        if ext and ext not in ("jpg", "jpeg", "png", "webp", "avif", "heic"):
            continue
        if post_type and post_type not in ("image", "photo", "carousel"):
            continue
        if url and url not in images:
            images.append(url)

    records = [
        _media_record("tiktok", post_id, ts, img, title, post_url, idx)
        for idx, img in enumerate(images)
    ]
    for record in records:
        record["quality_source"] = "original"
    return records

def from_ytdlp():
    """TikTok profile fallback, with direct slideshow expansion when possible."""
    url = f"https://www.tiktok.com/@{HANDLE}"
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings",
         "--socket-timeout", "30", url],
        capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError("yt-dlp exit " + str(out.returncode))
    data = json.loads(out.stdout)
    posts = []
    photo_candidates = 0
    expanded_photos = 0

    for e in data.get("entries") or []:
        pid = str(e.get("id") or "")
        ts = e.get("timestamp")
        if not pid or not ts:
            continue

        raw_url = str(e.get("webpage_url") or e.get("url") or "")
        post_url = raw_url if raw_url.startswith("http") else f"https://www.tiktok.com/@{HANDLE}/video/{pid}"
        title = e.get("title") or ""
        looks_photo = "/photo/" in post_url or title.lower().startswith("tiktok photo")

        if looks_photo:
            photo_candidates += 1
            photo_url = post_url.replace("/video/", "/photo/") if "/photo/" not in post_url else post_url
            expanded = expand_tiktok_photo(pid, photo_url, int(ts), title)
            if expanded:
                posts.extend(expanded)
                expanded_photos += 1
                continue

        thumbs = e.get("thumbnails") or []
        img = None
        if thumbs:
            img = sorted(thumbs, key=lambda t: (t.get("width") or 0))[-1].get("url")
        if not img:
            continue
        posts.append(_media_record("tiktok", pid, ts, img, title, post_url))

    log("yt-dlp TikTok photo candidates:", photo_candidates, "| expanded:", expanded_photos)
    return posts

def from_tikwm():
    """TikTok primary source. A photo carousel becomes one record per image."""
    import requests
    r = requests.get("https://www.tikwm.com/api/user/posts",
                     params={"unique_id": HANDLE, "count": 50}, headers=UA, timeout=40)
    r.raise_for_status()
    posts = []
    for v in (r.json().get("data") or {}).get("videos") or []:
        pid = str(v.get("video_id") or "")
        ts = v.get("create_time")
        if not pid or not ts:
            continue
        images = [x for x in (v.get("images") or []) if x]
        is_photo = bool(images)
        if not images:
            cover = v.get("origin_cover") or v.get("cover")
            if cover:
                images = [cover]
        post_url = f"https://www.tiktok.com/@{HANDLE}/{'photo' if is_photo else 'video'}/{pid}"
        for idx, img in enumerate(images):
            posts.append(_media_record(
                "tiktok", pid, ts, img, v.get("title") or "", post_url, idx
            ))
    return posts

def _parse_timestamp(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip()
    if re.fullmatch(r"\d{8}", text):
        try:
            return int(datetime.strptime(text, "%Y%m%d").replace(tzinfo=timezone.utc).timestamp())
        except Exception:
            return None
    text = text.replace("Z", "+00:00")
    try:
        return int(datetime.fromisoformat(text).timestamp())
    except Exception:
        return None

def from_public_ytdlp(source, url, limit=30):
    """Best-effort public profile/page reader for Instagram or Facebook."""
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings",
         "--playlist-end", str(limit), "--socket-timeout", "30", url],
        capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        raise RuntimeError("yt-dlp exit " + str(out.returncode))
    data = json.loads(out.stdout)
    posts = []
    for e in data.get("entries") or []:
        pid = str(e.get("id") or e.get("display_id") or "")
        ts = _parse_timestamp(e.get("timestamp") or e.get("release_timestamp") or e.get("upload_date"))
        if not pid or not ts:
            continue
        thumbs = e.get("thumbnails") or []
        img = None
        if thumbs:
            img = sorted(thumbs, key=lambda t: (t.get("width") or 0))[-1].get("url")
        img = img or e.get("thumbnail")
        if not img:
            continue
        posts.append(_media_record(
            source, pid, ts, img, e.get("title") or e.get("description") or "",
            e.get("webpage_url") or e.get("url") or url
        ))
    return posts

def from_public_gallery_dl(source, url, limit=30):
    """Best-effort gallery-dl fallback for public Instagram/Facebook media."""
    rows = _gallery_dl(url, limit=limit, timeout=90)
    posts = []
    per_post_index = {}
    for media_url, meta in rows:
        ext = str(meta.get("extension") or "").lower().lstrip(".")
        if ext and ext not in ("jpg", "jpeg", "png", "webp", "avif", "heic"):
            continue
        pid = str(
            meta.get("post_id") or meta.get("shortcode") or meta.get("id")
            or meta.get("media_id") or ""
        )
        ts = _parse_timestamp(
            meta.get("timestamp") or meta.get("date") or meta.get("created_time")
        )
        if not pid or not ts or not media_url:
            continue
        idx = per_post_index.get(pid, 0)
        per_post_index[pid] = idx + 1
        title = (
            meta.get("description") or meta.get("caption")
            or meta.get("title") or ""
        )
        href = (
            meta.get("post_url") or meta.get("permalink")
            or meta.get("webpage_url") or url
        )
        posts.append(_media_record(source, pid, ts, media_url, title, href, idx))
    return posts


def _walk_attachment_images(node):
    """Yield image URLs from Facebook Graph API attachment trees."""
    if not isinstance(node, dict):
        return
    media = node.get("media") or {}
    image = media.get("image") or {}
    if image.get("src"):
        yield image["src"]
    for child in ((node.get("subattachments") or {}).get("data") or []):
        yield from _walk_attachment_images(child)

def from_meta_graph():
    """Official Instagram/Facebook import when optional GitHub secrets exist."""
    import requests
    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    ig_user = os.environ.get("INSTAGRAM_USER_ID", "").strip()
    fb_page = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
    if not token or not (ig_user or fb_page):
        return []

    base = os.environ.get("META_GRAPH_BASE", "https://graph.facebook.com").rstrip("/")
    posts = []

    if ig_user:
        r = requests.get(
            f"{base}/{ig_user}/media",
            params={
                "access_token": token,
                "limit": 30,
                "fields": "id,caption,media_type,media_url,permalink,timestamp,children{media_type,media_url,id}",
            },
            headers=UA, timeout=45)
        r.raise_for_status()
        for item in r.json().get("data") or []:
            pid = str(item.get("id") or "")
            ts = _parse_timestamp(item.get("timestamp"))
            if not pid or not ts:
                continue
            children = (item.get("children") or {}).get("data") or []
            images = [
                c.get("media_url") for c in children
                if c.get("media_url") and c.get("media_type") == "IMAGE"
            ]
            if not images and item.get("media_url") and item.get("media_type") == "IMAGE":
                images = [item["media_url"]]
            for idx, img in enumerate(images):
                posts.append(_media_record(
                    "instagram", pid, ts, img, item.get("caption") or "",
                    item.get("permalink") or f"https://www.instagram.com/{INSTAGRAM_HANDLE}/", idx
                ))

    if fb_page:
        r = requests.get(
            f"{base}/{fb_page}/posts",
            params={
                "access_token": token,
                "limit": 30,
                "fields": "id,message,created_time,permalink_url,full_picture,attachments{media,subattachments}",
            },
            headers=UA, timeout=45)
        r.raise_for_status()
        for item in r.json().get("data") or []:
            pid = str(item.get("id") or "")
            ts = _parse_timestamp(item.get("created_time"))
            if not pid or not ts:
                continue
            images = []
            for attachment in ((item.get("attachments") or {}).get("data") or []):
                images.extend(_walk_attachment_images(attachment))
            if not images and item.get("full_picture"):
                images = [item["full_picture"]]
            images = list(dict.fromkeys(x for x in images if x))
            for idx, img in enumerate(images):
                posts.append(_media_record(
                    "facebook", pid, ts, img, item.get("message") or "",
                    item.get("permalink_url") or FACEBOOK_URL, idx
                ))

    return posts

def fetch_full(pid):
    """Full metadata for one post: (title, description) or ('', '').
    Tries the /photo/ URL, then the /video/ URL (posts can be either)."""
    for kind in ("photo", "video"):
        try:
            out = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "-J", "--no-warnings",
                 "--socket-timeout", "20", f"https://www.tiktok.com/@{HANDLE}/{kind}/{pid}"],
                capture_output=True, text=True, timeout=120)
            if out.returncode != 0:
                continue
            d = json.loads(out.stdout)
            if d:
                return d.get("title") or "", d.get("description") or ""
        except Exception:
            continue
    return "", ""

MONTHS_BS = ["januar", "februar", "mart", "april", "maj", "juni", "juli",
             "august", "septembar", "oktobar", "novembar", "decembar"]

def clean_title(raw, date_s):
    t = re.sub(r"[#@]\S+", "", raw or "")
    t = re.sub(r"\s+", " ", t).strip(" -–—|")
    if t.lower() in ("tiktok video", "tiktok photo", "tiktok"):
        t = ""
    if len(t) < 4:
        try:
            d = datetime.strptime(date_s, "%Y-%m-%d")
            t = "Radionica, " + MONTHS_BS[d.month - 1] + " " + str(d.year)
        except Exception:
            t = "U radionici"
    return t[:48]

def source_of(entry):
    source = str(entry.get("source") or "").lower()
    if source in ("tiktok", "instagram", "facebook"):
        return source
    href = str(entry.get("href") or entry.get("url") or "").lower()
    if "instagram.com" in href:
        return "instagram"
    if "facebook.com" in href or "fb.watch" in href:
        return "facebook"
    return "tiktok"

def post_id_of(entry):
    if entry.get("post_id"):
        return str(entry["post_id"])
    href = str(entry.get("href") or entry.get("url") or "")
    source = source_of(entry)
    if source == "instagram":
        m = re.search(r"/(?:p|reel)/([^/?#]+)", href)
        return m.group(1) if m else None
    if source == "facebook":
        m = re.search(r"(?:story_fbid=|/posts/|/photos/(?:a\.[^/]+/)?)([^&/?#]+)", href)
        return m.group(1) if m else None
    m = re.search(r"/(\d{10,})(?:[/?#]|$)", href)
    return m.group(1) if m else None

def media_id_of(entry):
    if entry.get("media_id"):
        return str(entry["media_id"])
    pid = post_id_of(entry)
    return f"{source_of(entry)}:{pid}:0" if pid else None

def needs_quality_upgrade(pools, media_id):
    """True when a known media item still points at a pre-v2/thumbnail asset."""
    matches = []
    for pool in ("hero", "heroMobile", "gallery"):
        for entry in pools.get(pool, []):
            if media_id_of(entry) == media_id:
                matches.append(entry)
    return bool(matches) and any(int(entry.get("quality_v") or 0) < 2 for entry in matches)

def main():
    # TikTok: TikWM first because it exposes every image in photo carousels.
    tiktok_posts, tiktok_reader = [], None
    for name, fn in (("tikwm", from_tikwm), ("yt-dlp", from_ytdlp)):
        try:
            tiktok_posts = fn()
            if tiktok_posts:
                tiktok_reader = name
                break
            log(name, "returned no TikTok posts")
        except Exception as ex:
            log(name, "TikTok failed:", str(ex)[:160])

    meta_posts = []
    try:
        meta_posts = from_meta_graph()
        if meta_posts:
            log("Meta Graph media:", len(meta_posts))
    except Exception as ex:
        log("Meta Graph failed:", str(ex)[:160])

    meta_sources = {p["source"] for p in meta_posts}
    fallback_posts = []
    for social, url in (
        ("instagram", f"https://www.instagram.com/{INSTAGRAM_HANDLE}/"),
        ("facebook", FACEBOOK_URL),
    ):
        if social in meta_sources:
            continue
        got = []
        try:
            got = from_public_ytdlp(social, url)
        except Exception as ex:
            log(social, "yt-dlp public reader unavailable:", str(ex)[:100])
        if not got:
            try:
                got = from_public_gallery_dl(social, url)
            except Exception as ex:
                log(social, "gallery-dl public reader unavailable:", str(ex)[:100])
        if got:
            fallback_posts.extend(got)
            log(social, "public media:", len(got))
        else:
            log(social, "public readers returned no media")

    posts = tiktok_posts + meta_posts + fallback_posts
    dedup = {}
    for p in posts:
        dedup[p["media_id"]] = p
    posts = list(dedup.values())

    if not posts:
        log("all social sources failed; leaving the site unchanged")
        return 0

    counts = {}
    for p in posts:
        counts[p["source"]] = counts.get(p["source"], 0) + 1
    log("media fetched:", counts, "| TikTok reader:", tiktok_reader)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    by_post = {}
    for p in posts:
        p["date"] = datetime.fromtimestamp(p["ts"], timezone.utc).strftime("%Y-%m-%d")
        by_post[(p["source"], p["post_id"])] = p

    tiktok_post_ids = {p["post_id"] for p in tiktok_posts}
    tiktok_dates = [
        datetime.fromtimestamp(p["ts"], timezone.utc).strftime("%Y-%m-%d")
        for p in tiktok_posts
    ]
    oldest_tiktok = min(tiktok_dates) if tiktok_dates else None

    fresh = [p for p in posts if datetime.fromtimestamp(p["ts"], timezone.utc) >= cutoff]
    fresh.sort(key=lambda p: (-p["ts"], p.get("media_index", 0)))
    log("media within", MAX_AGE_DAYS, "days:", len(fresh))

    with open(PHOTOS_JSON, encoding="utf-8") as f:
        pools = json.load(f)
    for pool in ("hero", "heroMobile", "gallery"):
        pools.setdefault(pool, [])

    known = set()
    known_tiktok_posts = set()
    for pool in ("hero", "heroMobile", "gallery"):
        for e in pools[pool]:
            mid = media_id_of(e)
            if mid:
                known.add(mid)
            if source_of(e) == "tiktok":
                pid = post_id_of(e)
                if pid:
                    known_tiktok_posts.add(pid)

    # yt-dlp's TikTok profile extractor currently exposes slideshow posts as
    # ordinary /video/ entries. Probe only new/recent IDs against /photo/,
    # cache the outcome, and back off on transient failures so the 15-minute
    # schedule never hammers TikTok.
    carousel_probe = pools.get("_carousel_probe") or {}
    probe_now = int(now.timestamp())
    probe_cutoff = probe_now - 2 * 24 * 3600
    unique_tiktok = {}
    for p in fresh:
        if p.get("source") == "tiktok":
            unique_tiktok.setdefault(p["post_id"], p)

    def post_needs_quality_upgrade(post_id):
        for pool in ("hero", "heroMobile", "gallery"):
            for entry in pools.get(pool, []):
                if source_of(entry) == "tiktok" and post_id_of(entry) == post_id:
                    if int(entry.get("quality_v") or 0) < 2:
                        return True
        return False

    known_photo_posts_needing_upgrade = set()
    for entry in pools.get("gallery", []):
        if (
            source_of(entry) == "tiktok"
            and "/photo/" in str(entry.get("href") or "")
            and int(entry.get("quality_v") or 0) < 2
        ):
            pid = post_id_of(entry)
            if pid:
                known_photo_posts_needing_upgrade.add(pid)

    candidates = sorted(unique_tiktok.values(), key=lambda p: -p["ts"])
    candidates = [
        p for p in candidates
        if (
            p["post_id"] in known_photo_posts_needing_upgrade
            or (
                p["post_id"] not in carousel_probe
                and (p["post_id"] not in known_tiktok_posts or p["ts"] >= probe_cutoff)
            )
            or (
                (carousel_probe.get(p["post_id"]) or {}).get("status") == "photo"
                and post_needs_quality_upgrade(p["post_id"])
            )
        )
    ][:25]

    expanded_by_media = {p["media_id"]: p for p in fresh}
    for p in candidates:
        pid = p["post_id"]
        photo_url = f"https://www.tiktok.com/@{HANDLE}/photo/{pid}"
        expanded = expand_tiktok_photo(pid, photo_url, p["ts"], p.get("title", ""))
        if expanded is None:
            previous = carousel_probe.get(pid) or {}
            attempts = int(previous.get("attempts") or 0) + 1
            carousel_probe[pid] = {
                "status": "retry" if attempts < 3 else "backoff",
                "attempts": attempts,
                "last": probe_now,
            }
            continue

        for item in expanded:
            item["date"] = p["date"]
            expanded_by_media[item["media_id"]] = item
        carousel_probe[pid] = {
            "status": "photo" if expanded else "not-photo",
            "count": len(expanded),
            "attempts": 1,
            "last": probe_now,
        }
        if expanded:
            log("TikTok carousel resolved:", pid, "| images:", len(expanded))

    # Retry transiently blocked probes after a 24-hour cool-down.
    for pid, state in list(carousel_probe.items()):
        if state.get("status") == "backoff" and probe_now - int(state.get("last") or 0) >= 24 * 3600:
            carousel_probe.pop(pid, None)
    pools["_carousel_probe"] = carousel_probe

    fresh = list(expanded_by_media.values())
    fresh.sort(key=lambda p: (-p["ts"], p.get("media_index", 0)))

    def cat_for(p, allow_fetch, entry_title=""):
        c = classify(p.get("raw", ""))
        if c != "opcenito":
            return c, True
        if entry_title and not entry_title.startswith("Radionica, "):
            c = classify(entry_title)
            if c != "opcenito":
                return c, True
        if allow_fetch and p.get("source") == "tiktok":
            t, desc = fetch_full(p["post_id"])
            if t:
                p["title"] = t
            return classify((t or "") + " " + (desc or "")), True
        return "opcenito", True

    import requests
    from PIL import Image
    os.makedirs(PHOTO_DIR, exist_ok=True)
    added = 0
    upgraded = 0

    for p in fresh:
        is_known = p["media_id"] in known
        upgrade_existing = (
            is_known
            and p.get("quality_source") == "original"
            and needs_quality_upgrade(pools, p["media_id"])
        )
        if is_known and not upgrade_existing:
            continue
        cat, cat_ok = cat_for(p, allow_fetch=True)
        try:
            resp = requests.get(p["img"], headers=UA, timeout=40)
            resp.raise_for_status()
            im = Image.open(BytesIO(resp.content)).convert("RGB")
        except Exception as ex:
            log("download failed for", p["media_id"], str(ex)[:120])
            continue

        short = hashlib.sha1(p["media_id"].encode("utf-8")).hexdigest()[:8]
        tag = p["date"].replace("-", "") + "-" + short
        prefix = {"tiktok": "tt", "instagram": "ig", "facebook": "fb"}.get(p["source"], "social")

        # Keep the source photo sharp. Never upscale, blur, or crop it just to
        # fill a frame; CSS handles the surrounding branded background.
        portrait = im.copy()
        max_edge = max(portrait.width, portrait.height)
        if max_edge > 2200:
            scale = 2200 / max_edge
            portrait = portrait.resize(
                (round(portrait.width * scale), round(portrait.height * scale)),
                Image.LANCZOS,
            )
        pfile = f"{prefix}-{tag}.webp"
        portrait.save(os.path.join(PHOTO_DIR, pfile), "WEBP", quality=92, method=6)

        wide = im.copy()
        wide_edge = max(wide.width, wide.height)
        if wide_edge > 2400:
            scale = 2400 / wide_edge
            wide = wide.resize(
                (round(wide.width * scale), round(wide.height * scale)),
                Image.LANCZOS,
            )
        wfile = f"{prefix}-wide-{tag}.webp"
        wide.save(os.path.join(PHOTO_DIR, wfile), "WEBP", quality=92, method=6)

        if upgrade_existing:
            portrait_src = f"assets/photos/{pfile}"
            wide_src = f"assets/photos/{wfile}"
            for entry in pools.get("gallery", []):
                if media_id_of(entry) == p["media_id"]:
                    entry["src"] = portrait_src
                    entry["quality_v"] = 2
            for entry in pools.get("heroMobile", []):
                if media_id_of(entry) == p["media_id"]:
                    entry["src"] = portrait_src
                    entry["quality_v"] = 2
            for entry in pools.get("hero", []):
                if media_id_of(entry) == p["media_id"]:
                    entry["src"] = wide_src
                    entry["quality_v"] = 2
            upgraded += 1
            log("upgraded full-quality media", p["media_id"], "|", im.size)
            continue

        title = clean_title(p["title"], p["date"])
        common = {
            "href": p["url"],
            "title": title,
            "date": p["date"],
            "cat": cat,
            "source": p["source"],
            "post_id": p["post_id"],
            "media_id": p["media_id"],
            "media_index": p["media_index"],
            "quality_v": 2,
        }

        pools["gallery"].insert(0, {
            **common,
            "src": f"assets/photos/{pfile}",
            "cat_checked": cat_ok,
            "cat_v": cat_ok,
        })
        pools["hero"].insert(0, {**common, "src": f"assets/photos/{wfile}"})
        pools["heroMobile"].insert(0, {**common, "src": f"assets/photos/{pfile}"})
        known.add(p["media_id"])
        added += 1
        log("added", p["media_id"], p["date"], "| cat:", cat, "|", title)

    for pool in ("hero", "heroMobile", "gallery"):
        for e in pools[pool]:
            e.setdefault("source", source_of(e))
            pid = post_id_of(e)
            if pid:
                e.setdefault("post_id", pid)
                e.setdefault("media_id", f"{e['source']}:{pid}:0")
                e.setdefault("media_index", 0)

            if e.get("title") in ("U radionici", "TikTok video", "TikTok photo"):
                e["title"] = clean_title("", e.get("date", ""))

            key = (e.get("source"), pid)
            if pid and key in by_post and not e.get("cat_v"):
                e["cat"], ok = cat_for(by_post[key], allow_fetch=True, entry_title=e.get("title", ""))
                e["cat_checked"] = ok
                e["cat_v"] = ok
                if e.get("title", "").startswith("Radionica, "):
                    better = clean_title(by_post[key].get("title", ""), e.get("date", ""))
                    if not better.startswith("Radionica, "):
                        e["title"] = better

    removed = 0
    missing_map = pools.get("_missing") or {}
    if len(tiktok_post_ids) >= 25 and oldest_tiktok:
        candidates = set()
        for pool in ("hero", "heroMobile", "gallery"):
            for e in pools[pool]:
                if source_of(e) != "tiktok":
                    continue
                pid = post_id_of(e)
                if pid and pid not in tiktok_post_ids and e.get("date", "9999") >= oldest_tiktok:
                    candidates.add(pid)

        confirmed_gone = set()
        for pid in candidates:
            t, desc = fetch_full(pid)
            if t or desc:
                log("kept (missing from TikTok list but direct post resolves):", pid)
                missing_map.pop(pid, None)
                continue
            missing_map[pid] = int(missing_map.get(pid, 0)) + 1
            if missing_map[pid] >= 2:
                confirmed_gone.add(pid)
            else:
                log("missing TikTok strike 1; verifying again next run:", pid)

        if confirmed_gone:
            for pool in ("hero", "heroMobile", "gallery"):
                keep = []
                for e in pools[pool]:
                    pid = post_id_of(e)
                    if source_of(e) == "tiktok" and pid in confirmed_gone:
                        removed += 1
                        src = e.get("src", "")
                        base = os.path.basename(src)
                        if re.match(r"tt(?:-wide)?-\d{8}-[A-Za-z0-9]+\.webp$", base):
                            fp = os.path.join(ROOT, src)
                            if os.path.isfile(fp):
                                os.remove(fp)
                        log("removed deleted TikTok media:", pid, src)
                        continue
                    keep.append(e)
                pools[pool] = keep
            for pid in confirmed_gone:
                missing_map.pop(pid, None)
    pools["_missing"] = missing_map

    retired = 0
    minimums = {"hero": 1, "heroMobile": 1, "gallery": 5}
    for pool, minimum in minimums.items():
        entries = pools.get(pool, [])
        entries.sort(
            key=lambda e: (e.get("date", ""), -(int(e.get("media_index") or 0))),
            reverse=True,
        )
        keep, drop = [], []
        for e in entries:
            d = e.get("date")
            fresh_e = False
            if d:
                try:
                    fresh_e = datetime.strptime(d, "%Y-%m-%d").replace(
                        tzinfo=timezone.utc
                    ) >= cutoff
                except ValueError:
                    pass
            if fresh_e or len(keep) < minimum:
                keep.append(e)
            else:
                drop.append(e)
        pools[pool] = keep
        for e in drop:
            retired += 1
            fp = os.path.join(ROOT, e.get("src", ""))
            if os.path.isfile(fp):
                os.remove(fp)
                log("retired (too old)", e["src"])

    services = {}
    gal = pools.get("gallery", [])
    for cat in CATS:
        cands = [e for e in gal if e.get("cat") == cat]
        if cands:
            cands.sort(
                key=lambda e: (e.get("date", ""), -(int(e.get("media_index") or 0))),
                reverse=True,
            )
            services[cat] = {
                "src": cands[0]["src"],
                "date": cands[0]["date"],
                "href": cands[0]["href"],
                "source": source_of(cands[0]),
            }
    pools["services"] = services

    if gal:
        newest = sorted(
            gal,
            key=lambda e: (e.get("date", ""), -(int(e.get("media_index") or 0))),
            reverse=True,
        )[0]
        wide_src = newest["src"]
        newest_mid = media_id_of(newest)
        for e in pools.get("hero", []):
            if media_id_of(e) == newest_mid:
                wide_src = e["src"]
                break
        pools["latest"] = {
            "src": newest["src"],
            "wide": wide_src,
            "href": newest["href"],
            "title": newest["title"],
            "date": newest["date"],
            "cat": newest.get("cat", "opcenito"),
            "source": source_of(newest),
            "post_id": post_id_of(newest),
            "media_id": newest_mid,
        }

    log("services map:", {k: v["date"] for k, v in services.items()})
    log("latest:", pools.get("latest", {}).get("date"), pools.get("latest", {}).get("title"))

    with open(PHOTOS_JSON, "w", encoding="utf-8") as f:
        json.dump(pools, f, ensure_ascii=False, indent=1)

    log(
        "done. added:", added,
        "| upgraded:", upgraded,
        "| removed:", removed,
        "| retired:", retired,
        "| pool sizes:", {k: len(pools.get(k, [])) for k in minimums},
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
