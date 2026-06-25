import type { DashboardData } from "./types";

export async function getDashboardData(): Promise<DashboardData> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL ?? ""}/data/dashboard.json`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("dashboard.json을 불러오지 못했습니다. npm run build:data 를 실행하세요.");
  }
  return res.json();
}

// 서버 컴포넌트용 — 파일 직접 읽기
import { readFile } from "fs/promises";
import path from "path";

export async function getDashboardDataFromFile(): Promise<DashboardData> {
  const filePath = path.join(process.cwd(), "public", "data", "dashboard.json");
  const raw = await readFile(filePath, "utf-8");
  return JSON.parse(raw);
}
