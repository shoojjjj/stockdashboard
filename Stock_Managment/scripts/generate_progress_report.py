#!/usr/bin/env python3
"""진행 상황 HTML 레포트 생성 후 브라우저에서 연다."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ARCHIVE = Path(__file__).resolve().parent.parent.parent
STOCK = ARCHIVE / "Stock_Managment"
DASHBOARD_JSON = STOCK / "public" / "data" / "dashboard.json"
LOG_DIR = STOCK / "logs"
OUTPUT = ARCHIVE / "Progress_Report.html"
LAST_OPEN_FILE = LOG_DIR / "last_report_open.txt"
OPEN_INTERVAL_SEC = 3600  # 1 hour

DEPLOY_URL = "https://stock-managment-black.vercel.app"
GITHUB_REPO = "https://github.com/shoojjjj/stockdashboard"

KST = ZoneInfo("Asia/Seoul")


def load_dashboard() -> dict:
    if DASHBOARD_JSON.exists():
        return json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
    return {}


def load_health() -> dict:
    health_file = STOCK / "public" / "data" / "health.json"
    if health_file.exists():
        return json.loads(health_file.read_text(encoding="utf-8"))
    return {"healthy": False, "checks": {}}


def run_health_check() -> dict:
    script = STOCK / "scripts" / "health_check.py"
    try:
        subprocess.run([sys.executable, str(script)], check=True, timeout=30)
    except Exception:
        pass
    return load_health()


def load_system_status() -> dict:
    health = run_health_check()
    status = {
        "scheduler_deploy": health.get("checks", {}).get("scheduler_deploy", "unknown"),
        "scheduler_refresh": health.get("checks", {}).get("scheduler_refresh", "unknown"),
        "vercel_site": health.get("checks", {}).get("vercel_site", "unknown"),
        "dashboard_json": health.get("checks", {}).get("dashboard_json", "unknown"),
        "telegram_env": health.get("checks", {}).get("telegram_env", "unknown"),
        "github_remote": health.get("checks", {}).get("github_remote", "unknown"),
        "health": "OK" if health.get("healthy") else "CHECK",
        "last_commit": "-",
        "vercel_password": "not set (local dev: open access)",
    }
    try:
        out = subprocess.run(
            ["git", "-C", str(ARCHIVE), "log", "-1", "--format=%h %s (%ci)"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            status["last_commit"] = out.stdout.strip()
    except Exception:
        pass
    if "--vercel-password-set" in sys.argv:
        status["vercel_password"] = "Production locked (password set)"
    return status


def load_latest_log() -> str:
    if not LOG_DIR.exists():
        return "(로그 없음)"
    logs = sorted(LOG_DIR.glob("refresh_*.log"), reverse=True)
    if not logs:
        return "(로그 없음)"
    lines = logs[0].read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-12:])


def parse_args() -> dict:
    phase_done = {1: True, 2: True, 3: "--step3-done" in sys.argv or "--step4-done" in sys.argv,
                  4: "--step4-done" in sys.argv}
    message = ""
    for i, arg in enumerate(sys.argv):
        if arg == "--message" and i + 1 < len(sys.argv):
            message = sys.argv[i + 1]
    return {"phase_done": phase_done, "message": message}


def build_html(data: dict, steps: list[dict], deploy_url: str, milestone: str, log_tail: str, sys_status: dict) -> str:
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    agents = data.get("agents", [])
    agent_rows = "".join(
        f"<tr><td>{a.get('emoji','')} {a.get('name','')}</td>"
        f"<td>{'✅ 연결' if a.get('status')=='active' else '⏳ 대기'}</td>"
        f"<td>{a.get('role','')}</td></tr>"
        for a in agents
    )
    step_cards = "".join(
        f"""<div class="step {'done' if s['done'] else ('active' if s.get('active') else 'pending')}">
          <div class="step-head"><span class="badge">{s['phase']}</span>
          <strong>{s['title']}</strong>
          <span class="status">{'✅ 완료' if s['done'] else ('🔄 진행중' if s.get('active') else '⏳ 대기')}</span></div>
          <p>{s['detail']}</p>
          {f'<p class="link"><a href="{s["url"]}" target="_blank">{s["url"]}</a></p>' if s.get('url') else ''}
          </div>"""
        for s in steps
    )
    today = data.get("today", {})
    signal_count = len(data.get("signals", []))
    milestone_block = (
        f'<section class="milestone"><h2>📌 이번 작업</h2><p>{milestone}</p></section>'
        if milestone
        else ""
    )
    log_escaped = re.sub(r"<", "&lt;", log_tail)
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>진행 레포트 — Stock Managment</title>
<style>
  body{{font-family:'Malgun Gothic',sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:24px}}
  .wrap{{max-width:920px;margin:0 auto}}
  header{{background:linear-gradient(135deg,#4f46e5,#0ea5e9);padding:32px;border-radius:20px;margin-bottom:24px}}
  h1{{margin:0 0 8px;font-size:1.6rem}}
  .meta{{opacity:.9;font-size:.9rem}}
  section{{background:#1e293b;border-radius:16px;padding:24px;margin-bottom:16px;border:1px solid #334155}}
  h2{{color:#818cf8;margin:0 0 16px;font-size:1.15rem}}
  .hero{{background:#312e81;border-radius:12px;padding:16px 20px;margin-bottom:12px}}
  .deploy{{background:#065f46;border:2px solid #10b981;border-radius:12px;padding:20px;margin-bottom:16px;text-align:center}}
  .deploy a{{color:#6ee7b7;font-size:1.2rem;font-weight:bold}}
  .milestone{{background:#422006;border-color:#f59e0b}}
  .action{{display:inline-block;background:#f59e0b;color:#1e293b;padding:6px 14px;border-radius:20px;font-weight:700;font-size:.85rem;margin-top:8px}}
  table{{width:100%;border-collapse:collapse;font-size:.9rem}}
  th,td{{border:1px solid #475569;padding:10px;text-align:left}}
  th{{background:#334155}}
  .step{{background:#0f172a;border:1px solid #475569;border-radius:12px;padding:16px;margin-bottom:10px}}
  .step.done{{border-color:#059669}}
  .step.active{{border-color:#f59e0b;box-shadow:0 0 0 2px #f59e0b33}}
  .step-head{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px}}
  .badge{{background:#4f46e5;color:white;padding:2px 10px;border-radius:12px;font-size:.75rem}}
  .status{{margin-left:auto;font-size:.85rem}}
  .link a{{color:#38bdf8}}
  .log{{background:#0f172a;border:1px solid #475569;border-radius:8px;padding:12px;font-family:Consolas,monospace;font-size:.75rem;white-space:pre-wrap;color:#94a3b8}}
  code{{background:#334155;padding:2px 6px;border-radius:4px;font-size:.85rem}}
  footer{{text-align:center;color:#64748b;font-size:.8rem;margin-top:24px}}
</style></head><body><div class="wrap">
<header>
  <h1>📊 Stock Managment 진행 레포트</h1>
  <p class="meta">갱신: {now}</p>
</header>

<section>
  <div class="deploy">
    <p>🌐 라이브 대시보드</p>
    <a href="{deploy_url}" target="_blank">{deploy_url}</a>
  </div>
</section>

{milestone_block}

<section>
  <h2>☀️ 오늘 한눈에</h2>
  <div class="hero">
    <p>{today.get('headline', '—')}</p>
    <span class="action">{today.get('action', '관망')}</span>
  </div>
  <p>최신 신호판: <strong>{data.get('latestSignalDate', '—')}</strong> · 신호판 {signal_count}개 · 미입력 <strong>{data.get('pendingInputs', 0)}</strong>곳</p>
</section>

<section>
  <h2>🤖 에이전트 연결</h2>
  <table><tr><th>에이전트</th><th>상태</th><th>역할</th></tr>{agent_rows}</table>
</section>

<section>
  <h2>🚀 진행 단계</h2>
  {step_cards}
</section>

<section>
  <h2>⚙️ 시스템 헬스체크</h2>
  <table>
    <tr><td>종합</td><td><strong>{sys_status.get('health','-')}</strong></td></tr>
    <tr><td>Vercel 사이트</td><td>{sys_status.get('vercel_site','-')}</td></tr>
    <tr><td>dashboard.json</td><td>{sys_status.get('dashboard_json','-')}</td></tr>
    <tr><td>자동 배포 스케줄</td><td>{sys_status.get('scheduler_deploy','-')}</td></tr>
    <tr><td>데이터 갱신 스케줄</td><td>{sys_status.get('scheduler_refresh','-')}</td></tr>
    <tr><td>텔레그램 .env</td><td>{sys_status.get('telegram_env','-')}</td></tr>
    <tr><td>GitHub remote</td><td>{sys_status.get('github_remote','-')}</td></tr>
    <tr><td>최근 Git 커밋</td><td><code>{sys_status.get('last_commit','-')}</code></td></tr>
    <tr><td>Vercel 로그인</td><td>{sys_status.get('vercel_password','-')}</td></tr>
  </table>
</section>

<section>
  <h2>📋 최근 자동화 로그</h2>
  <div class="log">{log_escaped}</div>
</section>

<footer>Progress_Report.html · {GITHUB_REPO}</footer>
</div></body></html>"""


def should_open_browser() -> bool:
    if "--no-open" in sys.argv:
        return False
    if "--force-open" in sys.argv:
        return True
    if "--smart-open" not in sys.argv:
        return True  # manual run: always open

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST)
    if LAST_OPEN_FILE.exists():
        try:
            last = datetime.fromisoformat(LAST_OPEN_FILE.read_text(encoding="utf-8").strip())
            if last.tzinfo is None:
                last = last.replace(tzinfo=KST)
            elapsed = (now - last).total_seconds()
            if elapsed < OPEN_INTERVAL_SEC and "--meaningful" not in sys.argv:
                print(f"Report saved (browser skip: {int(elapsed)}s since last open, < 1h)")
                return False
        except ValueError:
            pass
    return True


def record_browser_open() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LAST_OPEN_FILE.write_text(datetime.now(KST).isoformat(), encoding="utf-8")


def default_steps(phase_done: dict, phase_active: int = 0) -> list[dict]:
    return [
        {"phase": "1단계", "title": "MVP 대시보드", "done": True,
         "detail": "Next.js 6탭 UI, build_dashboard.py, 신호판 연동"},
        {"phase": "2단계", "title": "1_브리핑 + 자동갱신", "done": True,
         "detail": "브리핑 템플릿, 비밀번호 보호, Windows 스케줄러 06:00"},
        {"phase": "3단계", "title": "GitHub + Vercel 배포", "done": phase_done.get(3, False),
         "detail": "stockdashboard 푸시, stock-managment-black.vercel.app",
         "url": DEPLOY_URL if phase_done.get(3) else None},
        {"phase": "4단계", "title": "풀 자동 파이프라인", "done": phase_done.get(4, False),
         "active": phase_active == 4 and not phase_done.get(4, False),
         "detail": "수집→빌드→git push→Vercel 재배포 원클릭/스케줄"},
    ]


def main() -> None:
    args = parse_args()
    phase_active = 4 if "--step4-active" in sys.argv else 0
    if "--step4-done" in sys.argv:
        args["phase_done"][4] = True
        args["phase_done"][3] = True

    data = load_dashboard()
    steps = default_steps(args["phase_done"], phase_active)
    html = build_html(
        data, steps, DEPLOY_URL, args["message"], load_latest_log(), load_system_status()
    )

    OUTPUT.write_text(html, encoding="utf-8")
    ts = datetime.now(KST).strftime("%Y%m%d_%H%M")
    archive_copy = ARCHIVE / f"Progress_Report_{ts}.html"
    archive_copy.write_text(html, encoding="utf-8")

    print(f"Report: {OUTPUT}")
    print(f"Copy:   {archive_copy}")
    if should_open_browser():
        record_browser_open()
        subprocess.Popen(["cmd", "/c", "start", "", str(OUTPUT)], shell=False)


if __name__ == "__main__":
    main()
