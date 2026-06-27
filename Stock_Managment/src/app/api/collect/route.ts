import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { readFile } from "fs/promises";

function localEnabled() {
  return (
    process.env.COLLECT_ENABLED === "true" ||
    process.env.PORTFOLIO_WRITE_ENABLED === "true"
  );
}

function getArchiveRoot(): string {
  return process.env.ARCHIVE_ROOT || path.resolve(process.cwd(), "..");
}

async function readHealth() {
  try {
    const raw = await readFile(
      path.join(process.cwd(), "public", "data", "health.json"),
      "utf-8"
    );
    return JSON.parse(raw) as { checks?: Record<string, string> };
  } catch {
    return null;
  }
}

export async function GET() {
  const health = await readHealth();
  const checks = health?.checks ?? {};
  return NextResponse.json({
    available: localEnabled(),
    telegramEnv: checks.telegram_env ?? "unknown",
    telegramLatest: checks.telegram_latest ?? "unknown",
    columnLatest: checks.column_latest ?? "unknown",
    columnCookie: checks.column_cookie ?? "unknown",
    signalBoards: checks.signal_boards ?? "unknown",
    hint: localEnabled()
      ? "PC 로컬 — 수집 버튼 사용 가능"
      : "Vercel에서는 수집 불가. 로컬 npm run dev + COLLECT_ENABLED=true",
  });
}

export async function POST() {
  if (!localEnabled()) {
    return NextResponse.json(
      {
        error: "텔레그램 수집은 PC 로컬에서만 가능합니다.",
        hint: "Stock_Managment/.env.local 에 COLLECT_ENABLED=true 설정 후 npm run dev",
      },
      { status: 403 }
    );
  }

  const script = path.join(process.cwd(), "scripts", "collect_pipeline.py");
  const result = await new Promise<{ ok: boolean; output: string }>((resolve) => {
    const proc = spawn("python", [script], {
      cwd: process.cwd(),
      env: { ...process.env, ARCHIVE_ROOT: getArchiveRoot() },
    });
    let output = "";
    proc.stdout.on("data", (d) => { output += d.toString(); });
    proc.stderr.on("data", (d) => { output += d.toString(); });
    proc.on("close", (code) => resolve({ ok: code === 0, output }));
  });

  if (!result.ok) {
    return NextResponse.json(
      { error: "수집 실패", detail: result.output.slice(-2000) },
      { status: 500 }
    );
  }

  return NextResponse.json({
    ok: true,
    message: "텔레그램 + 칼럼 수집 + 대시보드 갱신 완료",
    output: result.output.trim().split("\n").slice(-8).join("\n"),
  });
}
