import type { SignalBoard } from "@/lib/types";
import { GradeBadge } from "../GradeBadge";

interface SignalTabProps {
  signals: SignalBoard[];
  latestDate: string | null;
}

export function SignalTab({ signals, latestDate }: SignalTabProps) {
  const latest = signals.find((s) => s.date === latestDate) ?? signals[signals.length - 1];

  if (!latest) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-amber-800">
        신호판 데이터가 없습니다. 소수몽키 에이전트에서 신호판을 생성한 뒤{" "}
        <code className="bg-amber-100 px-1 rounded">npm run build:data</code>를 실행하세요.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl border p-5">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <h2 className="text-lg font-bold">신호판 {latest.date}</h2>
          {Object.entries(latest.meta).map(([k, v]) => (
            <span key={k} className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-lg">
              {k}: {v}
            </span>
          ))}
        </div>

        <h3 className="font-semibold text-slate-700 mb-2">판독 요약</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-slate-50">
                <th className="border p-2 text-left w-20">등급</th>
                <th className="border p-2 text-left">신호</th>
                <th className="border p-2 text-left w-28">태그</th>
              </tr>
            </thead>
            <tbody>
              {latest.summary.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="border p-2">
                    <GradeBadge grade={row.grade} />
                  </td>
                  <td className="border p-2">{row.signal}</td>
                  <td className="border p-2 text-slate-500">{row.tags}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {latest.details.map((d, i) => (
        <div key={i} className="bg-white rounded-2xl border p-5">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="font-bold">{d.title}</h3>
            {d["등급"] && <GradeBadge grade={d["등급"].replace(/`/g, "")} />}
          </div>
          <dl className="space-y-2 text-sm">
            {Object.entries(d)
              .filter(([k]) => k !== "title")
              .map(([k, v]) => (
                <div key={k}>
                  <dt className="font-semibold text-slate-500">{k}</dt>
                  <dd className="text-slate-700 mt-0.5">{v}</dd>
                </div>
              ))}
          </dl>
        </div>
      ))}

      {latest.rebalancing.length > 0 && (
        <div className="bg-white rounded-2xl border p-5">
          <h3 className="font-bold mb-3">리밸런싱 영향</h3>
          <table className="w-full text-sm border-collapse">
            <tbody>
              {latest.rebalancing.map((r, i) => (
                <tr key={i}>
                  <td className="border p-2 font-mono font-semibold w-24">{r.target}</td>
                  <td className="border p-2">{r.impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {signals.length > 1 && (
        <div className="text-sm text-slate-500">
          이전 신호판: {signals.slice(0, -1).map((s) => s.date).join(", ")}
        </div>
      )}
    </div>
  );
}
