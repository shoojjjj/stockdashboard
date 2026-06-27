# Stock Managment

아카이브 기반 투자 대시보드

## 빠른 시작

```bash
npm install
npm run build:data
npm run dev          # http://localhost:3000
```

## 데이터 갱신

```bash
npm run build:data                    # 수동
npm run collect:columns               # 자산제곱 칼럼만 (네이버)
npm run collect                       # 텔레그램 + 칼럼 + 빌드
scripts/auto_refresh.bat              # Windows 더블클릭
powershell scripts/register_scheduler.ps1  # 매일 06:00 자동 등록
```

## 비밀번호 보호 (Vercel 배포 시)

```bash
cp .env.example .env.local
# DASHBOARD_PASSWORD=원하는비밀번호
```

Vercel 환경 변수에도 `DASHBOARD_PASSWORD` 추가.

## Vercel 배포

1. GitHub에 `아카이브` repo 푸시 (또는 `Stock_Managment`만 별도 repo)
2. Vercel Import → Root Directory: `Stock_Managment`
3. Environment: `DASHBOARD_PASSWORD`
4. Build: `npm run build` (아카이브가 상위에 있어야 `build:data` 동작)

> **단독 repo 배포 시:** `public/data/dashboard.json`을 커밋하거나 CI에서 생성.

## 폴더 구조

```
Stock_Managment/
  scripts/
    build_dashboard.py      # MD → JSON
    auto_refresh.ps1          # 매일 자동 갱신
    register_scheduler.ps1    # Windows 스케줄 등록
  public/data/dashboard.json
  src/                        # Next.js UI
```

## 연결된 아카이브 경로

| 데이터 | 아카이브 위치 |
|--------|---------------|
| 신호판 | `0_주식_에이전트/.../신호판/` |
| 현재판 | `1_브리핑/현재판.md` |
| 포트폴리오 | `1_브리핑/포트폴리오_브리핑/` |
| 자산제곱 | `1_브리핑/자산제곱_브리핑/` |
| 매매 회의 | `1_브리핑/토론_브리핑/` |
| 칼럼 | `칼럼/` (네이버 프리미엄 자동 수집 → MD) |

## 칼럼 자동 수집 (자산제곱 / 네이버 프리미엄)

1. `column_collect.env.example` → `column_collect.env` 복사
2. Chrome에서 네이버 로그인 + 자산제곱 구독 확인
3. DevTools → Network → 글 열기 → Request Headers → **Cookie** 전체 복사 → `NAVER_COOKIE=` 뒤에 붙여넣기
4. 실행:

```bash
npm run collect:columns    # 칼럼만
npm run build:data       # 대시보드 JSON 갱신
# 또는
npm run collect          # 텔레그램 + 칼럼 + 빌드 한번에
```

신규 글은 `아카이브/칼럼/{카테고리}/` 아래 MD로 저장되고, 📡 데이터 수집 버튼(`collect_pipeline`)에도 포함됩니다.


- [x] 1단계 MVP — 대시보드 6탭
- [x] 2단계 — `1_브리핑` 템플릿, 자동 갱신 스크립트, 비밀번호 보호
- [ ] 3단계 — GitHub Actions + Vercel 자동 배포
- [ ] 4단계 — 텔레그램/OCR 완전 자동화
