"use client";

import { useState } from "react";
import type { SignalBoard } from "@/lib/types";
import { GradeBadge } from "../GradeBadge";

interface SignalTabProps {
  signals: SignalBoard[];
  latestDate: string | null;
}

export function SignalTab({ signals, latestDate }: SignalTabProps) {
  const sorted = [...signals].sort((a, b) => a.date.localeCompare(b.date));
  const [selectedDate, setSelectedDate] = useState(latestDate ?? sorted[sorted.length - 1]?.date ?? "");

  const selected =
    sorted.find((s) => s.date === selectedDate) ?? sorted[sorted.length - 1];

  if (!selected) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-amber-800">
        신호판 데이터가 없습니다. 상단 <strong>데이터 수집</strong> 버튼(로컬 PC) 또는{" "}
        <code className="bg-amber-100 px-1 rounded">npm run collect</code> 실행
      </div>
    );
  }

  const isAuto = Object.values(selected.meta).some((v) => v.includes("auto-tagged"));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-slate-600">
          날짜 선택
          <select
            className="ml-2 border rounded-lg px-3 py-1.5 text-sm font-medium"
            value={selected.date}
            onChange={(e) => setSelectedDate(e.target.value)}
          >
            {[...sorted].reverse().map((s) => (
              <option key={s.date} value={s.date}>
                {s.date} ({s.summary.length}건)
              </option>
            ))}
          </select>
        </label>
        {isAuto && (
          <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-lg">
            자동 태그 — Cursor 수동 태그화 시 품질 향상
          </span>
        )}
      </div>

      <div className="bg-white rounded-2xl border p-5">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <h2 className="text-lg font-bold">신호판 {selected.date}</h2>
          {Object.entries(selected.meta).map(([k, v]) => (
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
              {selected.summary.map((row, i) => (
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

      {selected.details.map((d, i) => (
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

      {selected.rebalancing.length > 0 && (
        <div className="bg-white rounded-2xl border p-5">
          <h3 className="font-bold mb-3">리밸런싱 영향</h3>
          <table className="w-full text-sm border-collapse">
            <tbody>
              {selected.rebalancing.map((r, i) => (
                <tr key={i}>
                  <td className="border p-2 font-mono font-semibold w-24">{r.target}</td>
                  <td className="border p-2">{r.impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
