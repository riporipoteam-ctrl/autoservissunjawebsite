#!/usr/bin/env python3
"""Auto fresh-photos for autosunja.sitey.my — v2.

Runs from GitHub Actions (see .github/workflows/fresh-photos.yml, every
15 min). Pulls the shop's newest TikTok posts (@autoservissunja),
mirrors images into assets/photos/, and keeps photos.json pools (hero,
heroMobile, gallery) limited to posts at most 60 days old.
v2 adds: post categories (from caption/hashtags) feeding the matching
service tab on the site, deletion sync (a post deleted on TikTok is
removed from the site too), and a "latest" pointer so the site can
feature the newest photo first.
Fail-soft: if every source fails, nothing changes and the run passes.
"""
import json, os, re, subprocess, sys, unicodedata
from datetime import datetime, timezone, timedelta
from io import BytesIO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_JSON = os.path.join(ROOT, "photos.json")
PHOTO_DIR = os.path.join(ROOT, "assets", "photos")
HANDLE = "autoservissunja"
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
                      "title": e.get("title") or "", "raw": e.get("title") or "",
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
                      "title": v.get("title") or "", "raw": v.get("title") or "",
                      "url": f"https://www.tiktok.com/@{HANDLE}/{'photo' if is_photo else 'video'}/{pid}"})
    return posts

def vision_cat(img_url):
    """Ask a free vision model which service category a photo shows.
    Returns a category word, or None when the service did not answer."""
    import requests
    prompt = ("Look at this car repair workshop photo and reply with exactly one word, the category: "
              "kljucevi = car keys, key fob or key programming device; "
              "dijagnostika = diagnostic tablet or computer used on a car; "
              "elektrika = ECU circuit board, wiring or battery; "
              "veliki = engine internals, timing belt or cylinder head; "
              "mali = oil change, filters, brakes or general servicing; "
              "peugeot = a Peugeot car as the main subject; "
              "opcenito = anything else.")
    try:
        r = requests.post("https://text.pollinations.ai/openai",
                          json={"model": "openai", "messages": [{"role": "user", "content": [
                              {"type": "text", "text": prompt},
                              {"type": "image_url", "image_url": {"url": img_url}}]}]},
                          timeout=90)
        r.raise_for_status()
        txt = (r.json()["choices"][0]["message"]["content"] or "").strip().lower()
        for cat in CATS + ["opcenito"]:
            if cat in txt:
                return cat
        log("vision answered unrecognised:", txt[:60])
    except Exception as ex:
        log("vision failed:", str(ex)[:100])
    return None

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
    if (raw or "").strip().lower() in ("tiktok video", "tiktok photo", "tiktok"):
        raw = ""
    t = re.sub(r"[#@]\S+", "", raw or "")
    t = re.sub(r"\s+", " ", t).strip(" -–—|")
    if len(t) < 4:
        try:
            d = datetime.strptime(date_s, "%Y-%m-%d")
            t = "Radionica, " + MONTHS_BS[d.month - 1] + " " + str(d.year)
        except Exception:
            t = "U radionici"
    return t[:48]

def post_id_of(entry):
    m = re.search(r"/(\d{10,})(?:[/?#]|$)", entry.get("href", ""))
    return m.group(1) if m else None

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
    by_id = {}
    for p in posts:
        p["date"] = datetime.fromtimestamp(p["ts"], timezone.utc).strftime("%Y-%m-%d")
        by_id[p["id"]] = p
    fetched_ids = set(by_id)
    oldest_fetched = min(p["date"] for p in posts)
    fresh = [p for p in posts if datetime.fromtimestamp(p["ts"], timezone.utc) >= cutoff]
    fresh.sort(key=lambda p: -p["ts"])
    log("posts within", MAX_AGE_DAYS, "days:", len(fresh))

    with open(PHOTOS_JSON, encoding="utf-8") as f:
        pools = json.load(f)
    for pool in ("hero", "heroMobile", "gallery"):
        pools.setdefault(pool, [])

    known = set()
    for pool in ("hero", "heroMobile", "gallery"):
        for e in pools[pool]:
            pid = post_id_of(e)
            if pid:
                known.add(pid)

    # classification: caption text -> known entry title -> full metadata -> vision.
    # Returns (category, definitive). Not definitive = retry on a later run.
    def cat_for(p, allow_fetch, entry_title=""):
        c = classify(p.get("raw", ""))
        if c != "opcenito":
            return c, True
        if entry_title and not entry_title.startswith("Radionica, "):
            c = classify(entry_title)
            if c != "opcenito":
                return c, True
        if allow_fetch:
            t, desc = fetch_full(p["id"])
            if t:
                p["title"] = t
            c = classify((t or "") + " " + (desc or ""))
            if c != "opcenito":
                return c, True
            vc = vision_cat(p.get("img", ""))
            if vc is not None:
                return vc, True
            return "opcenito", False
        return "opcenito", False

    # add new posts
    import requests
    from PIL import Image, ImageFilter
    os.makedirs(PHOTO_DIR, exist_ok=True)
    added = 0
    for p in fresh:
        if p["id"] in known:
            continue
        cat, cat_ok = cat_for(p, allow_fetch=True)
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
        portrait.save(os.path.join(PHOTO_DIR, pfile), "WEBP", quality=80, method=6)
        tw, th = 1600, 1000
        wide = im.copy()
        s = max(tw / wide.width, th / wide.height)
        wide = wide.resize((round(wide.width * s), round(wide.height * s)), Image.LANCZOS)
        x = (wide.width - tw) // 2
        y = (wide.height - th) // 2
        wide = wide.crop((x, y, x + tw, y + th)).filter(ImageFilter.GaussianBlur(30))
        fg = im.copy()
        s2 = min(tw / fg.width, th / fg.height)
        fg = fg.resize((round(fg.width * s2), round(fg.height * s2)), Image.LANCZOS)
        wide.paste(fg, ((tw - fg.width) // 2, (th - fg.height) // 2))
        wfile = f"tt-wide-{tag}.webp"
        wide.save(os.path.join(PHOTO_DIR, wfile), "WEBP", quality=79, method=6)
        title = clean_title(p["title"], p["date"])
        pools["gallery"].insert(0, {"src": f"assets/photos/{pfile}", "href": p["url"], "title": title, "date": p["date"], "cat": cat, "cat_checked": cat_ok})
        pools["hero"].insert(0, {"src": f"assets/photos/{wfile}", "href": p["url"], "title": title, "date": p["date"], "cat": cat})
        pools["heroMobile"].insert(0, {"src": f"assets/photos/{pfile}", "href": p["url"], "title": title, "date": p["date"], "cat": cat})
        known.add(p["id"])
        added += 1
        log("added", p["id"], p["date"], "| cat:", cat, "|", title)

    # backfill categories + repair fallback titles on known entries
    for pool in ("hero", "heroMobile", "gallery"):
        for e in pools[pool]:
            pid = post_id_of(e)
            if e.get("title") in ("U radionici", "TikTok video", "TikTok photo"):
                e["title"] = clean_title("", e.get("date", ""))
            if pid and pid in by_id and not e.get("cat_checked"):
                e["cat"], e["cat_checked"] = cat_for(by_id[pid], allow_fetch=True, entry_title=e.get("title", ""))
                if e.get("title", "").startswith("Radionica, "):
                    better = clean_title(by_id[pid].get("title", ""), e.get("date", ""))
                    if not better.startswith("Radionica, "):
                        e["title"] = better

    # deletion sync: post gone from TikTok -> gone from the site.
    # Careful on purpose: a post must be missing from the profile list AND
    # unresolvable at its direct URL on two consecutive runs before removal.
    removed = 0
    missing_map = pools.get("_missing") or {}
    if len(posts) >= 50:
        candidates = set()
        for pool in ("hero", "heroMobile", "gallery"):
            for e in pools[pool]:
                pid = post_id_of(e)
                if pid and pid not in fetched_ids and e.get("date", "9999") >= oldest_fetched:
                    candidates.add(pid)
        confirmed_gone = set()
        for pid in candidates:
            t, desc = fetch_full(pid)
            if t or desc:
                log("kept (missing from list but post still resolvable):", pid)
                missing_map.pop(pid, None)
                continue
            missing_map[pid] = int(missing_map.get(pid, 0)) + 1
            if missing_map[pid] >= 2:
                confirmed_gone.add(pid)
            else:
                log("missing strike 1 (will verify once more before removing):", pid)
        if confirmed_gone:
            for pool in ("hero", "heroMobile", "gallery"):
                keep = []
                for e in pools[pool]:
                    pid = post_id_of(e)
                    if pid in confirmed_gone:
                        removed += 1
                        src = e.get("src", "")
                        base = os.path.basename(src)
                        if re.match(r"tt-\d{8}-\d+\.webp$", base) or re.match(r"tt-wide-\d{8}-\d+\.webp$", base):
                            fp = os.path.join(ROOT, src)
                            if os.path.isfile(fp):
                                os.remove(fp)
                        log("removed (post deleted on TikTok, verified twice):", pid, src)
                        continue
                    keep.append(e)
                pools[pool] = keep
            for pid in confirmed_gone:
                missing_map.pop(pid, None)
    pools["_missing"] = missing_map

    # prune by age (keep pool minimums with the newest)
    retired = 0
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
            retired += 1
            fp = os.path.join(ROOT, e.get("src", ""))
            if os.path.isfile(fp):
                os.remove(fp)
                log("retired (too old)", e["src"])

    # services map: newest photo per category (drives the service tabs)
    services = {}
    gal = pools.get("gallery", [])
    for cat in CATS:
        cands = [e for e in gal if e.get("cat") == cat]
        if cands:
            cands.sort(key=lambda e: e.get("date", ""), reverse=True)
            services[cat] = {"src": cands[0]["src"], "date": cands[0]["date"], "href": cands[0]["href"]}
    pools["services"] = services

    # latest post overall (the site features it first)
    if gal:
        newest = sorted(gal, key=lambda e: e.get("date", ""), reverse=True)[0]
        wide_src = newest["src"]
        for e in pools.get("hero", []):
            if post_id_of(e) == post_id_of(newest):
                wide_src = e["src"]
                break
        pools["latest"] = {"src": newest["src"], "wide": wide_src, "href": newest["href"],
                           "title": newest["title"], "date": newest["date"], "cat": newest.get("cat", "opcenito")}
    log("services map:", {k: v["date"] for k, v in services.items()})
    log("latest:", pools.get("latest", {}).get("date"), pools.get("latest", {}).get("title"))

    with open(PHOTOS_JSON, "w", encoding="utf-8") as f:
        json.dump(pools, f, ensure_ascii=False, indent=1)
    log("done. added:", added, "| removed:", removed, "| retired:", retired,
        "| pool sizes:", {k: len(pools.get(k, [])) for k in minimums})
    return 0

if __name__ == "__main__":
    sys.exit(main())
