#!/usr/bin/env python3
"""자산제곱·소수몽키·포트폴리오 입력을 합쳐 오늘 매매 회의 MD를 자동 생성한다."""

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

ASSET_PATH = BRIEFING / "자산제곱_브리핑" / "00_운용판단" / "이번주_실행판.md"
PORTFOLIO_PATH = BRIEFING / "포트폴리오_브리핑" / "00_현황" / "실제_보유현황.md"
MEETING_PATH = BRIEFING / "토론_브리핑" / "00_오늘매매" / "오늘_매매_회의.md"
CURRENT_PAN_PATH = BRIEFING / "현재판.md"

TICKER_THEMES: dict[str, str] = {
    "NVDA": "AI·반도체·메모리",
    "AVGO": "AI·반도체·메모리",
    "MU": "AI·반도체·메모리",
    "ARM": "AI·반도체·메모리",
    "DRAM": "AI·반도체·메모리",
    "MSFT": "SW·클라우드·AI에이전트",
    "PLTR": "SW·클라우드·AI에이전트",
    "CRWV": "데이터센터·인프라",
    "NBIS": "데이터센터·인프라",
    "SLV": "매크로·금리·물가",
    "GDX": "매크로·금리·물가",
    "IBM": "정책·트럼프·IBM",
    "000660": "AI·반도체·메모리",
    "005930": "AI·반도체·메모리",
    "034020": "데이터센터·인프라",
    "234340": "매크로·금리·물가",
    "SATL": "우주·스페이스X",
    "RDW": "우주·스페이스X",
    "IONQ": "AI·반도체·메모리",
    "IREN": "데이터센터·인프라",
    "QCOM": "AI·반도체·메모리",
    "CRCA": "SW·클라우드·AI에이전트",
    "CRDU": "AI·반도체·메모리",
    "MRVL": "AI·반도체·메모리",
    "LITE": "AI·반도체·메모리",
    "RAM": "AI·반도체·메모리",
}

LEVERAGED = {"CRCA", "CRDU", "RAM"}
HIGH_RISK = {"IONQ", "SATL", "RDW", "IREN"}


def latest_signal_file() -> tuple[Path | None, str | None]:
    files = sorted(SIGNAL_DIR.glob("신호판_*.md")) if SIGNAL_DIR.exists() else []
    if not files:
        return None, None
    path = files[-1]
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    return path, (m.group(1) if m else None)


def load_recent_signals(max_days: int = 3) -> tuple[str, dict[str, str]]:
    files = sorted(SIGNAL_DIR.glob("신호판_*.md")) if SIGNAL_DIR.exists() else []
    if not files:
        return date.today().isoformat(), {}
    recent = files[-max_days:]
    rank = {"SM-S3": 3, "SM-S2": 2, "SM-S1": 1, "SM-S0": 0}
    merged: dict[str, str] = {}
    for path in recent:
        for theme, grade in parse_signal_grades(path.read_text(encoding="utf-8")).items():
            if rank.get(grade, 0) >= rank.get(merged.get(theme, ""), -1):
                merged[theme] = grade
    latest = recent[-1]
    m = re.search(r"(\d{4}-\d{2}-\d{2})", latest.stem)
    return (m.group(1) if m else date.today().isoformat()), merged


def parse_signal_grades(text: str) -> dict[str, str]:
    """테마 라벨 → 최고 등급 (SM-S3 > SM-S2)."""
    rank = {"SM-S3": 3, "SM-S2": 2, "SM-S1": 1, "SM-S0": 0}
    grades: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*`(SM-S[0-3])`\s*\|\s*([^|]+)\s*\|", line)
        if not m:
            continue
        grade, label = m.group(1), m.group(2).strip()
        theme = label.split("—")[0].strip() if "—" in label else label[:40]
        if rank.get(grade, 0) >= rank.get(grades.get(theme, ""), -1):
            grades[theme] = grade
    return grades


def parse_md_table(section_text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.match(r"\|\s*[-:]+", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and not all(c.replace("-", "") == "" for c in cells):
            rows.append(cells)
    return rows


def section(text: str, heading: str) -> str:
    m = re.search(rf"## {re.escape(heading)}[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1) if m else ""


def parse_asset_candidates(text: str) -> tuple[list[dict], list[dict], list[str], list[str], list[str]]:
    buy: list[dict] = []
    wait: list[dict] = []
    hold: list[str] = []
    reduce: list[str] = []

    for row in parse_md_table(section(text, "이번 주 매수 후보")):
        if len(row) >= 2 and row[0] not in ("티커", ""):
            buy.append({"ticker": row[0], "gate": row[1], "note": row[2] if len(row) > 2 else ""})

    for row in parse_md_table(section(text, "조건부 대기")):
        if len(row) >= 2 and row[0] not in ("티커", ""):
            wait.append({"ticker": row[0], "reason": row[1], "condition": row[2] if len(row) > 2 else ""})

    hold_sec = section(text, "홀딩·관망")
    for line in hold_sec.splitlines():
        m = re.match(r"-\s*([A-Z/]+)", line.strip())
        if m:
            hold.append(m.group(1))

    reduce_sec = section(text, "매도·감축·정리 검토")
    for row in parse_md_table(reduce_sec):
        if row and row[0] not in ("티커", ""):
            reduce.append(row[0])
    if not reduce:
        for line in reduce_sec.splitlines():
            if "SLV" in line or "GDX" in line:
                reduce.append("SLV / GDX")

    dont = section(text, "이번 주 하지 말 것")
    dont_lines = [ln.strip("- ").strip() for ln in dont.splitlines() if ln.strip().startswith("-")]

    return buy, wait, hold, reduce, dont_lines


def parse_portfolio(text: str) -> tuple[set[str], int, list[str], list[dict]]:
    held: set[str] = set()
    notes: list[str] = []
    holdings: list[dict] = []
    pending = text.count("_(입력)_")
    for sec_name in ("보유 종목 — 국장", "보유 종목 — 미장", "보유 종목"):
        for row in parse_md_table(section(text, sec_name)):
            if not row or row[0] in ("티커", "_(추가)_", ""):
                continue
            ticker = row[0].upper()
            if ticker and not ticker.startswith("_"):
                held.add(ticker)
                name = row[1] if len(row) > 1 else ""
                note = row[6] if len(row) > 6 else (row[5] if len(row) > 5 else "")
                if note:
                    notes.append(f"{ticker}: {note}")
                holdings.append({"ticker": ticker, "name": name, "note": note})
    cash_sec = section(text, "현금·여력")
    if "부족" in cash_sec or "현금 0" in cash_sec:
        notes.append("현금 여력 부족")
    elif "_(있음/부족)_" in cash_sec:
        notes.append("현금 여력 미입력")
    return held, pending, notes, holdings


def signal_for_ticker(ticker: str, grades: dict[str, str]) -> str:
    key = ticker.split("/")[0].strip()
    for part in re.split(r"[/\s]+", ticker):
        theme = TICKER_THEMES.get(part.upper())
        if theme and theme in grades:
            return grades[theme]
    theme = TICKER_THEMES.get(key.upper())
    if theme and theme in grades:
        return grades[theme]
    return "—"


def portfolio_col(ticker: str, held: set[str], notes: list[str]) -> str:
    parts = re.split(r"[/\s]+", ticker)
    held_any = any(p.upper() in held for p in parts if p)
    note_blob = " ".join(notes)
    if "현금 여력 부족" in note_blob and not held_any:
        return "현금 0 · 신규 불가"
    if held_any:
        return "이미 보유"
    return "미보유"


def mediate_holding(ticker: str, note: str) -> str:
    t = ticker.upper()
    if t in LEVERAGED or "레버리지" in note or "2배" in note:
        return "감축 검토 · 추가 금지"
    if t in HIGH_RISK or "고위험" in note or "투기" in note:
        return "홀딩 · 물타기 금지"
    if t in ("000660", "005930", "QCOM", "MRVL", "LITE"):
        return "코어 홀딩 · 추격 금지"
    if t == "034020":
        return "전력·원전 홀딩"
    return "홀딩 유지"


def mediate(
    ticker: str,
    gate: str,
    signal: str,
    pf: str,
    *,
    conditional: bool = False,
) -> str:
    if "추가 금지" in pf or "물타기 금지" in pf or "신규 불가" in pf:
        if "미보유" in pf or "신규" in pf:
            return "현금 확보 전 보류"
        return "홀딩, 추가 금지"
    if "정리" in gate or ticker.startswith("SLV"):
        return "정리 후보 유지"
    if conditional:
        if signal == "SM-S3":
            return "2차 대기 (과열·눌림 확인)"
        return "조건부 대기"
    if "이미 보유" in pf:
        return "홀딩"
    if gate.startswith("G2"):
        if signal == "SM-S3":
            return "눌림 시 1차"
        if signal == "SM-S2":
            return "눌림 시 분할 검토"
        return "조건부 대기"
    return "관망"


def build_meeting(
    today: str,
    signal_date: str,
    asset_date: str,
    portfolio_date: str,
    signal_grades: dict[str, str],
    buy: list[dict],
    wait: list[dict],
    hold: list[str],
    reduce: list[str],
    dont: list[str],
    held: set[str],
    pending: int,
    pf_notes: list[str],
    holdings: list[dict] | None = None,
) -> str:
    holdings = holdings or []
    rows: list[tuple[str, str, str, str, str]] = []
    for item in buy:
        t, g = item["ticker"], item["gate"]
        sig = signal_for_ticker(t, signal_grades)
        pf = portfolio_col(t, held, pf_notes)
        rows.append((t, f"{g} {item.get('note', '')[:12]}".strip(), sig, pf, mediate(t, g, sig, pf)))

    for item in wait:
        t = item["ticker"]
        sig = signal_for_ticker(t, signal_grades)
        pf = portfolio_col(t, held, pf_notes)
        rows.append((t, "조건부", sig, pf, mediate(t, "조건부", sig, pf, conditional=True)))

    do_today: list[str] = []
    dont_today = dont[:6] if dont else []
    if "현금 여력 부족" in " ".join(pf_notes):
        do_today.append("**홀딩 우선** — 현금 0원, 신규 매수 없음")
        do_today.append("코어(하이닉스·삼성·퀄컴·마벨·루멘텀): 방향 유지, 추격 금지")
    elif not any("눌림" in r[4] for r in rows):
        do_today.append("_(없음 — 조건부 대기 우세)_")

    protect: list[str] = []
    for h in holdings:
        label = f"{h['name']} ({h['ticker']})" if h.get("name") else h["ticker"]
        protect.append(f"{label}: {mediate_holding(h['ticker'], h.get('note', ''))}")
    for h in hold:
        line = h.replace(":", " —")
        if line not in " ".join(protect):
            protect.append(line)

    reduce_lines = []
    for r in reduce:
        if "/" in r:
            reduce_lines.append(f"{r}: 감축·교체 검토")
        else:
            reduce_lines.append(f"{r}: 정리 후보")
    if not reduce_lines:
        reduce_lines = ["_(없음)_"]

    agreements: list[str] = []
    conflicts: list[str] = []
    s3_themes = [t for t, g in signal_grades.items() if g == "SM-S3"]
    if s3_themes:
        agreements.append(
            f"소수몽키 강신호({', '.join(s3_themes[:3])}) — AI 인프라 충원 방향과 정합"
        )
    agreements.append("타이밍은 전원 **눌림/재지지** 우선 (자산제곱 원칙)")
    if holdings:
        agreements.append(
            f"보유 14종목(각 1,000만원·총 1.4억) — AI·메모리 테마 **정합**, 레버리지 3종 리스크 주의"
        )
    if any("ARM" in r[0] for r in rows):
        conflicts.append("ARM: 미보유 — 여력 확보 후에만 1차 검토")
    if any(t in LEVERAGED for t in held):
        conflicts.append("CRCA/CRDU/RAM: 레버리지 ETF 보유 — 신규 충원보다 감축 우선 검토")

    user_checks = []
    if "현금 여력 부족" in " ".join(pf_notes):
        user_checks.append("현금 0원 — NVDA/MSFT 매수 전 CRCA·CRDU·RAM 등 감축으로 여력 확보할지 결정")
    user_checks.append("레버리지 ETF 3종 비중 축소 여부")
    user_checks.append("고위험 4종(IONQ/SATL/RDW/IREN) 손절·익절 기준 확인")
    if pending > 0:
        user_checks.insert(0, f"보유현황 미입력 {pending}곳 — 실제 계좌 숫자 반영 후 회의 신뢰도 상승")

    table_lines = [
        "| 후보 | 자산제곱 | 소수몽키 | 포트폴리오 | 중재 결론 |",
        "|------|----------|----------|------------|-----------|",
    ]
    for t, a, s, p, c in rows:
        table_lines.append(f"| {t} | {a} | {s} | {p} | {c} |")

    lines = [
        "# 오늘 매매 회의",
        "",
        f"> 기준시각: {today}",
        f"> 입력 최신성: 신호판 {signal_date} ✅ / 실행판 {asset_date} ✅ / 보유현황 {portfolio_date} {'⚠️ 미입력' if pending else '✅'}",
        f"> 기준일: {today}",
        f"> 생성: 자동 (generate_meeting.py) — 규칙 기반 중재",
        "",
        "## 오늘 바로 할 것",
        "",
    ]
    for x in do_today or ["_(없음)_"]:
        lines.append(f"- {x}")
    lines += ["", "## 오늘 하지 말 것", ""]
    for x in dont_today or ["급등 추격 매수", "포트폴리오 여력 없이 신규 진입"]:
        lines.append(f"- {x}")
    lines += ["", "## 조건부 대기", ""] + table_lines
    lines += ["", "## 보유·수익 보호", ""]
    for x in protect or ["_(해당 없음)_"]:
        lines.append(f"- {x}")
    lines += ["", "## 정리·감축 검토", ""]
    for x in reduce_lines:
        lines.append(f"- {x}")
    lines += ["", "## 핵심 합의", ""]
    for x in agreements:
        lines.append(f"- {x}")
    lines += ["", "## 핵심 불합의", ""]
    for x in conflicts or ["_(없음)_"]:
        lines.append(f"- {x}")
    lines += ["", "## 사용자 확인 필요", ""]
    for i, x in enumerate(user_checks, 1):
        lines.append(f"{i}. {x}")
    lines.append("")
    return "\n".join(lines)


def patch_current_pan(signal_date: str | None) -> None:
    if not CURRENT_PAN_PATH.exists() or not signal_date:
        return
    text = CURRENT_PAN_PATH.read_text(encoding="utf-8")
    text = re.sub(r"> 갱신: \d{4}-\d{2}-\d{2}", f"> 갱신: {signal_date}", text, count=1)
    text = re.sub(
        r"\| 소수몽키 \| ✅ \| 신호판 \d{4}-\d{2}-\d{2} \|",
        f"| 소수몽키 | ✅ | 신호판 {signal_date} |",
        text,
    )
    text = re.sub(
        r"신호판_\d{4}-\d{2}-\d{2}\.md",
        f"신호판_{signal_date}.md",
        text,
    )
    CURRENT_PAN_PATH.write_text(text, encoding="utf-8")


def extract_date(path: Path) -> str:
    if not path.exists():
        return "—"
    m = re.search(r"> 기준일: (\d{4}-\d{2}-\d{2})", path.read_text(encoding="utf-8"))
    return m.group(1) if m else date.today().isoformat()


def main() -> int:
    today = date.today().isoformat()
    if not ASSET_PATH.exists():
        print("generate_meeting skip: 이번주_실행판.md 없음")
        return 1

    asset_text = ASSET_PATH.read_text(encoding="utf-8")
    portfolio_text = PORTFOLIO_PATH.read_text(encoding="utf-8") if PORTFOLIO_PATH.exists() else ""

    signal_date, signal_grades = load_recent_signals()
    buy, wait, hold, reduce, dont = parse_asset_candidates(asset_text)
    held, pending, pf_notes, holdings = parse_portfolio(portfolio_text)

    asset_date = extract_date(ASSET_PATH)
    portfolio_date = extract_date(PORTFOLIO_PATH) if PORTFOLIO_PATH.exists() else today

    # 실행판 출처 날짜 동기화
    asset_text = re.sub(
        r"> 출처:.*",
        f"> 출처: 자산제곱 에이전트 + 소수몽키 신호판 {signal_date}",
        asset_text,
        count=1,
    )
    ASSET_PATH.write_text(asset_text, encoding="utf-8")

    content = build_meeting(
        today=today,
        signal_date=signal_date,
        asset_date=asset_date,
        portfolio_date=portfolio_date,
        signal_grades=signal_grades,
        buy=buy,
        wait=wait,
        hold=hold,
        reduce=reduce,
        dont=dont,
        held=held,
        pending=pending,
        pf_notes=pf_notes,
        holdings=holdings,
    )

    MEETING_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEETING_PATH.write_text(content, encoding="utf-8")
    patch_current_pan(signal_date)
    print(f"generate_meeting done -> {MEETING_PATH.name} (signal {signal_date})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
