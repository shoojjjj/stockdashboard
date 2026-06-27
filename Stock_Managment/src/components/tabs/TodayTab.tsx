import type { TodaySummary, Agent, BriefingSlot, DailySnapshot } from "@/lib/types";
import { AgentStatus } from "../AgentStatus";

interface TodayTabProps {
  today: TodaySummary;
  agents: Agent[];
  latestDate: string | null;
  generatedAt: string;
  meeting?: BriefingSlot;
  pendingInputs?: number;
  dailyHistory?: DailySnapshot[];
}

export function TodayTab({ today, agents, latestDate, generatedAt, meeting, pendingInputs, dailyHistory }: TodayTabProps) {
  const updated = new Date(generatedAt).toLocaleString("ko-KR", { timeZone: "Asia/Seoul" });

  return (
    <div>
      <AgentStatus agents={agents} />

      <div className="bg-gradient-to-br from-indigo-600 to-sky-500 text-white rounded-2xl p-6 mb-5 shadow-lg">
        <p className="text-indigo-100 text-sm mb-1">오늘의 한 줄</p>
        <h2 className="text-xl font-bold mb-4">{today.headline}</h2>
        <div className="inline-block bg-white/20 px-4 py-2 rounded-xl text-sm font-semibold">
          권장 행동: {today.action}
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-5 mb-4">
        <h3 className="font-bold text-slate-700 mb-3">핵심 신호 요약</h3>
        <ul className="space-y-2">
          {today.bullets.map((b, i) => (
            <li key={i} className="text-sm text-slate-600 pl-3 border-l-2 border-indigo-300">
              {b}
            </li>
          ))}
        </ul>
      </div>

      {(pendingInputs ?? 0) > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4 text-sm text-amber-900">
          <strong>📝 입력 대기 {pendingInputs}곳</strong> — 포트폴리오 MD에 실제 계좌 숫자를 채운 뒤{" "}
          <code className="bg-amber-100 px-1 rounded">npm run build:data</code> 실행
        </div>
      )}

      <div className="grid sm:grid-cols-2 gap-3 text-sm text-slate-500">
        <div className="bg-white rounded-xl border p-4">
          <span className="font-semibold text-slate-700">최신 신호판</span>
          <p className="mt-1">{latestDate ?? "없음"}</p>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <span className="font-semibold text-slate-700">데이터 갱신</span>
          <p className="mt-1">{updated}</p>
        </div>
      </div>

      {(dailyHistory?.length ?? 0) > 0 && (
        <div className="bg-white rounded-2xl border p-5 mt-4">
          <h3 className="font-bold text-slate-700 mb-3">📅 일별 누적 기록 ({dailyHistory!.length}일)</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {[...dailyHistory!].reverse().map((d) => (
              <div key={d.date} className="text-sm border-b border-slate-100 pb-2 last:border-0">
                <div className="flex justify-between gap-2">
                  <span className="font-semibold text-indigo-700">{d.date}</span>
                  <span className="text-xs text-slate-400">
                    TG {d.telegramMessages ?? "—"}건
                    {d.gradeCounts?.["SM-S3"] ? ` · S3 ${d.gradeCounts["SM-S3"]}` : ""}
                  </span>
                </div>
                <p className="text-slate-600 mt-0.5 line-clamp-2">{d.headline}</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-2">
            저장 위치: 1_브리핑/일일_스냅샷/ · 수집할 때마다 누적
          </p>
        </div>
      )}

      {meeting?.ready && meeting.content && (
        <div className="bg-white rounded-2xl border border-indigo-100 p-5 mt-4">
          <h3 className="font-bold text-indigo-700 mb-3">⚖️ 오늘 매매 회의 요약</h3>
          <MeetingQuickView content={meeting.content} />
        </div>
      )}
    </div>
  );
}

function MeetingQuickView({ content }: { content: string }) {
  const sections = ["오늘 바로 할 것", "오늘 하지 말 것", "사용자 확인 필요"];
  const items: { title: string; body: string }[] = [];
  for (const sec of sections) {
    const re = new RegExp(`## ${sec}\\n([\\s\\S]*?)(?=\\n## |$)`);
    const m = content.match(re);
    if (m) items.push({ title: sec, body: m[1].trim() });
  }
  return (
    <div className="space-y-3 text-sm">
      {items.map((item) => (
        <div key={item.title}>
          <p className="font-semibold text-slate-600">{item.title}</p>
          <p className="text-slate-700 whitespace-pre-line mt-1">{item.body}</p>
        </div>
      ))}
    </div>
  );
}
