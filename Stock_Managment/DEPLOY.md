# Stock Managment — Vercel 배포 가이드

## 1. GitHub 푸시 (최초 1회)

```powershell
cd C:\Users\JEON\Desktop\아카이브
git init
git add .
git commit -m "feat: Stock Managment dashboard phase 1-3"
git branch -M main
git remote add origin https://github.com/shoojjjj/stockdashboard.git
git push -u origin main
```

## 2. Vercel 연결

1. https://vercel.com → Add New Project
2. Import `shoojjjj/stockdashboard`
3. **Root Directory**: `Stock_Managment` ← 중요!
4. Framework: Next.js (자동 감지)
5. Environment Variables:
   - `DASHBOARD_PASSWORD` = 원하는 비밀번호

## 3. 배포 후

- URL: `https://stockdashboard-xxx.vercel.app`
- 로그인 페이지에서 비밀번호 입력

## 4. 데이터 갱신 흐름

```
로컬: scripts/auto_refresh.bat
  → dashboard.json 갱신
  → git add + commit + push
  → Vercel 자동 재배포
```

또는 GitHub Actions (`.github/workflows/dashboard-refresh.yml`) cron 사용

## 주의

- `.env` (텔레그램 키)는 Git에 올리지 않음
- 사진 650장은 `.gitignore`로 제외 (MD/JSON만 푸시)
