#!/usr/bin/env python3
"""auto-stub 신호판을 텔레그램 원문 기반 규칙 태그화로 갱신한다."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent.parent.parent
JSONL_PATH = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "01_텔레그램_원천파서"
    / "API_수집"
    / "인덱스"
    / "소수몽키_API_원천인덱스.jsonl"
)
SIGNAL_DIR = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "03_신호_태그화"
    / "신호판"
)

STRONG = ("신고가", "주도", "강세", "상한가", "핵심", "확대", "돌파", "랠리", "초호황")
WEAK = ("유의", "조정", "경계", "노이즈", "관망", "보류", "리스크", "변동성")

THEMES: list[dict] = [
    {"id": "ai_semi", "label": "AI·반도체·메모리", "tags": "종목, 섹터, ETF",
     "keys": ("엔비디아", "NVDA", "반도체", "AI", "GTC", "DRAM", "메모리", "ARM", "AVGO", "MU", "키옥시아", "마이크론", "SMH")},
    {"id": "sw_cloud", "label": "SW·클라우드·AI에이전트", "tags": "종목, 섹터",
     "keys": ("마소", "MSFT", "PLTR", "ORCL", "NOW", "IGV", "SW", "소프트웨어", "에이전트", "클라우드")},
    {"id": "macro", "label": "매크로·금리·물가", "tags": "매크로, 정책",
     "keys": ("금리", "CPI", "인플레", "연준", "물가", "10년", "디스인플", "거시", "매크로")},
    {"id": "dc_infra", "label": "데이터센터·인프라", "tags": "종목, 섹터",
     "keys": ("데이터센터", "CRWV", "NBIS", "서버", "HPE", "DELL", "네오클라우드")},
    {"id": "space", "label": "우주·스페이스X", "tags": "종목, ETF, 이벤트",
     "keys": ("스페이스X", "우주", "NASA", "RKLB", "로켓")},
    {"id": "policy", "label": "정책·트럼프·IBM", "tags": "정책, 종목",
     "keys": ("트럼프", "IBM", "양자", "정책", "관세", "베센트")},
]


def load_messages_by_date() -> dict[str, list[dict]]:
    by_date: dict[str, list[dict]] = defaultdict(list)
    if not JSONL_PATH.exists():
        return by_date
    for line in JSONL_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        day = str(rec.get("date") or "")
        if day:
            by_date[day].append(rec)
    return by_date


def extract_tickers(text: str) -> list[str]:
    found = set(re.findall(r"\$([A-Z]{1,5})\b", text))
    for t in ("NVDA", "MSFT", "ARM", "MU", "AVGO", "PLTR", "CRWV", "NBIS", "IBM", "IGV"):
        if t in text.upper() or t.lower() in text:
            found.add(t)
    return sorted(found)[:8]


def score_theme(texts: list[str], theme: dict) -> tuple[int, int, list[str]]:
    strong = weak = 0
    msgs: list[str] = []
    blob = "\n".join(texts)
    hits = sum(blob.count(k) for k in theme["keys"])
    for t in texts:
        if any(k in t for k in theme["keys"]):
            msgs.append(t[:120].replace("\n", " "))
            for s in STRONG:
                if s in t:
                    strong += 1
            for w in WEAK:
                if w in t:
                    weak += 1
    return hits + strong * 2, strong - weak, msgs[:3]


def grade_for(score: int, net_strong: int) -> str:
    if score >= 8 and net_strong >= 2:
        return "SM-S3"
    if score >= 4 or net_strong >= 1:
        return "SM-S2"
    return "SM-S1"


def build_board(day: str, msgs: list[dict]) -> str:
    texts = [str(m.get("text") or "") for m in msgs if m.get("text")]
    msg_ids = [str(m.get("message_id") or "") for m in msgs if m.get("message_id")][:6]
    all_text = "\n".join(texts)
    tickers = extract_tickers(all_text)

    scored: list[tuple[int, int, dict, list[str]]] = []
    for theme in THEMES:
        sc, net, snippets = score_theme(texts, theme)
        if sc > 0:
            scored.append((sc, net, theme, snippets))
    scored.sort(key=lambda x: (-x[0], -x[1]))

    if not scored:
        scored = [(1, 0, {"label": "일일 브리핑", "tags": "매크로", "keys": ()}, texts[:2])]

    summary_rows: list[str] = []
    details: list[str] = []
    rebalance: list[str] = []
    used_snippets: set[str] = set()
    detail_idx = 0

    for _sc, net, theme, snippets in scored[:5]:
        grade = grade_for(_sc, net)
        snippet = snippets[0] if snippets else f"텔레그램 {len(msgs)}건"
        # 동일 문장이 여러 테마에 반복되지 않도록 처리
        sig_key = snippet[:40]
        if sig_key in used_snippets:
            continue
        used_snippets.add(sig_key)
        signal = f"{theme['label']} — {snippet[:80]}{'…' if len(snippet) > 80 else ''}"
        evidence = ", ".join(msg_ids[:4]) if msg_ids else "API 원천"
        summary_rows.append(
            f"| `{grade}` | {signal} | {theme['tags']} | {evidence} |"
        )
        theme_tickers = extract_tickers(" ".join(snippets))
        ticker_str = ", ".join(f"`{t}`" for t in (theme_tickers or tickers)[:6]) or "-"
        detail_idx += 1
        details.append(
            f"""### {detail_idx}. {theme['label']}

- 등급: `{grade}`
- 핵심 테마: {theme['label']}
- 언급 종목/ETF: {ticker_str}
- 소수몽키 관점: {snippet}
- 포트폴리오 해석: {'강한 신호 — 기존 리밸런싱 방향 확인' if grade == 'SM-S3' else '감시 신호 — 추격 매수보다 조건 확인'}
"""
        )
        for t in (theme_tickers or tickers)[:4]:
            rebalance.append(f"| `{t}` | {grade} 신호 — {'1차 검토' if grade == 'SM-S3' else '관찰'} |")

    if not rebalance and tickers:
        for t in tickers[:5]:
            rebalance.append(f"| `{t}` | 언급 확인 — 관찰 |")

    summary_table = "\n".join(summary_rows)
    detail_block = "\n".join(details)
    rebalance_table = "\n".join(rebalance) if rebalance else "| *(해당 없음)* | 관찰 유지 |"

    return f"""# 소수몽키 신호판 {day}

> 기준 원천: Telegram API `소수의견(26년 2분기)` (auto-tagged)
> 사용 산출물: API 원천 인덱스, 규칙 태그화
> 판독 범위: {day}

## 판독 요약

| 등급 | 신호 | 태그 | 근거 |
|------|------|------|------|
{summary_table}

## 상세 신호

{detail_block}

## 리밸런싱 영향

| 대상 | 영향 |
|------|------|
{rebalance_table}
"""


def main() -> int:
    by_date = load_messages_by_date()
    tagged = 0
    for path in sorted(SIGNAL_DIR.glob("신호판_*.md")):
        text = path.read_text(encoding="utf-8")
        # 수동 작성 신호판은 건드리지 않음
        if "auto-stub" not in text and "auto-tagged" not in text:
            continue
        m = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
        if not m:
            continue
        day = m.group(1)
        msgs = by_date.get(day, [])
        if not msgs:
            continue
        path.write_text(build_board(day, msgs), encoding="utf-8")
        tagged += 1
        print(f"auto-tagged: {path.name} ({len(msgs)} msgs)")

    print(f"auto_tag_stubs done ({tagged} files)")
    return tagged


if __name__ == "__main__":
    main()
