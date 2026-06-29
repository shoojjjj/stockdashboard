"use client";

import type { BriefingSlot } from "@/lib/types";
import { MarkdownView } from "../MarkdownView";

const STRATEGY_RATIONALE: Record<
  string,
  { label: string; className: string; text: string }
> = {
  "오늘 바로 할 것": {
    label: "전략 사유",
    className: "bg-emerald-50 border-emerald-200 text-emerald-900",
    text: "계좌 현금 0원·14종 풀투자 → 신규 매수보다 홀딩이 우선입니다. 소수몽키 AI·메모리 S3와 코어 보유(하이닉스·삼성·퀄컴 등) 방향은 일치하므로 추격 없이 유지만 합니다.",
  },
  "오늘 하지 말 것": {
    label: "전략 사유",
    className: "bg-rose-50 border-rose-200 text-rose-900",
    text: "여력 없이 매수·물타기·급등 추격은 테마 편중(메모리·AI) 리스크만 키웁니다. 레버리지 ETF는 시간 감쇠가 있어 추가 매수는 특히 금지입니다.",
  },
  "조건부 대기": {
    label: "중재 로직",
    className: "bg-indigo-50 border-indigo-200 text-indigo-900",
    text: "자산제곱 G2(눌림 진입) + 소수몽키 S3 + 포트폴리오 여력을 표로 합친 결과입니다. 현금이 없으면 좋은 신호라도 「현금 확보 전 보류」로 낮춥니다.",
  },
  "보유·수익 보호": {
    label: "포트폴리오 사유",
    className: "bg-amber-50 border-amber-200 text-amber-900",
    text: "코어(반도체·메모리)는 홀딩·추격 금지, 고위험(양자·위성)은 물타기 금지, 레버리지(CRCA/CRDU/RAM)는 감축 검토 — 종목 역할별로 규칙을 나눴습니다.",
  },
  "정리·감축 검토": {
    label: "감축 사유",
    className: "bg-orange-50 border-orange-200 text-orange-900",
    text: "2배 일일 ETF와 투기 테마는 변동성·감쇠 비용이 커서, 신규 충원 전 비중을 줄이거나 현금을 확보하는 쪽이 유리합니다.",
  },
  "핵심 합의": {
    label: "합의 근거",
    className: "bg-violet-50 border-violet-200 text-violet-900",
    text: "세 에이전트 입력이 AI 인프라·메모리 주도장에서 같은 방향을 가리킵니다. 다만 타이밍은 자산제곱 원칙대로 눌림/재지지가 공통 조건입니다.",
  },
  "핵심 불합의": {
    label: "조정 사유",
    className: "bg-slate-100 border-slate-300 text-slate-800",
    text: "신호는 강해도(ARM) 미보유·현금 부족이면 순위를 낮춥니다. 레버리지 3종 보유는 신규 NVDA/MSFT보다 감축을 먼저 검토하라는 뜻입니다.",
  },
  "사용자 확인 필요": {
    label: "확인 포인트",
    className: "bg-sky-50 border-sky-200 text-sky-900",
    text: "아래 항목은 규칙만으로 결정할 수 없습니다. 실제 계좌·손절 기준·감축 실행 여부는 본인이 체크해야 합니다.",
  },
};

function parseSections(content: string): { title: string; body: string }[] {
  const parts = content.split(/^## /m).filter(Boolean);
  return parts.map((block) => {
    const nl = block.indexOf("\n");
    if (nl === -1) return { title: block.trim(), body: "" };
    return {
      title: block.slice(0, nl).trim(),
      body: block.slice(nl + 1).trim(),
    };
  });
}

function StrategyNote({ title }: { title: string }) {
  const note = STRATEGY_RATIONALE[title];
  if (!note) return null;
  return (
    <div className={`mt-3 mb-1 rounded-xl border px-4 py-3 text-sm leading-relaxed ${note.className}`}>
      <span className="font-semibold text-xs uppercase tracking-wide opacity-80">
        💡 {note.label}
      </span>
      <p className="mt-1.5">{note.text}</p>
    </div>
  );
}

function SectionTable({ body }: { body: string }) {
  const lines = body.split("\n");
  const tableStart = lines.findIndex((l) => l.trim().startsWith("|"));
  if (tableStart === -1) {
    return <MarkdownView content={body} compact={false} />;
  }
  const before = lines.slice(0, tableStart).join("\n").trim();
  const tableLines = lines.slice(tableStart).filter((l) => l.trim().startsWith("|"));
  const rows = tableLines
    .filter((l) => !/^\|[\s\-:|]+\|$/.test(l.trim()))
    .map((l) =>
      l
        .trim()
        .replace(/^\|/, "")
        .replace(/\|$/, "")
        .split("|")
        .map((c) => c.trim())
    );

  return (
    <div className="space-y-3">
      {before && <MarkdownView content={before} compact={false} />}
      {rows.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-slate-50">
                {rows[0].map((cell, i) => (
                  <th key={i} className="border border-slate-200 px-2 py-1.5 text-left font-semibold">
                    {cell}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.slice(1).map((row, ri) => (
                <tr key={ri} className="hover:bg-slate-50/80">
                  {row.map((cell, ci) => (
                    <td key={ci} className="border border-slate-200 px-2 py-1.5">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export function MeetingTab({ slot }: { slot: BriefingSlot }) {
  if (!slot.ready || !slot.content) {
    return (
      <div className="bg-slate-50 border border-dashed border-slate-300 rounded-2xl p-8 text-center">
        <div className="text-4xl mb-3">⚖️</div>
        <h2 className="text-lg font-bold text-slate-700 mb-2">오늘 매매 회의</h2>
        <p className="text-slate-500">{slot.placeholder}</p>
      </div>
    );
  }

  const headerEnd = slot.content.indexOf("\n## ");
  const header = headerEnd === -1 ? slot.content : slot.content.slice(0, headerEnd).trim();
  const sections =
    headerEnd === -1 ? [] : parseSections(slot.content.slice(headerEnd + 1));

  return (
    <div className="bg-white rounded-2xl border p-6 space-y-6">
      <div>
        <h2 className="text-lg font-bold mb-2">⚖️ 오늘 매매 회의</h2>
        <p className="text-xs text-slate-500">
          결론 아래 <span className="text-indigo-600 font-medium">색상 코멘트</span>는 왜 그렇게
          판단했는지 전략 사유입니다.
        </p>
      </div>

      <div className="rounded-xl bg-slate-50 border border-slate-100 px-4 py-3">
        <MarkdownView content={header} compact={false} />
      </div>

      {sections.map((sec) => (
        <section key={sec.title}>
          <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-2 mb-2">
            {sec.title}
          </h3>
          <SectionTable body={sec.body} />
          <StrategyNote title={sec.title} />
        </section>
      ))}
    </div>
  );
}
