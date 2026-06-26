#!/usr/bin/env python3
"""신호판/날짜 기준으로 1_브리핑 헤더 날짜를 동기화한다."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent.parent.parent
BRIEFING = ARCHIVE / "1_브리핑"
SIGNAL_DIR = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "03_신호_태그화"
    / "신호판"
)


def latest_signal_date() -> str | None:
    files = sorted(SIGNAL_DIR.glob("신호판_*.md")) if SIGNAL_DIR.exists() else []
    if not files:
        return None
    m = re.search(r"(\d{4}-\d{2}-\d{2})", files[-1].stem)
    return m.group(1) if m else None


def patch_date(path: Path, label: str = "기준일") -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    today = date.today().isoformat()
    new_line = f"> {label}: {today}"
    if re.search(rf"> {label}:", text):
        updated = re.sub(rf"> {label}:.*", new_line, text, count=1)
    else:
        updated = text.replace("\n\n## ", f"\n{new_line}\n\n## ", 1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def sync_current_pan(signal_date: str | None) -> bool:
    path = BRIEFING / "현재판.md"
    if not path.exists() or not signal_date:
        return False
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r"> 갱신: \d{4}-\d{2}-\d{2}", f"> 갱신: {signal_date}", text, count=1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    signal_date = latest_signal_date()
    changed = 0
    targets = [
        BRIEFING / "포트폴리오_브리핑" / "00_현황" / "실제_보유현황.md",
        BRIEFING / "자산제곱_브리핑" / "00_운용판단" / "이번주_실행판.md",
        BRIEFING / "토론_브리핑" / "00_오늘매매" / "오늘_매매_회의.md",
    ]
    for t in targets:
        if patch_date(t):
            changed += 1
            print(f"updated date: {t.name}")
    if sync_current_pan(signal_date):
        changed += 1
        print("updated: 현재판.md")
    print(f"sync_briefing done ({changed} files)")


if __name__ == "__main__":
    main()
