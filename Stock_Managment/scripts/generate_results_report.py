#!/usr/bin/env python3
"""전체 프로젝트 결과 보고서 HTML 생성."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ARCHIVE = Path(__file__).resolve().parent.parent.parent
STOCK = ARCHIVE / "Stock_Managment"
DASHBOARD_JSON = STOCK / "public" / "data" / "dashboard.json"
HEALTH_JSON = STOCK / "public" / "data" / "health.json"
OUTPUT = ARCHIVE / "Results_Report.html"

DEPLOY_URL = "https://stock-managment-black.vercel.app"
GITHUB = "https://github.com/shoojjjj/stockdashboard"
KST = ZoneInfo("Asia/Seoul")


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def git_last() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ARCHIVE), "log", "-1", "--format=%h %s (%ci)"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() if out.returncode == 0 else "-"
    except Exception:
        return "-"


def build_html(d: dict, health: dict) -> str:
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    today = d.get("today", {})
    agents = d.get("agents", [])
    agent_rows = "".join(
        f"<tr><td>{a.get('emoji','')} {a.get('name','')}</td>"
        f"<td>{'✅' if a.get('status')=='active' else '⏳'}</td>"
        f"<td>{a.get('role','')}</td></tr>"
        for a in agents
    )
    checks = health.get("checks", {})
    check_rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in checks.items()
    )
    pending = d.get("pendingInputs", 0)

    phases = [
        ("1단계", "MVP 대시보드", "✅", "6탭 UI, 신호판 연동"),
        ("2단계", "1_브리핑 + 자동갱신", "✅", "4에이전트 템플릿, 스케줄러"),
        ("3단계", "GitHub + Vercel", "✅", DEPLOY_URL),
        ("4단계", "풀 자동 파이프라인", "✅", "build→push→deploy, 1h 레포트"),
        ("5단계", "포트폴리오 입력 + 동기화", "✅", "웹 입력폼, sync_briefing.py"),
        ("6단계", "텔레그램 자동수집 + 신호판", "✅", "스케줄러 ON, signal stubs"),
        ("7단계", "스텁 자동 태그화", "✅", "auto_tag_stubs.py, S1~S3 규칙"),
        ("8단계", "Vercel 배포 + 포트폴리오 UX", "✅", "저장→rebuild, 신호판 push"),
        ("9단계", "GitHub 원격 동기화", "✅", "pull --rebase + 전체 푸시"),
    ]
    phase_rows = "".join(
        f"<tr><td>{p[0]}</td><td>{p[1]}</td><td>{p[2]}</td><td>{p[3]}</td></tr>"
        for p in phases
    )

    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stock Managment — 결과 보고서</title>
<style>
  body{{font-family:'Malgun Gothic',sans-serif;background:#0b1220;color:#e2e8f0;margin:0;padding:24px}}
  .wrap{{max-width:960px;margin:0 auto}}
  header{{background:linear-gradient(135deg,#059669,#0ea5e9);padding:36px;border-radius:20px;margin-bottom:24px}}
  h1{{margin:0 0 8px;font-size:1.8rem}}
  section{{background:#1e293b;border-radius:16px;padding:24px;margin-bottom:16px;border:1px solid #334155}}
  h2{{color:#34d399;margin:0 0 14px;font-size:1.15rem}}
  table{{width:100%;border-collapse:collapse;font-size:.9rem}}
  th,td{{border:1px solid #475569;padding:10px;text-align:left}}
  th{{background:#334155}}
  .hero{{background:#064e3b;border:2px solid #10b981;border-radius:14px;padding:20px;margin-bottom:16px;text-align:center}}
  .hero a{{color:#6ee7b7;font-size:1.15rem;font-weight:bold;text-decoration:none}}
  .warn{{background:#422006;border-color:#f59e0b;padding:16px;border-radius:12px;margin-top:12px}}
  .cmd{{background:#0f172a;padding:12px;border-radius:8px;font-family:Consolas,monospace;font-size:.85rem;margin-top:8px}}
  footer{{text-align:center;color:#64748b;font-size:.82rem;margin:24px 0}}
</style></head><body><div class="wrap">
<header>
  <h1>📋 Stock Managment — 최종 결과 보고서</h1>
  <p>생성: {now} KST · 1~9단계 완료</p>
</header>

<div class="hero">
  <p>🌐 라이브 대시보드</p>
  <a href="{DEPLOY_URL}" target="_blank">{DEPLOY_URL}</a>
  <p style="margin-top:12px;font-size:.9rem;opacity:.9">로그인 비밀번호: a419128</p>
</div>

<section>
  <h2>☀️ 오늘 투자 한눈에</h2>
  <p><strong>{today.get('headline','—')}</strong></p>
  <p>권장: {today.get('action','—')}</p>
  <p>신호판: {d.get('latestSignalDate','—')} · 신호 {len(d.get('signals',[]))}개 · 미입력 {pending}곳</p>
</section>

<section>
  <h2>🚀 완료된 단계 (1~9)</h2>
  <table><tr><th>단계</th><th>내용</th><th>상태</th><th>비고</th></tr>{phase_rows}</table>
</section>

<section>
  <h2>🤖 에이전트</h2>
  <table><tr><th>에이전트</th><th>상태</th><th>역할</th></tr>{agent_rows}</table>
</section>

<section>
  <h2>⚙️ 헬스체크</h2>
  <p>종합: <strong>{'OK' if health.get('healthy') else 'CHECK'}</strong></p>
  <table><tr><th>항목</th><th>결과</th></tr>{check_rows}</table>
</section>

<section>
  <h2>🔄 자동화 (매일)</h2>
  <table>
    <tr><td>06:00 DailyDeploy</td><td>빌드 → git push → Vercel</td></tr>
    <tr><td>06:00 DailyRefresh</td><td>텔레그램 수집 + JSON 빌드</td></tr>
    <tr><td>매 1시간 HourlyCheck</td><td>헬스체크 (레포트 1h throttle)</td></tr>
  </table>
  <p style="margin-top:10px;font-size:.85rem;color:#94a3b8">Git: {git_last()}</p>
</section>

<section>
  <h2>▶️ 지금 하면 되는 것</h2>
  <ol>
    <li><strong>포트폴리오 탭</strong> → 숫자 입력 → 저장 (로컬 dev)</li>
    <li>터미널: <code>npm run build:data</code> → <code>npm run deploy:quick</code></li>
    <li>매일 아침 Vercel 대시보드 확인</li>
  </ol>
  <div class="warn">
    <strong>⏳ 남은 1가지:</strong> 실제_보유현황.md 계좌 숫자 {pending}곳 — 대시보드 포트폴리오 탭에서 입력 가능
  </div>
  <div class="cmd">cd Stock_Managment<br>npm run dev          # 로컬 (포트폴리오 저장 가능)<br>npm run deploy:quick # Vercel 반영</div>
</section>

<footer>Results_Report.html · {GITHUB}</footer>
</div></body></html>"""


def main() -> None:
    health_script = STOCK / "scripts" / "health_check.py"
    subprocess.run([sys.executable, str(health_script)], check=False)
    d = load_json(DASHBOARD_JSON)
    h = load_json(HEALTH_JSON)
    OUTPUT.write_text(build_html(d, h), encoding="utf-8")
    print(f"Results report: {OUTPUT}")
    subprocess.Popen(["cmd", "/c", "start", "", str(OUTPUT)], shell=False)


if __name__ == "__main__":
    main()
