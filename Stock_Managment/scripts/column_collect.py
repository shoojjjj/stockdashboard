#!/usr/bin/env python3
"""네이버 프리미엄(자산제곱) 신규 칼럼 → 아카이브/칼럼/*.md 자동 저장."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT.parent
COLUMN_DIR = ARCHIVE / "칼럼"
DATA_DIR = ROOT / "data"
INDEX_FILE = DATA_DIR / "column_index.json"
ENV_FILE = ROOT / "column_collect.env"

BASE = "https://contents.premium.naver.com/assetx2/assetsx2"
LIST_URL = f"{BASE}/contents"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

CATEGORY_MAP = {
    "자산네제곱 프로젝트": "자산네제곱 프로젝트",
    "투자전략": "투자 전략",
    "투자 전략": "투자 전략",
    "시나리오": "시나리오",
    "시장 리포트": "시장 리포트",
    "기술적 분석 프로젝트": "기술적 분석 프로젝트",
    "기술적 분석": "기술적 분석 프로젝트",
}

SOURCE_RE = re.compile(
    r"contents\.premium\.naver\.com/assetx2/assetsx2/contents/([a-z0-9]{15,25})"
)


def safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        print(text.encode(enc, errors="replace").decode(enc, errors="replace"))


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def load_cookie() -> str:
    load_env_file(ENV_FILE)
    raw = os.environ.get("NAVER_COOKIE", "").strip()
    if raw:
        return raw
    cookie_file = os.environ.get("NAVER_COOKIE_FILE", "").strip()
    if cookie_file and Path(cookie_file).exists():
        return Path(cookie_file).read_text(encoding="utf-8").strip()
    return ""


def fetch_url(url: str, cookie: str = "") -> str:
    headers = {"User-Agent": UA, "Referer": "https://contents.premium.naver.com/"}
    if cookie:
        headers["Cookie"] = cookie
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as res:
        return res.read().decode("utf-8", "replace")


def load_known_ids() -> set[str]:
    known: set[str] = set()
    if INDEX_FILE.exists():
        try:
            data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            known.update(data.get("ids", []))
        except json.JSONDecodeError:
            pass
    if COLUMN_DIR.exists():
        for md in COLUMN_DIR.rglob("*.md"):
            text = md.read_text(encoding="utf-8", errors="replace")
            known.update(SOURCE_RE.findall(text))
            m = re.search(r"^source_id:\s*(\S+)", text, re.M)
            if m:
                known.add(m.group(1))
    return known


def parse_listing(html: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    seen: set[str] = set()

    card_pattern = re.compile(
        r'href="/assetx2/assetsx2/contents/([a-z0-9]{15,25})"[^>]*class="[^"]*content[^"]*link',
        re.I,
    )
    for m in card_pattern.finditer(html):
        cid = m.group(1)
        if cid in seen:
            continue
        seen.add(cid)
        items.append({"id": cid, "title": "", "category": ""})

    title_pattern = re.compile(
        r'href="/assetx2/assetsx2/contents/([a-z0-9]{15,25})"[^>]*>\s*'
        r'(?:<[^>]+>\s*)*<[^>]*content_title[^>]*>(.*?)</',
        re.S | re.I,
    )
    for m in title_pattern.finditer(html):
        cid, title_html = m.group(1), m.group(2)
        title = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", title_html))).strip()
        for item in items:
            if item["id"] == cid and title:
                item["title"] = title

    if not items:
        for cid in re.findall(r"/assetx2/assetsx2/contents/([a-z0-9]{15,25})", html):
            if cid not in seen:
                seen.add(cid)
                items.append({"id": cid, "title": "", "category": ""})

    return items


def fetch_listing_pages(max_pages: int) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        url = LIST_URL if page == 1 else f"{LIST_URL}?page={page}"
        try:
            html = fetch_url(url)
        except urllib.error.HTTPError as e:
            safe_print(f"WARN listing page {page}: HTTP {e.code}")
            break
        batch = parse_listing(html)
        if not batch:
            break
        new_on_page = 0
        for item in batch:
            if item["id"] not in seen:
                seen.add(item["id"])
                merged.append(item)
                new_on_page += 1
        if page > 1 and new_on_page == 0:
            break
        time.sleep(0.4)
    return merged


def meta_content(html: str, name: str) -> str:
    m = re.search(
        rf'<meta\s+(?:name|property)="{re.escape(name)}"\s+content="([^"]*)"',
        html,
        re.I,
    )
    return unescape(m.group(1)) if m else ""


def parse_publish_date(html: str) -> tuple[str, str]:
    iso_raw = meta_content(html, "publish-datetime")
    if iso_raw:
        try:
            dt = datetime.fromisoformat(iso_raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            local = dt.astimezone()
            return local.date().isoformat(), local.strftime("%B %d, %Y")
        except ValueError:
            pass
    m = re.search(r'class="viewer_date"[^>]*>([^<]+)<', html)
    if m:
        nums = re.findall(r"\d+", m.group(1))
        if len(nums) >= 3:
            y, mo, d = int(nums[0]), int(nums[1]), int(nums[2])
            dt = datetime(y, mo, d)
            return dt.date().isoformat(), dt.strftime("%B %d, %Y")
    return "", ""


def map_category(raw: str) -> str:
    raw = raw.strip()
    return CATEGORY_MAP.get(raw, raw or "투자 전략")


def span_to_md(html: str) -> str:
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)

    def link_repl(m: re.Match[str]) -> str:
        href = m.group(1)
        label = re.sub(r"<[^>]+>", "", m.group(2))
        label = unescape(label).strip()
        return f"[{label}]({href})" if label else href

    html = re.sub(
        r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        link_repl,
        html,
        flags=re.S | re.I,
    )
    html = re.sub(
        r"<(?:b|strong)[^>]*>(.*?)</(?:b|strong)>",
        r"**\1**",
        html,
        flags=re.S | re.I,
    )
    html = re.sub(r"<[^>]+>", "", html)
    return unescape(html).replace("\xa0", " ").strip()


def extract_main_html(html: str) -> str:
    start = html.find('<div class="se-main-container">')
    if start == -1:
        return ""
    start += len('<div class="se-main-container">')
    paywall = html.find("viewer_paywall", start)
    end = paywall if paywall != -1 else html.find("<!-- SE_DOC_FOOTER", start)
    if end == -1:
        end = html.find('<div class="viewer_bottom', start)
    if end == -1:
        end = len(html)
    return html[start:end]


def html_to_markdown(main_html: str) -> str:
    lines: list[str] = []
    components = re.split(r'<div class="se-component ', main_html)
    for comp in components[1:]:
        if comp.startswith("se-section-title") or "se-section-title" in comp[:80]:
            m = re.search(r"se-text-paragraph[^>]*>(.*?)</p>", comp, re.S)
            if m:
                text = span_to_md(m.group(1))
                if text:
                    lines.extend(["", f"**{text}**", ""])
            continue
        if "se-image" in comp[:40] or "se-module-image" in comp:
            m = re.search(r'(?:data-src|src)="([^"]+)"', comp)
            if m:
                url = unescape(m.group(1))
                lines.extend(["", f"![]({url})", ""])
            continue
        if "se-quotation" in comp[:60]:
            m = re.search(r"se-text-paragraph[^>]*>(.*?)</p>", comp, re.S)
            if m:
                text = span_to_md(m.group(1))
                if text:
                    lines.extend(["", f"> {text}", ""])
            continue
        if "se-text" in comp[:40]:
            for m in re.finditer(r"se-text-paragraph[^>]*>(.*?)</p>", comp, re.S):
                text = span_to_md(m.group(1))
                if not text or text == "\u200b":
                    lines.append("")
                else:
                    lines.append(text)
            continue
        if "se-oglink" in comp or "se-module-oglink" in comp:
            m = re.search(r'href="([^"]+)"', comp)
            title_m = re.search(r'class="[^"]*oglink_title[^"]*"[^>]*>([^<]+)<', comp)
            if m:
                url = m.group(1)
                title = unescape(title_m.group(1)).strip() if title_m else url
                lines.extend(["", f"[{title}]({url})", ""])

    out: list[str] = []
    blank = 0
    for line in lines:
        if not line.strip():
            blank += 1
            if blank <= 1:
                out.append("")
            continue
        blank = 0
        out.append(line.rstrip())
    return "\n".join(out).strip()


def looks_incomplete(html: str, body: str) -> bool:
    if "viewer_paywall" not in html:
        return False
    if 'data-is-membership="true"' in html or 'data-content-auth="true"' in html:
        return False
    m = re.search(r'"total_text_length":"(\d+)"', html)
    if not m:
        return len(body) < 800
    expected = int(m.group(1))
    return len(body) < expected * 0.45


def parse_article(html: str, content_id: str) -> dict[str, str]:
    title = meta_content(html, "og:title") or meta_content(html, "twitter:title")
    if not title:
        m = re.search(r"se-title-text.*?<span[^>]*>([^<]+)</span>", html, re.S)
        title = unescape(m.group(1)).strip() if m else content_id

    cat_m = re.search(r'class="viewer_category_link"[^>]*>([^<]+)<', html)
    category = map_category(unescape(cat_m.group(1)).strip() if cat_m else "투자 전략")

    date_iso, date_label = parse_publish_date(html)
    main = extract_main_html(html)
    body = html_to_markdown(main)
    source_url = f"{BASE}/contents/{content_id}"

    return {
        "id": content_id,
        "title": title,
        "category": category,
        "date_iso": date_iso,
        "date_label": date_label,
        "body": body,
        "source_url": source_url,
        "incomplete": looks_incomplete(html, body),
    }


def safe_filename(title: str) -> str:
    name = title.strip()
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "")
    name = name.replace("\n", " ").strip()
    return name[:180] if name else "untitled"


def status_value(category: str) -> str:
    if category == "투자 전략":
        return "투자전략"
    return category


def build_markdown(article: dict[str, str]) -> str:
    date_label = article["date_label"] or datetime.now().strftime("%B %d, %Y")
    title = article["title"]
    body = article["body"]
    source = article["source_url"]
    category = article["category"]
    imported = datetime.now().astimezone().isoformat(timespec="seconds")

    md = f"""---
tags:
  - 자산제곱
Date: {date_label}
Status:
  - {status_value(category)}
source_url: {source}
source_id: {article["id"]}
source_platform: naver_premium
imported_at: {imported}
---
# {title}

{body}

Source: <{source}>
"""
    return md


def save_article(article: dict[str, str]) -> Path:
    folder = COLUMN_DIR / article["category"]
    folder.mkdir(parents=True, exist_ok=True)
    stem = safe_filename(article["title"])
    path = folder / f"{stem}.md"
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="replace")
        if article["id"] in text:
            return path
        path = folder / f"{stem}_{article['id'][:6]}.md"
    path.write_text(build_markdown(article), encoding="utf-8")
    return path


def save_index(all_ids: set[str], latest: dict[str, str] | None) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "total": len(all_ids),
        "ids": sorted(all_ids),
        "latest_id": latest.get("id") if latest else "",
        "latest_title": latest.get("title") if latest else "",
        "latest_date": latest.get("date_iso") if latest else "",
    }
    INDEX_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="네이버 프리미엄 자산제곱 칼럼 자동 저장")
    parser.add_argument("--list-pages", type=int, default=int(os.getenv("COLUMN_LIST_PAGES", "3")))
    parser.add_argument("--new-limit", type=int, default=int(os.getenv("COLUMN_NEW_LIMIT", "10")))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cookie = load_cookie()
    known = load_known_ids()
    safe_print(f"column_collect: known {len(known)} articles")

    listing = fetch_listing_pages(args.list_pages)
    safe_print(f"listing scanned: {len(listing)} items ({args.list_pages} page(s))")

    new_items = [x for x in listing if x["id"] not in known]
    safe_print(f"new candidates: {len(new_items)}")

    if not new_items:
        save_index(known, None)
        safe_print("column_collect done (no new articles)")
        return 0

    if not cookie:
        safe_print("ERROR: NAVER_COOKIE missing — full article needs login cookie.")
        safe_print(f"  Setup: copy {ENV_FILE.name}.example → {ENV_FILE.name}")
        safe_print("  Chrome → 네이버 로그인(구독) → DevTools → Network → Cookie 복사")
        for item in new_items[:5]:
            safe_print(f"  pending: {item['id']} {item.get('title','')}")
        save_index(known, None)
        return 0

    saved = 0
    latest: dict[str, str] | None = None
    for item in new_items[: args.new_limit]:
        cid = item["id"]
        url = f"{BASE}/contents/{cid}"
        try:
            html = fetch_url(url, cookie=cookie)
        except urllib.error.HTTPError as e:
            safe_print(f"WARN fetch {cid}: HTTP {e.code}")
            continue
        article = parse_article(html, cid)
        if not article["body"]:
            safe_print(f"WARN empty body: {cid} {article['title']}")
            continue
        if article["incomplete"]:
            safe_print(f"WARN paywall/incomplete: {cid} — cookie expired or not subscribed?")
            continue
        if args.dry_run:
            safe_print(f"DRY-RUN save: [{article['category']}] {article['title']}")
            known.add(cid)
            saved += 1
            latest = article
            continue
        path = save_article(article)
        known.add(cid)
        saved += 1
        latest = article
        safe_print(f"saved: {path.relative_to(ARCHIVE)}")
        time.sleep(0.6)

    save_index(known, latest)
    safe_print(f"column_collect done — saved {saved} new article(s)")
    return 0 if saved else 1


if __name__ == "__main__":
    sys.exit(main())
