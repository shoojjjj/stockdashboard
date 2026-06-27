#!/usr/bin/env python3
"""일별 대시보드 스냅샷을 누적 저장한다."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT.parent
DAILY_DIR = ROOT / "public" / "data" / "daily"
ARCHIVE_DAILY = ARCHIVE / "1_브리핑" / "일일_스냅샷"
INDEX_PATH = DAILY_DIR / "index.json"


def grade_counts(signal: dict | None) -> dict[str, int]:
    if not signal:
        return {}
    counts: dict[str, int] = {}
    for row in signal.get("summary", []):
        g = row.get("grade", "")
        counts[g] = counts.get(g, 0) + 1
    return counts


def snapshot_from_payload(payload: dict) -> dict:
    latest_date = payload.get("latestSignalDate")
    signals = payload.get("signals", [])
    latest = next((s for s in signals if s.get("date") == latest_date), signals[-1] if signals else None)

    tg_stats = payload.get("telegramStats", [])
    tg_row = next((r for r in reversed(tg_stats) if r.get("date") == latest_date), tg_stats[-1] if tg_stats else {})

    return {
        "date": latest_date,
        "savedAt": datetime.now(timezone.utc).isoformat(),
        "headline": payload.get("today", {}).get("headline", ""),
        "action": payload.get("today", {}).get("action", ""),
        "bullets": payload.get("today", {}).get("bullets", []),
        "latestSignalDate": latest_date,
        "signalSource": (latest or {}).get("meta", {}).get("기준 원천", ""),
        "isAutoTagged": "auto-tagged" in str((latest or {}).get("meta", {})),
        "gradeCounts": grade_counts(latest),
        "signalSummary": (latest or {}).get("summary", []),
        "telegramMessages": tg_row.get("messages", ""),
        "pendingInputs": payload.get("pendingInputs", 0),
    }


def write_md(snap: dict, path: Path) -> None:
    lines = [
        f"# 일일 스냅샷 {snap.get('date', '—')}",
        "",
        f"> 저장: {snap.get('savedAt', '')}",
        "",
        "## 한 줄 요약",
        snap.get("headline", "—"),
        "",
        f"**권장:** {snap.get('action', '—')}",
        "",
        "## 신호 등급",
    ]
    for g, n in sorted(snap.get("gradeCounts", {}).items()):
        lines.append(f"- {g}: {n}건")
    lines.extend(["", "## 핵심 bullet"])
    for b in snap.get("bullets", []):
        lines.append(f"- {b}")
    lines.extend(["", "## 텔레그램", f"- 메시지: {snap.get('telegramMessages', '—')}건"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def archive_signal_day(payload: dict, signal: dict) -> str | None:
    day = signal.get("date")
    if not day:
        return None
    snap = {
        "date": day,
        "savedAt": datetime.now(timezone.utc).isoformat(),
        "headline": signal["summary"][0]["signal"] if signal.get("summary") else "",
        "action": payload.get("today", {}).get("action", ""),
        "bullets": [r.get("signal", "") for r in signal.get("summary", [])[:5]],
        "latestSignalDate": day,
        "signalSource": signal.get("meta", {}).get("기준 원천", ""),
        "isAutoTagged": "auto-tagged" in str(signal.get("meta", {})),
        "gradeCounts": grade_counts(signal),
        "signalSummary": signal.get("summary", []),
        "telegramMessages": _tg_count(payload, day),
        "pendingInputs": payload.get("pendingInputs", 0),
    }
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DAILY.mkdir(parents=True, exist_ok=True)
    (DAILY_DIR / f"{day}.json").write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(snap, ARCHIVE_DAILY / f"{day}.md")
    return day


def _tg_count(payload: dict, day: str) -> str:
    for row in reversed(payload.get("telegramStats", [])):
        if row.get("date") == day:
            return str(row.get("messages", ""))
    return ""


def backfill(payload: dict) -> int:
    count = 0
    for signal in payload.get("signals", []):
        day = signal.get("date")
        if not day:
            continue
        path = DAILY_DIR / f"{day}.json"
        if not path.exists():
            archive_signal_day(payload, signal)
            count += 1
    # 최신일은 항상 갱신
    latest = payload.get("latestSignalDate")
    if latest:
        sig = next((s for s in payload.get("signals", []) if s.get("date") == latest), None)
        if sig:
            archive_signal_day(payload, sig)
    _rebuild_index()
    return count


def _rebuild_index() -> None:
    index: list[dict] = []
    for f in sorted(DAILY_DIR.glob("*.json")):
        if f.name == "index.json":
            continue
        snap = json.loads(f.read_text(encoding="utf-8"))
        index.append({
            "date": snap.get("date"),
            "headline": (snap.get("headline") or "")[:80],
            "gradeCounts": snap.get("gradeCounts", {}),
            "telegramMessages": snap.get("telegramMessages", ""),
            "savedAt": snap.get("savedAt"),
        })
    index.sort(key=lambda x: x.get("date", ""))
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def archive(payload: dict) -> str | None:
    backfill(payload)
    return payload.get("latestSignalDate")


def load_index() -> list[dict]:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return []


if __name__ == "__main__":
    import sys
    dash = ROOT / "public" / "data" / "dashboard.json"
    if dash.exists():
        p = json.loads(dash.read_text(encoding="utf-8"))
        d = archive(p)
        print(f"archived: {d}")
