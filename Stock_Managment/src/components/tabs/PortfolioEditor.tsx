"use client";

import { useState } from "react";

const EMPTY_HOLDING = { ticker: "", qty: "", value: "", pnl: "", role: "", note: "" };

const DEFAULT_HOLDINGS = [
  { ticker: "MU", qty: "1", value: "", pnl: "", role: "장기/코어", note: "메모리 축" },
  { ticker: "DRAM ETF", qty: "", value: "", pnl: "", role: "장기/코어", note: "1층 메모리" },
  { ticker: "PLTR", qty: "", value: "", pnl: "", role: "스윙/전술", note: "추가 보류" },
  { ticker: "CRWV", qty: "", value: "", pnl: "", role: "옵션/고위험", note: "물타기 금지" },
];

interface Props {
  pendingInputs?: number;
}

export function PortfolioEditor({ pendingInputs = 0 }: Props) {
  const [totalValue, setTotalValue] = useState("");
  const [cash, setCash] = useState("");
  const [investRatio, setInvestRatio] = useState("");
  const [cashCapacity, setCashCapacity] = useState("있음");
  const [holdings, setHoldings] = useState(DEFAULT_HOLDINGS);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  function updateHolding(i: number, key: string, val: string) {
    setHoldings((prev) => prev.map((h, idx) => (idx === i ? { ...h, [key]: val } : h)));
  }

  function addRow() {
    setHoldings((prev) => [...prev, { ...EMPTY_HOLDING }]);
  }

  function removeRow(i: number) {
    setHoldings((prev) => prev.filter((_, idx) => idx !== i));
  }

  async function handleSave() {
    setLoading(true);
    setStatus("");
    try {
      const res = await fetch("/api/portfolio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ totalValue, cash, investRatio, cashCapacity, holdings }),
      });
      const data = await res.json();
      if (!res.ok) {
        setStatus(data.error || "저장 실패 — 로컬에서 PORTFOLIO_WRITE_ENABLED=true 필요");
        return;
      }
      const rebuild = await fetch("/api/rebuild", { method: "POST" });
      const rebuildData = await rebuild.json();
      if (rebuild.ok) {
        setStatus("저장 + 대시보드 갱신 완료! 새로고침하세요.");
        setTimeout(() => window.location.reload(), 1200);
      } else {
        setStatus(`MD 저장됨. 갱신: npm run build:data (${rebuildData.error || ""})`);
      }
    } catch {
      setStatus("네트워크 오류");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-2xl border border-indigo-100 p-5 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
        <h3 className="font-bold text-indigo-700">✏️ 포트폴리오 입력</h3>
        {pendingInputs > 0 && (
          <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full">
            미입력 {pendingInputs}곳
          </span>
        )}
      </div>
      <p className="text-xs text-slate-500 mb-4">
        숫자 입력 → 저장 시 MD 갱신 + dashboard.json 자동 빌드 (로컬 dev)
      </p>

      <div className="grid sm:grid-cols-3 gap-3 mb-4">
        {[
          ["총 평가금", totalValue, setTotalValue, "예: 5000만원"],
          ["현금/예수금", cash, setCash, "예: 800만원"],
          ["투자 비중", investRatio, setInvestRatio, "예: 85%"],
        ].map(([label, val, set, ph]) => (
          <label key={label as string} className="text-sm">
            <span className="text-slate-600">{label as string}</span>
            <input
              className="w-full mt-1 border rounded-lg px-3 py-2 text-sm"
              value={val as string}
              onChange={(e) => (set as (v: string) => void)(e.target.value)}
              placeholder={ph as string}
            />
          </label>
        ))}
      </div>

      <label className="text-sm block mb-4">
        <span className="text-slate-600">현금 여력</span>
        <select
          className="w-full mt-1 border rounded-lg px-3 py-2 text-sm"
          value={cashCapacity}
          onChange={(e) => setCashCapacity(e.target.value)}
        >
          <option value="있음">있음</option>
          <option value="부족">부족</option>
        </select>
      </label>

      <div className="overflow-x-auto mb-2">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50">
              {["티커", "수량", "평가금", "손익률", "역할", "비고", ""].map((h) => (
                <th key={h || "x"} className="border p-2">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {holdings.map((h, i) => (
              <tr key={i}>
                {(["ticker", "qty", "value", "pnl", "role", "note"] as const).map((k) => (
                  <td key={k} className="border p-1">
                    <input
                      className="w-full px-1 py-1 border-0 bg-transparent min-w-[4rem]"
                      value={h[k]}
                      onChange={(e) => updateHolding(i, k, e.target.value)}
                    />
                  </td>
                ))}
                <td className="border p-1 text-center">
                  <button
                    type="button"
                    onClick={() => removeRow(i)}
                    className="text-red-400 hover:text-red-600"
                    title="행 삭제"
                  >
                    ×
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        type="button"
        onClick={addRow}
        className="text-sm text-indigo-600 mb-4 hover:underline"
      >
        + 종목 추가
      </button>

      <div>
        <button
          onClick={handleSave}
          disabled={loading}
          className="bg-indigo-600 text-white px-5 py-2 rounded-xl text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? "저장 중…" : "저장 + 대시보드 갱신"}
        </button>
      </div>
      {status && <p className="text-sm mt-3 text-slate-600">{status}</p>}
    </div>
  );
}
