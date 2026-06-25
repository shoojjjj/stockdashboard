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

KST = ZoneInfo("Asia/Seoul")


def load_dashboard() -> dict:
    if DASHBOARD_JSON.exists():
        return json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
    return {}


def count_files(folder: Path, pattern: str = "**/*") -> int:
    if not folder.exists():
        return 0
    return sum(1 for f in folder.rglob(pattern.split("/")[-1]) if f.is_file())


def build_html(data: dict, steps: list[dict]) -> str:
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
          <p>{s['detail']}</p></div>"""
        for s in steps
    )
    today = data.get("today", {})
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
  .action{{display:inline-block;background:#f59e0b;color:#1e293b;padding:6px 14px;border-radius:20px;font-weight:700;font-size:.85rem;margin-top:8px}}
  table{{width:100%;border-collapse:collapse;font-size:.9rem}}
  th,td{{border:1px solid #475569;padding:10px;text-align:left}}
  th{{background:#334155}}
  .step{{background:#0f172a;border:1px solid #475569;border-radius:12px;padding:16px;margin-bottom:10px}}
  .step.done{{border-color:#059669}}
  .step-head{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px}}
  .badge{{background:#4f46e5;color:white;padding:2px 10px;border-radius:12px;font-size:.75rem}}
  .status{{margin-left:auto;font-size:.85rem}}
  .next{{background:#164e63;border-color:#0891b2}}
  code{{background:#334155;padding:2px 6px;border-radius:4px;font-size:.85rem}}
  footer{{text-align:center;color:#64748b;font-size:.8rem;margin-top:24px}}
</style></head><body><div class="wrap">
<header>
  <h1>📊 Stock Managment 진행 레포트</h1>
  <p class="meta">갱신: {now} · 단계 3 진행 중</p>
</header>

<section>
  <h2>☀️ 오늘 한눈에</h2>
  <div class="hero">
    <p>{today.get('headline', '—')}</p>
    <span class="action">{today.get('action', '관망')}</span>
  </div>
  <p>최신 신호판: <strong>{data.get('latestSignalDate', '—')}</strong></p>
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
  <h2>▶️ 다음 액션</h2>
  <ol>
    <li>GitHub <code>stockdashboard</code> repo에 푸시</li>
    <li>Vercel Import → Root Directory: <code>Stock_Managment</code></li>
    <li>환경변수 <code>DASHBOARD_PASSWORD</code> 설정</li>
    <li>보유현황 MD에 실제 계좌 숫자 입력</li>
  </ol>
</section>

<footer>Progress_Report.html · 자동 생성</footer>
</div></body></html>"""


def main() -> None:
    data = load_dashboard()
    steps = [
        {"phase": "1단계", "title": "MVP 대시보드", "done": True,
         "detail": "Next.js 6탭 UI, build_dashboard.py, 신호판 연동"},
        {"phase": "2단계", "title": "1_브리핑 + 자동갱신", "done": True,
         "detail": "브리핑 템플릿, 비밀번호 보호, auto_refresh.ps1, GitHub Actions"},
        {"phase": "3단계", "title": "Git + Vercel 배포", "done": False,
         "detail": "git init, .gitignore, vercel.json, repo 푸시 준비"},
    ]
    # argv로 완료 표시: python generate_progress_report.py --step3-done
    if "--step3-done" in sys.argv:
        steps[2]["done"] = True
    html = build_html(data, steps)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Report: {OUTPUT}")
    subprocess.Popen(["cmd", "/c", "start", "", str(OUTPUT)], shell=False)


if __name__ == "__main__":
    main()
