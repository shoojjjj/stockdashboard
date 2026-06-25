import type { Agent } from "@/lib/types";

interface AgentStatusProps {
  agents: Agent[];
}

export function AgentStatus({ agents }: AgentStatusProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {agents.map((a) => (
        <div
          key={a.id}
          className={`rounded-xl p-3 border text-center ${
            a.status === "active"
              ? "bg-white border-emerald-200"
              : "bg-slate-50 border-slate-200 opacity-70"
          }`}
        >
          <div className="text-2xl">{a.emoji}</div>
          <div className="text-sm font-bold mt-1">{a.name}</div>
          <div className="text-xs text-slate-500">{a.role}</div>
          <div
            className={`text-xs mt-1 font-semibold ${
              a.status === "active" ? "text-emerald-600" : "text-amber-600"
            }`}
          >
            {a.status === "active" ? "● 연결됨" : "○ 대기"}
          </div>
        </div>
      ))}
    </div>
  );
}
