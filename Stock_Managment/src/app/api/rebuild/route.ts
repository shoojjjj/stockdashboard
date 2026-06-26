import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export async function POST() {
  if (process.env.PORTFOLIO_WRITE_ENABLED !== "true") {
    return NextResponse.json(
      { error: "Rebuild disabled. Local dev only (PORTFOLIO_WRITE_ENABLED=true)." },
      { status: 403 }
    );
  }

  const script = path.join(process.cwd(), "scripts", "build_dashboard.py");
  const result = await new Promise<{ ok: boolean; output: string }>((resolve) => {
    const proc = spawn("python", [script], { cwd: process.cwd() });
    let output = "";
    proc.stdout.on("data", (d) => { output += d.toString(); });
    proc.stderr.on("data", (d) => { output += d.toString(); });
    proc.on("close", (code) => resolve({ ok: code === 0, output }));
  });

  if (!result.ok) {
    return NextResponse.json({ error: "Build failed", detail: result.output }, { status: 500 });
  }

  return NextResponse.json({ ok: true, output: result.output.trim() });
}
