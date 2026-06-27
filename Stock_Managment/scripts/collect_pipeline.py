#!/usr/bin/env python3
"""텔레그램 수집 → 신호판 → 대시보드 빌드 (PC 로컬 원클릭)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT.parent
TELEGRAM_DIR = (
    ARCHIVE
    / "0_주식_에이전트"
    / "소수몽키_에이전트"
    / "01_텔레그램_원천파서"
)
TELEGRAM = TELEGRAM_DIR / "telegram_api_collect.py"
TELEGRAM_ENV = TELEGRAM_DIR / ".env"
TELEGRAM_SESSION = TELEGRAM_DIR / "API_수집" / "session" / "sosumonkey"
TELEGRAM_COLLECTION = TELEGRAM_DIR / "API_수집"
TELEGRAM_OUTPUT = TELEGRAM_COLLECTION / "인덱스"


def safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"
        ))


def run(label: str, cmd: list[str], cwd: Path | None = None, *, interactive: bool = False) -> bool:
    safe_print(f"--- {label} ---")
    if interactive:
        # 텔레그램 최초 로그인(인증코드)은 터미널 입력 필요
        r = subprocess.run(cmd, cwd=cwd or ROOT)
        if r.returncode != 0:
            safe_print(f"WARN: {label} exit {r.returncode}")
            if "dialog title matched" in (getattr(r, "stderr", "") or ""):
                safe_print("  → Telegram 앱에서 해당 채널에 가입했는지 확인하세요.")
                safe_print("  → .env 의 TG_ENTITY_TITLE 또는 TG_ENTITY(초대링크) 수정")
            return False
        return True
    r = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.stdout:
        safe_print(r.stdout.strip())
    if r.stderr:
        safe_print(r.stderr.strip())
    if r.returncode != 0:
        safe_print(f"WARN: {label} exit {r.returncode}")
        return False
    return True


def main() -> int:
    ok = True
    if TELEGRAM.exists() and TELEGRAM_ENV.exists():
        ok = run(
            "telegram collect",
            [
                sys.executable,
                str(TELEGRAM),
                "--env-file",
                str(TELEGRAM_ENV),
                "--session",
                str(TELEGRAM_SESSION),
                "--collection-dir",
                str(TELEGRAM_COLLECTION),
                "--output-dir",
                str(TELEGRAM_OUTPUT),
                "--limit",
                "300",
                "--download-media",
            ],
            ARCHIVE,
            interactive=False,
        ) and ok
    else:
        safe_print("telegram skip: script or .env missing")

    run("column collect", [sys.executable, str(ROOT / "scripts" / "column_collect.py")])

    ok = run("build dashboard", [sys.executable, str(ROOT / "scripts" / "build_dashboard.py")]) and ok
    run("health check", [sys.executable, str(ROOT / "scripts" / "health_check.py")])
    safe_print("collect_pipeline done" if ok else "collect_pipeline finished with warnings")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
