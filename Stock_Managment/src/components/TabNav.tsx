"use client";

const TABS = [
  { id: "today", label: "오늘 한눈에", icon: "☀️" },
  { id: "signal", label: "소수몽키 신호", icon: "🐵" },
  { id: "asset", label: "자산제곱", icon: "🧠" },
  { id: "meeting", label: "매매 회의", icon: "⚖️" },
  { id: "columns", label: "칼럼", icon: "📚" },
  { id: "portfolio", label: "포트폴리오", icon: "💼" },
] as const;

export type TabId = (typeof TABS)[number]["id"];

interface TabNavProps {
  active: TabId;
  onChange: (id: TabId) => void;
}

export function TabNav({ active, onChange }: TabNavProps) {
  return (
    <nav className="flex flex-wrap gap-2 mb-6">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
            active === tab.id
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-200"
              : "bg-white text-slate-600 border border-slate-200 hover:border-indigo-300"
          }`}
        >
          {tab.icon} {tab.label}
        </button>
      ))}
    </nav>
  );
}
