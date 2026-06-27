"use client";

import { useMemo, useState } from "react";
import type { ColumnCategory } from "@/lib/types";
import { MarkdownView } from "../MarkdownView";

interface ColumnsTabProps {
  columns: ColumnCategory[];
}

interface ArticleDetail {
  id: string;
  category: string;
  title: string;
  date?: string;
  dateLabel?: string;
  content: string;
}

export function ColumnsTab({ columns }: ColumnsTabProps) {
  const [activeCat, setActiveCat] = useState(columns[0]?.name ?? "");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<ArticleDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const category = columns.find((c) => c.name === activeCat) ?? columns[0];

  const filtered = useMemo(() => {
    const articles = [...(category?.articles ?? [])].sort((a, b) =>
      (b.date ?? "").localeCompare(a.date ?? "")
    );
    const q = query.trim().toLowerCase();
    if (!q) return articles;
    return articles.filter((a) => a.title.toLowerCase().includes(q));
  }, [category?.articles, query]);

  async function openArticle(id: string) {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/columns/${id}`);
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "불러오기 실패");
        return;
      }
      setSelected(data as ArticleDetail);
    } catch {
      setError("네트워크 오류");
    } finally {
      setLoading(false);
    }
  }

  if (!columns.length) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-amber-800 text-sm">
        칼럼 데이터 없음 — PC에서 <code className="bg-amber-100 px-1 rounded">npm run build:data</code> 실행
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-slate-600 text-sm">
        최신순 정렬 · 제목 클릭 시 본문 표시
      </p>

      <div className="flex flex-wrap gap-2">
        {columns.map((cat) => (
          <button
            key={cat.name}
            type="button"
            onClick={() => { setActiveCat(cat.name); setQuery(""); setSelected(null); }}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition ${
              activeCat === cat.name
                ? "bg-indigo-600 text-white"
                : "bg-white border text-slate-600 hover:border-indigo-300"
            }`}
          >
            {cat.name} ({cat.count})
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-4 min-h-[420px]">
        <div className="bg-white rounded-2xl border p-4 flex flex-col">
          <input
            type="search"
            placeholder={`${category?.name ?? ""}에서 검색…`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm mb-2"
          />
          <ul className="flex-1 overflow-y-auto divide-y divide-slate-100 max-h-[480px]">
            {filtered.map((a) => (
              <li key={a.id}>
                <button
                  type="button"
                  onClick={() => openArticle(a.id)}
                  disabled={loading}
                  className={`w-full text-left text-sm px-2 py-2 hover:bg-indigo-50 transition flex items-start justify-between gap-3 ${
                    selected?.id === a.id ? "bg-indigo-50 text-indigo-900" : "text-slate-700"
                  }`}
                >
                  <span className={`leading-snug ${selected?.id === a.id ? "font-medium" : ""}`}>
                    {a.title}
                  </span>
                  {a.dateLabel && (
                    <span className="text-xs text-slate-400 shrink-0 pt-0.5 tabular-nums">
                      {a.dateLabel}
                    </span>
                  )}
                </button>
              </li>
            ))}
            {filtered.length === 0 && (
              <li className="text-sm text-slate-400 px-2 py-4">검색 결과 없음</li>
            )}
          </ul>
          {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
        </div>

        <div className="bg-white rounded-2xl border p-4 overflow-y-auto max-h-[560px]">
          {loading && <p className="text-sm text-slate-500">불러오는 중…</p>}
          {!loading && !selected && (
            <div className="text-center text-slate-400 py-16 text-sm">
              ← 왼쪽 목록에서 글을 선택하세요
            </div>
          )}
          {selected && !loading && (
            <>
              <div className="flex flex-wrap items-center gap-2 mb-3 pb-2 border-b border-slate-100">
                <span className="text-xs text-indigo-600">{selected.category}</span>
                {selected.dateLabel && (
                  <span className="text-xs text-slate-400">{selected.dateLabel}</span>
                )}
              </div>
              <h2 className="text-lg font-bold text-slate-900 mb-2 leading-snug">{selected.title}</h2>
              <MarkdownView content={selected.content} compact />
            </>
          )}
        </div>
      </div>

      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-800">
        💡 추천: <strong>자산네제곱 프로젝트</strong> 최신 글부터, 1→6단계 순서대로
      </div>
    </div>
  );
}
