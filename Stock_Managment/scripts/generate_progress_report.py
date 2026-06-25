#!/usr/bin/env python3
"""진행 상황 HTML 레포트 생성 후 브라우저에서 연다."""

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
OUTPUT = ARCHIVE / "Progress_Report.html"

DEPLOY_URL = "https://stock-managment-black.vercel.app"
GITHUB_REPO = "https://github.com/shoojjjj/stockdashboard"

KST = ZoneInfo("Asia/Seoul")


def load_dashboard() -> dict:
    if DASHBOARD_JSON.exists():
        return json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
    return {}


def build_html(data: dict, steps: list[dict], deploy_url: str) -> str:
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    agents = data.get("agents", [])
    agent_rows = "".join(
        f"<tr><td>{a.get('emoji','')} {a.get('name','')}</td>"
        f"<td>{'✅ 연결' if a.get('status')=='active' else '⏳ 대기'}</td>"
        f"<td>{a.get('role','')}</td></tr>"
        for a in agents
    )
    step_cards = "".join(
        f"""<div class="step {'done' if s['done'] else 'pending'}">
          <div class="step-head"><span class="badge">{s['phase']}</span>
          <strong>{s['title']}</strong>
          <span class="status">{'✅ 완료' if s['done'] else '🔄 진행중'}</span></div>
          <p>{s['detail']}</p>
          {f'<p class="link"><a href="{s["url"]}" target="_blank">{s["url"]}</a></p>' if s.get('url') else ''}
          </div>"""
        for s in steps
    )
    today = data.get("today", {})
    signal_count = len(data.get("signals", []))
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
  .action{{display:inline-block;background:#f59e0b;color:#1e293b;padding:6px 14px;border-radius:20px;font-weight:700;font-size:.85rem;margin-top:8px}}
  table{{width:100%;border-collapse:collapse;font-size:.9rem}}
  th,td{{border:1px solid #475569;padding:10px;text-align:left}}
  th{{background:#334155}}
  .step{{background:#0f172a;border:1px solid #475569;border-radius:12px;padding:16px;margin-bottom:10px}}
  .step.done{{border-color:#059669}}
  .step-head{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px}}
  .badge{{background:#4f46e5;color:white;padding:2px 10px;border-radius:12px;font-size:.75rem}}
  .status{{margin-left:auto;font-size:.85rem}}
  .link a{{color:#38bdf8}}
  .next{{background:#164e63;border-color:#0891b2}}
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

<section>
  <h2>☀️ 오늘 한눈에</h2>
  <div class="hero">
    <p>{today.get('headline', '—')}</p>
    <span class="action">{today.get('action', '관망')}</span>
  </div>
  <p>최신 신호판: <strong>{data.get('latestSignalDate', '—')}</strong> · 신호판 {signal_count}개 · GitHub 푸시 완료</p>
</section>

<section>
  <h2>🤖 에이전트 연결</h2>
  <table><tr><th>에이전트</th><th>상태</th><th>역할</th></tr>{agent_rows}</table>
</section>

<section>
  <h2>🚀 진행 단계</h2>
  {step_cards}
</section>

<section class="next">
  <h2>▶️ 다음 액션 (본인)</h2>
  <ol>
    <li>Vercel 대시보드에서 Git 연결 → Root Directory: <code>Stock_Managment</code></li>
    <li>환경변수 <code>DASHBOARD_PASSWORD</code> 설정 (비밀번호 잠금)</li>
    <li>보유현황 MD 실제 숫자 입력 → <code>npm run build:data</code> → git push</li>
    <li><code>scripts/register_scheduler.ps1</code> 로 매일 06:00 자동 갱신</li>
  </ol>
</section>

<footer>Progress_Report.html · {GITHUB_REPO}</footer>
</div></body></html>"""


def main() -> None:
    data = load_dashboard()
    step3_done = "--step3-done" in sys.argv
    steps = [
        {"phase": "1단계", "title": "MVP 대시보드", "done": True,
         "detail": "Next.js 6탭 UI, build_dashboard.py, 신호판 연동"},
        {"phase": "2단계", "title": "1_브리핑 + 자동갱신", "done": True,
         "detail": "브리핑 템플릿 4에이전트, 비밀번호 보호, auto_refresh.ps1"},
        {"phase": "3단계", "title": "GitHub + Vercel 배포", "done": step3_done,
         "detail": "stockdashboard repo 푸시, Vercel 프로덕션 배포",
         "url": DEPLOY_URL if step3_done else None},
    ]
    html = build_html(data, steps, DEPLOY_URL)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Report: {OUTPUT}")
    subprocess.Popen(["cmd", "/c", "start", "", str(OUTPUT)], shell=False)


if __name__ == "__main__":
    main()
