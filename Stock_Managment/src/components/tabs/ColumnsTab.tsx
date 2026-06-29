"use client";

import { useEffect, useMemo, useRef, useState } from "react";
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

function ArticleReader({
  article,
  fullscreen = false,
  onClose,
  closeLabel = "닫기 ✕",
}: {
  article: ArticleDetail;
  fullscreen?: boolean;
  onClose?: () => void;
  closeLabel?: string;
}) {
  return (
    <>
      <div
        className={`flex flex-wrap items-center gap-2 mb-3 pb-2 border-b border-slate-100 ${
          fullscreen ? "sticky top-0 bg-slate-50/95 backdrop-blur-sm z-10 pt-1 -mt-1" : ""
        }`}
      >
        {fullscreen && onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-sm px-3 py-1.5 rounded-lg bg-slate-800 text-white hover:bg-slate-700 shrink-0"
          >
            {closeLabel}
          </button>
        )}
        <span className="text-xs text-indigo-600">{article.category}</span>
        {article.dateLabel && (
          <span className="text-xs text-slate-400">{article.dateLabel}</span>
        )}
        <div className="ml-auto flex items-center gap-2">
          {!fullscreen && onClose && (
            <button
              type="button"
              onClick={onClose}
              className="text-xs px-2.5 py-1 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50"
            >
              넓게 읽기
            </button>
          )}
        </div>
      </div>
      <h2
        className={`font-bold text-slate-900 mb-2 leading-snug ${
          fullscreen ? "text-xl" : "text-base lg:text-lg"
        }`}
      >
        {article.title}
      </h2>
      <MarkdownView content={article.content} compact reader />
    </>
  );
}

function isMobileViewport() {
  return typeof window !== "undefined" && window.matchMedia("(max-width: 1023px)").matches;
}

export function ColumnsTab({ columns }: ColumnsTabProps) {
  const [activeCat, setActiveCat] = useState(columns[0]?.name ?? "");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<ArticleDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fullscreen, setFullscreen] = useState(false);
  const readerHistoryPushed = useRef(false);

  const category = columns.find((c) => c.name === activeCat) ?? columns[0];

  const filtered = useMemo(() => {
    const articles = [...(category?.articles ?? [])].sort((a, b) =>
      (b.date ?? "").localeCompare(a.date ?? "")
    );
    const q = query.trim().toLowerCase();
    if (!q) return articles;
    return articles.filter((a) => a.title.toLowerCase().includes(q));
  }, [category?.articles, query]);

  const showReaderOverlay = fullscreen && selected;

  function pushReaderHistory() {
    if (!readerHistoryPushed.current) {
      window.history.pushState({ columnReader: true }, "");
      readerHistoryPushed.current = true;
    }
  }

  function closeReader() {
    if (readerHistoryPushed.current) {
      readerHistoryPushed.current = false;
      window.history.back();
      return;
    }
    setFullscreen(false);
  }

  useEffect(() => {
    if (!showReaderOverlay) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeReader();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [showReaderOverlay]);

  useEffect(() => {
    const onPopState = () => {
      if (readerHistoryPushed.current || fullscreen) {
        readerHistoryPushed.current = false;
        setFullscreen(false);
      }
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, [fullscreen]);

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
      if (isMobileViewport()) {
        setFullscreen(true);
        pushReaderHistory();
      }
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
        <span className="hidden lg:inline"> · PC에서는 <strong>넓게 읽기</strong>로 전체 화면</span>
        <span className="lg:hidden"> · 모바일은 글 화면으로 바로 이동</span>
      </p>

      <div className="flex flex-wrap gap-2">
        {columns.map((cat) => (
          <button
            key={cat.name}
            type="button"
            onClick={() => {
              setActiveCat(cat.name);
              setQuery("");
              setSelected(null);
              if (readerHistoryPushed.current) {
                readerHistoryPushed.current = false;
                window.history.back();
              } else {
                setFullscreen(false);
              }
            }}
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

      <div className="grid lg:grid-cols-[minmax(220px,280px)_1fr] gap-4 min-h-0 lg:min-h-[420px]">
        <div className="bg-white rounded-2xl border p-4 flex flex-col lg:max-h-[calc(100vh-240px)]">
          <input
            type="search"
            placeholder={`${category?.name ?? ""}에서 검색…`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm mb-2"
          />
          <ul className="flex-1 overflow-y-auto divide-y divide-slate-100 min-h-0 lg:min-h-0 max-h-[60vh] lg:max-h-none">
            {filtered.map((a) => (
              <li key={a.id}>
                <button
                  type="button"
                  onClick={() => openArticle(a.id)}
                  disabled={loading}
                  className={`w-full text-left text-sm px-2 py-2.5 hover:bg-indigo-50 transition flex items-start justify-between gap-2 ${
                    selected?.id === a.id ? "bg-indigo-50 text-indigo-900" : "text-slate-700"
                  }`}
                >
                  <span className={`leading-snug ${selected?.id === a.id ? "font-medium" : ""}`}>
                    {a.title}
                  </span>
                  {a.dateLabel && (
                    <span className="text-[11px] text-slate-400 shrink-0 pt-0.5 tabular-nums">
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
          {loading && <p className="text-xs text-slate-500 mt-2">불러오는 중…</p>}
          {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
        </div>

        {/* PC: 오른쪽 미리보기 패널 */}
        <div className="hidden lg:block bg-white rounded-2xl border p-4 lg:p-5 overflow-y-auto lg:min-h-[480px] lg:max-h-[calc(100vh-240px)]">
          {!selected && (
            <div className="text-center text-slate-400 py-16 text-sm">
              ← 왼쪽 목록에서 글을 선택하세요
            </div>
          )}
          {selected && (
            <ArticleReader
              article={selected}
              onClose={() => {
                setFullscreen(true);
                pushReaderHistory();
              }}
            />
          )}
        </div>
      </div>

      {/* 모바일·PC 공통 전체 화면 읽기 */}
      {showReaderOverlay && (
        <div
          className="fixed inset-0 z-50 bg-slate-50"
          role="dialog"
          aria-modal="true"
          aria-label={selected.title}
        >
          <div className="h-full overflow-y-auto">
            <div className="max-w-5xl mx-auto px-4 sm:px-8 py-4 sm:py-8">
              <ArticleReader
                article={selected}
                fullscreen
                closeLabel="← 목록"
                onClose={closeReader}
              />
            </div>
          </div>
        </div>
      )}

      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-800">
        💡 추천: <strong>자산네제곱 프로젝트</strong> 최신 글부터, 1→6단계 순서대로
      </div>
    </div>
  );
}
