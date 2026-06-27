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
  content: string;
}

export function ColumnsTab({ columns }: ColumnsTabProps) {
  const [activeCat, setActiveCat] = useState(columns[0]?.name ?? "");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<ArticleDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const category = columns.find((c) => c.name === activeCat) ?? columns[0];
  const articles = category?.articles ?? [];

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return articles;
    return articles.filter((a) => a.title.toLowerCase().includes(q));
  }, [articles, query]);

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
        제목을 누르면 본문을 바로 읽을 수 있습니다. (아카이브 <code className="bg-slate-100 px-1 rounded">칼럼/</code> 연동)
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
            className="w-full border rounded-lg px-3 py-2 text-sm mb-3"
          />
          <ul className="flex-1 overflow-y-auto space-y-1 max-h-[480px] pr-1">
            {filtered.map((a) => (
              <li key={a.id}>
                <button
                  type="button"
                  onClick={() => openArticle(a.id)}
                  disabled={loading}
                  className={`w-full text-left text-sm px-3 py-2 rounded-lg hover:bg-indigo-50 transition ${
                    selected?.id === a.id ? "bg-indigo-100 text-indigo-900 font-medium" : "text-slate-700"
                  }`}
                >
                  {a.title}
                </button>
              </li>
            ))}
            {filtered.length === 0 && (
              <li className="text-sm text-slate-400 px-3 py-4">검색 결과 없음</li>
            )}
          </ul>
          {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
        </div>

        <div className="bg-white rounded-2xl border p-5 overflow-y-auto max-h-[560px]">
          {loading && <p className="text-sm text-slate-500">불러오는 중…</p>}
          {!loading && !selected && (
            <div className="text-center text-slate-400 py-16 text-sm">
              ← 왼쪽 목록에서 글을 선택하세요
            </div>
          )}
          {selected && !loading && (
            <>
              <p className="text-xs text-indigo-600 mb-1">{selected.category}</p>
              <h2 className="text-lg font-bold text-slate-900 mb-4">{selected.title}</h2>
              <MarkdownView content={selected.content} />
            </>
          )}
        </div>
      </div>

      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-800">
        💡 추천: <strong>자산네제곱 프로젝트</strong> 1→6단계 순서, 그다음 투자 전략
      </div>
    </div>
  );
}
