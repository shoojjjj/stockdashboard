#!/usr/bin/env python3
"""wonik-macro /api/context → JSON (섹터·퀀트·보유종목 시세)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / "macro_context.env"
DEFAULT_MACRO_URL = "https://wonik-macro.vercel.app/api/context"


def _load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def fetch_macro_context(tickers: list[str], *, timeout: int = 90) -> dict | None:
    _load_env()
    base = os.environ.get("MACRO_CONTEXT_URL", DEFAULT_MACRO_URL).rstrip("/")
    if not base.endswith("/context"):
        if "/api/" not in base:
            base = base + "/api/context"

    params: dict[str, str] = {"tickers": ",".join(tickers[:20])}
    api_key = os.environ.get("MACRO_API_KEY", "")
    if api_key:
        params["key"] = api_key
    url = f"{base}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"User-Agent": "stock-dashboard/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"WARN macro context HTTP {e.code}: {body}")
        return None
    except Exception as e:
        print(f"WARN macro context: {e}")
        return None


def format_macro_section(ctx: dict | None) -> str:
    if not ctx:
        return ""

    as_of = (ctx.get("asOf") or "")[:10]
    title = f"## 시장·섹터 컨텍스트 (macro · {as_of})" if as_of else "## 시장·섹터 컨텍스트 (macro 연동)"
    lines = [title, ""]

    macro = ctx.get("macro") or {}
    qqq = macro.get("qqq") or {}
    sox = macro.get("sox") or {}
    if qqq.get("todayPct") is not None:
        lines.append(f"- **QQQ** 오늘 {_pct(qqq.get('todayPct'))} · 1M {_pct(qqq.get('month1Pct'))}")
    if sox.get("todayPct") is not None:
        lines.append(f"- **SOX** 오늘 {_pct(sox.get('todayPct'))} · 1M {_pct(sox.get('month1Pct'))}")

    lines.append("")
    lines.append("| 섹터 | US 오늘 | KR 오늘 | 괴리 |")
    lines.append("|------|---------|---------|------|")
    for sec in (ctx.get("sectors") or [])[:8]:
        lines.append(
            f"| {sec.get('label', '—')} | {_pct(sec.get('usTodayPct'))} | "
            f"{_pct(sec.get('krTodayPct'))} | {_pct(sec.get('spreadPct'), suffix='p')} |"
        )

    holdings = ctx.get("holdings") or []
    if holdings:
        lines.extend(["", "### 보유 종목 × 퀀트", ""])
        lines.append("| 티커 | 섹터 | 오늘 | 1M | 퀀트 | 등급 |")
        lines.append("|------|------|------|-----|------|------|")
        for h in holdings:
            q = h.get("quantScore")
            q_str = str(int(q)) if q is not None else "—"
            lines.append(
                f"| {h.get('ticker', '—')} | {h.get('sector') or '—'} | "
                f"{_pct(h.get('todayPct'))} | {_pct(h.get('month1Pct'))} | "
                f"{q_str} | {h.get('quantGrade') or '—'} |"
            )

    for sl in ctx.get("summaryLines") or []:
        lines.append(f"- {sl}")

    lines.append("")
    return "\n".join(lines)


def _pct(v, suffix: str = "") -> str:
    if v is None:
        return "—"
    try:
        n = float(v)
    except (TypeError, ValueError):
        return "—"
    sign = "+" if n >= 0 else ""
    return f"{sign}{n:.1f}%{suffix}"


if __name__ == "__main__":
    import sys

    tickers = sys.argv[1:] or ["QCOM", "000660", "MRVL"]
    data = fetch_macro_context(tickers)
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("\n--- MD ---\n")
        print(format_macro_section(data))
