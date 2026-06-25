import type { ColumnCategory } from "@/lib/types";

interface ColumnsTabProps {
  columns: ColumnCategory[];
}

export function ColumnsTab({ columns }: ColumnsTabProps) {
  return (
    <div className="space-y-4">
      <p className="text-slate-600 text-sm">
        아카이브 <code className="bg-slate-100 px-1 rounded">칼럼/</code> 폴더의 읽을거리 목록입니다.
        Obsidian에서 깊이 읽고, 대시보드에서는 무엇을 읽을지 고르세요.
      </p>
      <div className="grid sm:grid-cols-2 gap-4">
        {columns.map((cat) => (
          <div key={cat.name} className="bg-white rounded-2xl border p-5">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-bold">{cat.name}</h3>
              <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-2 py-1 rounded-full">
                {cat.count}편
              </span>
            </div>
            <ul className="text-sm text-slate-600 space-y-1">
              {cat.samples.map((s) => (
                <li key={s} className="truncate" title={s}>
                  · {s}
                </li>
              ))}
              {cat.count > 5 && (
                <li className="text-slate-400">… 외 {cat.count - 5}편</li>
              )}
            </ul>
          </div>
        ))}
      </div>
      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-800">
        💡 추천 순서: <strong>자산네제곱 프로젝트</strong> 1단계 → 6단계 순서대로, 그다음 투자 전략 글을 골라 읽기
      </div>
    </div>
  );
}
