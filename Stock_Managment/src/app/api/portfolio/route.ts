import { NextResponse } from "next/server";
import { writeFile, access } from "fs/promises";
import path from "path";

export interface PortfolioPayload {
  totalValue: string;
  cash: string;
  investRatio: string;
  cashCapacity: string;
  holdings: {
    ticker: string;
    qty: string;
    value: string;
    pnl: string;
    role: string;
    note: string;
  }[];
}

function buildMd(data: PortfolioPayload, baseDate: string): string {
  const rows = data.holdings
    .filter((h) => h.ticker.trim())
    .map(
      (h) =>
        `| ${h.ticker} | ${h.qty || "-"} | ${h.value || "-"} | ${h.pnl || "-"} | ${h.role || "-"} | ${h.note || "-"} |`
    )
    .join("\n");

  return `# 실제 보유현황

> 기준일: ${baseDate}
> 출처: 사용자 계좌 스냅샷 (대시보드에서 저장)

## 계좌 요약

| 항목 | 값 |
|------|-----|
| 총 평가금 | ${data.totalValue || "-"} |
| 현금/예수금 | ${data.cash || "-"} |
| 투자 비중 | ${data.investRatio || "-"} |

## 보유 종목

| 티커 | 수량 | 평가금 | 손익률 | 계좌 역할 | 비고 |
|------|------|--------|--------|-----------|------|
${rows || "| _(종목 없음)_ | | | | | |"}

## 현금·여력

- 조건부 정찰병 여력: ${data.cashCapacity || "_(확인)_"}
- 동일 테마 중복 노출: _(확인 필요)_

## 수익 보호·정리 플래그

| 티커 | 플래그 | 사유 |
|------|--------|------|
| SLV/GDX | 정리 후보 | 소수몽키 신호와 직접 관련 낮음 |

## 점검 메모

- 보유 이유가 아직 유효한가?
- 급등 추격 여력이 있는가?
- 수익 보호가 먼저인 종목이 있는가?
`;
}

function getArchiveRoot(): string {
  const root = process.env.ARCHIVE_ROOT;
  if (root) return root;
  return path.resolve(process.cwd(), "..");
}

export async function POST(request: Request) {
  if (process.env.PORTFOLIO_WRITE_ENABLED !== "true") {
    return NextResponse.json(
      { error: "Portfolio write disabled. Set PORTFOLIO_WRITE_ENABLED=true locally." },
      { status: 403 }
    );
  }

  const archiveRoot = getArchiveRoot();
  const target = path.join(
    archiveRoot,
    "1_브리핑",
    "포트폴리오_브리핑",
    "00_현황",
    "실제_보유현황.md"
  );

  try {
    await access(path.dirname(target));
  } catch {
    return NextResponse.json({ error: "Archive path not accessible on this server." }, { status: 503 });
  }

  const body = (await request.json()) as PortfolioPayload;
  const baseDate = new Date().toISOString().slice(0, 10);
  const md = buildMd(body, baseDate);

  await writeFile(target, md, "utf-8");

  return NextResponse.json({
    ok: true,
    path: target,
    hint: "Run npm run build:data to refresh dashboard",
  });
}
