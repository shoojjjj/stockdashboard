import { getDashboardDataFromFile } from "@/lib/data";
import { Dashboard } from "@/components/Dashboard";

export const dynamic = "force-dynamic";

export default async function Home() {
  let data;
  try {
    data = await getDashboardDataFromFile();
  } catch {
    return (
      <main className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-slate-800 mb-4">데이터가 아직 없습니다</h1>
        <p className="text-slate-600 mb-6">
          터미널에서 아래 명령을 실행해 주세요.
        </p>
        <code className="bg-slate-800 text-green-400 px-4 py-3 rounded-xl block max-w-sm mx-auto">
          npm run build:data
        </code>
      </main>
    );
  }

  const updated = new Date(data.generatedAt).toLocaleString("ko-KR", {
    timeZone: "Asia/Seoul",
  });

  return (
    <main className="max-w-4xl mx-auto px-4 py-6 sm:py-10">
      <header className="mb-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-indigo-600 text-sm font-semibold mb-1">Stock Managment</p>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">투자 관제탑</h1>
            <p className="text-slate-500 text-sm mt-1">아카이브 기반 · 2단계 (브리핑 + 자동갱신)</p>
          </div>
          <div className="text-right text-xs text-slate-400">
            <p>갱신: {updated}</p>
            <p>신호판: {data.latestSignalDate ?? "—"}</p>
          </div>
        </div>
      </header>

      <Dashboard data={data} />
    </main>
  );
}
