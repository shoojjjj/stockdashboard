"use client";

import { useEffect, useState } from "react";

interface CollectStatus {
  available: boolean;
  telegramLatest?: string;
  hint?: string;
}

export function CollectButton() {
  const [status, setStatus] = useState<CollectStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("/api/collect")
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({ available: false }));
  }, []);

  async function handleCollect() {
    setLoading(true);
    setMessage("");
    try {
      const res = await fetch("/api/collect", { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        setMessage("수집 완료! 새로고침합니다…");
        setTimeout(() => window.location.reload(), 1500);
      } else {
        setMessage(data.error || data.hint || "수집 실패");
      }
    } catch {
      setMessage("네트워크 오류");
    } finally {
      setLoading(false);
    }
  }

  const latest = status?.telegramLatest?.replace("ok - ", "") ?? "—";

  return (
    <div className="text-right">
      <button
        type="button"
        onClick={handleCollect}
        disabled={loading || status?.available === false}
        title={
          status?.available
            ? "PC에서 텔레그램 수집 → 신호판 → 대시보드 갱신"
            : "로컬 dev 전용 (Vercel에서는 비활성)"
        }
        className="inline-flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
      >
        {loading ? "수집 중…" : "📡 데이터 수집"}
      </button>
      <p className="text-xs text-slate-400 mt-1.5">
        텔레그램 최신: {latest}
        {!status?.available && status !== null && (
          <span className="block text-amber-600">로컬 PC에서만 수집 가능</span>
        )}
      </p>
      {message && <p className="text-xs text-slate-600 mt-1 max-w-xs ml-auto">{message}</p>}
    </div>
  );
}
