#!/usr/bin/env python3
"""아카이브 폴더의 MD/CSV를 읽어 대시보드 JSON을 생성한다."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT.parent
OUTPUT = ROOT / "public" / "data" / "dashboard.json"

SIGNAL_DIR = ARCHIVE / "0_주식_에이전트" / "소수몽키_에이전트" / "03_신호_태그화" / "신호판"
CSV_PATH = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "01_텔레그램_원천파서"
    / "API_수집"
    / "인덱스"
    / "소수몽키_API_일자별_집계.csv"
)
COLUMN_DIR = ARCHIVE / "칼럼"
BRIEFING_DIR = ARCHIVE / "1_브리핑"


def parse_meta_block(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("> "):
            body = line[2:]
            if ":" in body:
                key, val = body.split(":", 1)
                meta[key.strip()] = val.strip()
    return meta


def parse_summary_table(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    for line in text.splitlines():
        if line.strip() == "## 판독 요약":
            in_table = True
            continue
        if in_table:
            if line.startswith("## "):
                break
            if not line.strip().startswith("|"):
                continue
            if "---" in line or "등급" in line and "신호" in line:
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 4:
                grade = parts[0].strip("`")
                rows.append(
                    {
                        "grade": grade,
                        "signal": parts[1],
                        "tags": parts[2],
                        "evidence": parts[3],
                    }
                )
    return rows


def parse_detail_sections(text: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_title = ""
    current: dict[str, str] = {}

    for line in text.splitlines():
        if line.startswith("### "):
            if current_title:
                sections.append({"title": current_title, **current})
            current_title = line[4:].strip()
            current = {}
            continue
        if line.startswith("## ") and "상세" not in line:
            if current_title:
                sections.append({"title": current_title, **current})
            break
        m = re.match(r"^- (.+?):\s*(.+)$", line.strip())
        if m and current_title:
            key = m.group(1).strip()
            current[key] = m.group(2).strip()

    if current_title:
        sections.append({"title": current_title, **current})
    return sections


def parse_rebalancing_table(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    for line in text.splitlines():
        if line.strip() == "## 리밸런싱 영향":
            in_table = True
            continue
        if in_table:
            if line.startswith("## "):
                break
            if not line.strip().startswith("|"):
                continue
            if "---" in line or "대상" in line:
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2:
                rows.append({"target": parts[0].strip("`"), "impact": parts[1]})
    return rows


def parse_grade_distribution(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    for line in text.splitlines():
        if line.strip() == "## 등급 분포":
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            if "---" in line or "등급" in line and "수" in line:
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3:
                rows.append(
                    {
                        "grade": parts[0].strip("`"),
                        "count": parts[1],
                        "memo": parts[2],
                    }
                )
    return rows


def parse_signal_board(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    date = date_match.group(1) if date_match else ""
    return {
        "date": date,
        "file": path.name,
        "meta": parse_meta_block(text),
        "summary": parse_summary_table(text),
        "details": parse_detail_sections(text),
        "rebalancing": parse_rebalancing_table(text),
        "gradeDistribution": parse_grade_distribution(text),
    }


def load_telegram_stats() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_columns() -> list[dict[str, str | int]]:
    categories: list[dict[str, str | int]] = []
    if not COLUMN_DIR.exists():
        return categories
    for folder in sorted(COLUMN_DIR.iterdir()):
        if not folder.is_dir():
            continue
        files = sorted(folder.glob("*.md"))
        categories.append(
            {
                "name": folder.name,
                "count": len(files),
                "samples": [f.stem for f in files[:5]],
            }
        )
    return categories


def load_briefing_file(*parts: str) -> str | None:
    path = BRIEFING_DIR.joinpath(*parts)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def parse_section(md: str, heading: str) -> str | None:
    marker = f"## {heading}"
    if marker not in md:
        return None
    start = md.index(marker) + len(marker)
    rest = md[start:].lstrip("\n")
    end = rest.find("\n## ")
    block = rest[:end] if end != -1 else rest
    return block.strip()


def build_today_from_current_pan(md: str | None) -> dict | None:
    if not md:
        return None
    headline = parse_section(md, "오늘 한 줄")
    action_block = parse_section(md, "권장 행동")
    if not headline:
        return None
    action = action_block.split("\n")[0].strip("* ") if action_block else "관망"
    action = action.replace("**", "").strip()
    bullets = [line.strip("- ").strip() for line in headline.split("\n") if line.strip()]
    if len(bullets) == 1:
        return {"headline": bullets[0], "bullets": bullets, "action": action}
    return {"headline": bullets[0], "bullets": bullets[1:] or bullets, "action": action}


def load_latest_sosumonkey_report() -> str | None:
    report_dir = BRIEFING_DIR / "소수몽키_브리핑" / "일일보고"
    if not report_dir.exists():
        return None
    files = sorted(report_dir.glob("*.md"))
    if not files:
        return None
    return files[-1].read_text(encoding="utf-8")


def build_today_summary(latest_signal: dict | None) -> dict:
    if not latest_signal:
        return {
            "headline": "아직 신호판 데이터가 없습니다.",
            "bullets": ["소수몽키 에이전트에서 신호판을 생성해 주세요."],
            "action": "관망",
        }

    s3 = [s for s in latest_signal["summary"] if s["grade"] == "SM-S3"]
    s2 = [s for s in latest_signal["summary"] if s["grade"] == "SM-S2"]
    bullets = []
    for s in s3[:2]:
        bullets.append(f"[S3] {s['signal'][:80]}{'…' if len(s['signal']) > 80 else ''}")
    for s in s2[:1]:
        bullets.append(f"[S2] {s['signal'][:80]}{'…' if len(s['signal']) > 80 else ''}")

    action = "조건부 실행 검토" if s3 else ("관찰" if s2 else "관망")
    headline = f"소수몽키 신호 {latest_signal['date']} — S3 {len(s3)}건, S2 {len(s2)}건"

    return {"headline": headline, "bullets": bullets, "action": action}


def main() -> None:
    archive_ok = SIGNAL_DIR.exists() or BRIEFING_DIR.exists()
    if not archive_ok and OUTPUT.exists():
        print(f"Archive not on this machine — keeping existing {OUTPUT}")
        print(f"  (signals in file: check locally)")
        return

    signal_files = sorted(SIGNAL_DIR.glob("신호판_*.md")) if SIGNAL_DIR.exists() else []
    signals = [parse_signal_board(p) for p in signal_files]
    latest = signals[-1] if signals else None

    portfolio_md = load_briefing_file("포트폴리오_브리핑", "00_현황", "실제_보유현황.md")
    asset_md = load_briefing_file("자산제곱_브리핑", "00_운용판단", "이번주_실행판.md")
    meeting_md = load_briefing_file("토론_브리핑", "00_오늘매매", "오늘_매매_회의.md")
    current_pan_path = BRIEFING_DIR / "현재판.md"
    current_pan_md = (
        current_pan_path.read_text(encoding="utf-8") if current_pan_path.exists() else None
    )
    sosumonkey_report = load_latest_sosumonkey_report()
    rebalance_md = load_briefing_file(
        "포트폴리오_브리핑", "01_목표구성", "목표_및_리밸런싱_현재판.md"
    )

    today = build_today_from_current_pan(current_pan_md) or build_today_summary(latest)

    portfolio_pending = 0
    if portfolio_md:
        portfolio_pending += portfolio_md.count("_(입력)_")
    if rebalance_md:
        portfolio_pending += rebalance_md.count("_(입력)_")

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "archivePath": str(ARCHIVE),
        "today": today,
        "currentPan": {
            "ready": current_pan_md is not None,
            "content": current_pan_md,
        },
        "sosumonkeyReport": {
            "ready": sosumonkey_report is not None,
            "content": sosumonkey_report,
        },
        "latestSignalDate": latest["date"] if latest else None,
        "pendingInputs": portfolio_pending,
        "signals": signals,
        "telegramStats": load_telegram_stats(),
        "columns": load_columns(),
        "portfolio": {
            "ready": portfolio_md is not None,
            "content": portfolio_md,
            "placeholder": "1_브리핑/포트폴리오_브리핑/00_현황/실제_보유현황.md 를 만들면 여기에 표시됩니다.",
        },
        "asset": {
            "ready": asset_md is not None,
            "content": asset_md,
            "placeholder": "1_브리핑/자산제곱_브리핑/00_운용판단/이번주_실행판.md 를 만들면 여기에 표시됩니다.",
        },
        "meeting": {
            "ready": meeting_md is not None,
            "content": meeting_md,
            "placeholder": "토론 중재 에이전트 브리핑이 생성되면 여기에 표시됩니다. Cursor에서 '오늘 매매할 것은?'을 실행하세요.",
        },
        "rebalance": {
            "ready": rebalance_md is not None,
            "content": rebalance_md,
        },
        "agents": [
            {
                "id": "sosumonkey",
                "name": "소수몽키",
                "emoji": "🐵",
                "role": "시장 신호·모멘텀",
                "status": "active" if sosumonkey_report or latest else "waiting",
            },
            {
                "id": "asset",
                "name": "자산제곱",
                "emoji": "🧠",
                "role": "원칙·매수 게이트",
                "status": "active" if asset_md else "waiting",
            },
            {
                "id": "portfolio",
                "name": "포트폴리오",
                "emoji": "💼",
                "role": "보유·노출 여력",
                "status": "active" if portfolio_md else "waiting",
            },
            {
                "id": "moderator",
                "name": "토론 중재",
                "emoji": "⚖️",
                "role": "최종 행동 정리",
                "status": "active" if meeting_md else "waiting",
            },
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"dashboard.json written -> {OUTPUT}")
    print(f"  signals: {len(signals)}, latest: {payload['latestSignalDate']}")


if __name__ == "__main__":
    main()
