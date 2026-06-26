#!/usr/bin/env python3
"""시스템 헬스체크 — 레포트/자동화용."""

from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent.parent.parent
STOCK = ARCHIVE / "Stock_Managment"
DASHBOARD_JSON = STOCK / "public" / "data" / "dashboard.json"
DEPLOY_URL = "https://stock-managment-black.vercel.app"
TELEGRAM_ENV = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "01_텔레그램_원천파서"
    / ".env"
)
TELEGRAM_CSV = (
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


def check_scheduler(name: str) -> str:
    try:
        out = subprocess.run(
            ["schtasks", "/Query", "/TN", name, "/FO", "LIST"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0 and ("Ready" in out.stdout or "준비" in out.stdout):
            return "ok"
    except Exception:
        pass
    return "missing"


def check_url(url: str) -> str:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status in (200, 307, 308):
                return f"ok ({res.status})"
    except urllib.error.HTTPError as e:
        if e.code in (307, 308, 401):
            return f"ok ({e.code})"
        return f"error ({e.code})"
    except Exception as e:
        return f"error ({e})"
    return "unknown"


def main() -> None:
    checks: dict[str, str] = {}

    if DASHBOARD_JSON.exists():
        data = json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
        signals = len(data.get("signals", []))
        pending = data.get("pendingInputs", 0)
        checks["dashboard_json"] = f"ok - signals {signals}, pending {pending}"
    else:
        checks["dashboard_json"] = "missing"

    checks["vercel_site"] = check_url(DEPLOY_URL)
    checks["telegram_env"] = "ok" if TELEGRAM_ENV.exists() else "missing"

    if TELEGRAM_CSV.exists():
        import csv
        rows = list(csv.DictReader(TELEGRAM_CSV.open(encoding="utf-8-sig")))
        latest_tg = rows[-1]["date"] if rows else "-"
        checks["telegram_latest"] = f"ok - {latest_tg} ({len(rows)} days)"
    else:
        checks["telegram_latest"] = "missing csv"

    boards = list(SIGNAL_DIR.glob("신호판_*.md")) if SIGNAL_DIR.exists() else []
    stubs = sum(1 for p in boards if "auto-stub" in p.read_text(encoding="utf-8", errors="replace"))
    tagged = sum(1 for p in boards if "auto-tagged" in p.read_text(encoding="utf-8", errors="replace"))
    checks["signal_boards"] = f"ok - {len(boards)} files, {tagged} tagged, {stubs} stubs"
    checks["scheduler_deploy"] = check_scheduler("StockManagment_DailyDeploy")
    checks["scheduler_refresh"] = check_scheduler("StockManagment_DailyRefresh")

    try:
        out = subprocess.run(
            ["git", "-C", str(ARCHIVE), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        checks["github_remote"] = "ok" if out.returncode == 0 else "missing"
    except Exception:
        checks["github_remote"] = "error"

    all_ok = all(
        v.startswith("ok") for k, v in checks.items() if k != "telegram_env"
    ) or checks.get("dashboard_json", "").startswith("ok")

    result = {"healthy": all_ok, "checks": checks}
    out_path = STOCK / "public" / "data" / "health.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
