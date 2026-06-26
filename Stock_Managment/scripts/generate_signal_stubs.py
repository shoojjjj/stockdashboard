#!/usr/bin/env python3
"""텔레그램 집계에 있으나 신호판이 없는 날짜에 스텁 신호판을 생성한다."""

from __future__ import annotations

import csv
import re
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent.parent.parent
CSV_PATH = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "01_텔레그램_원천파서"
    / "API_수집"
    / "인덱스"
    / "소수몽키_API_일자별_집계.csv"
)
SIGNAL_DIR = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "03_신호_태그화"
    / "신호판"
)


def existing_dates() -> set[str]:
    if not SIGNAL_DIR.exists():
        return set()
    dates: set[str] = set()
    for path in SIGNAL_DIR.glob("신호판_*.md"):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
        if m:
            dates.add(m.group(1))
    return dates


def load_telegram_dates() -> list[tuple[str, int]]:
    if not CSV_PATH.exists():
        return []
    rows: list[tuple[str, int]] = []
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            day = row.get("date", "").strip()
            if not day:
                continue
            try:
                count = int(row.get("messages") or 0)
            except ValueError:
                count = 0
            rows.append((day, count))
    return rows


def stub_md(day: str, msg_count: int) -> str:
    return f"""# 소수몽키 신호판 {day}

> 기준 원천: Telegram API `소수의견(26년 2분기)` (auto-stub)
> 사용 산출물: API 원천 인덱스
> 판독 범위: {day}

## 판독 요약

| 등급 | 신호 | 태그 | 근거 |
|------|------|------|------|
| `SM-S1` | 텔레그램 {msg_count}건 수집 — 신호 태그화(Cursor) 검토 필요 | 자동생성 | API 일자별 집계 |

## 상세 신호

### 1. 자동 생성 스텁

- 등급: `SM-S1`
- 핵심 테마: 신호판 미작성 — Cursor에서 소수몽키 태그화 실행 필요
- 소수몽키 관점: 이전 신호판 기준 유지. 태그화 후 갱신.
- 포트폴리오 해석: 급변 없음 — 최신 수동 신호판 또는 이전일 기준 유지.

## 리밸런싱 영향

| 대상 | 영향 |
|------|------|
| 전체 | 태그화 완료 전까지 이전 신호판 기준 유지 |
"""


def main() -> int:
    have = existing_dates()
    created = 0
    SIGNAL_DIR.mkdir(parents=True, exist_ok=True)

    for day, count in load_telegram_dates():
        if day in have:
            continue
        target = SIGNAL_DIR / f"신호판_{day}.md"
        target.write_text(stub_md(day, count), encoding="utf-8")
        have.add(day)
        created += 1
        print(f"stub created: {target.name} ({count} msgs)")

    print(f"generate_signal_stubs done ({created} new)")
    return created


if __name__ == "__main__":
    main()
