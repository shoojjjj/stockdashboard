import type { BriefingSlot } from "@/lib/types";

function SimpleMarkdown({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="md-content text-sm">
      {lines.map((line, i) => {
        if (line.startsWith("# "))
          return (
            <h1 key={i}>{line.slice(2)}</h1>
          );
        if (line.startsWith("## "))
          return (
            <h2 key={i}>{line.slice(3)}</h2>
          );
        if (line.startsWith("### "))
          return (
            <h3 key={i}>{line.slice(4)}</h3>
          );
        if (line.startsWith("- "))
          return (
            <li key={i}>{line.slice(2)}</li>
          );
        if (line.startsWith("> "))
          return (
            <blockquote key={i}>{line.slice(2)}</blockquote>
          );
        if (line.trim() === "") return <br key={i} />;
        return (
          <p key={i}>{line}</p>
        );
      })}
    </div>
  );
}

interface BriefingTabProps {
  slot: BriefingSlot;
  title: string;
  emoji: string;
  setupHint?: string;
}

export function BriefingTab({ slot, title, emoji, setupHint }: BriefingTabProps) {
  if (!slot.ready || !slot.content) {
    return (
      <div className="bg-slate-50 border border-dashed border-slate-300 rounded-2xl p-8 text-center">
        <div className="text-4xl mb-3">{emoji}</div>
        <h2 className="text-lg font-bold text-slate-700 mb-2">{title}</h2>
        <p className="text-slate-500 mb-4">{slot.placeholder}</p>
        <div className="bg-white rounded-xl border p-4 text-left text-sm text-slate-600 max-w-lg mx-auto">
          <p className="font-semibold mb-2">설정 방법</p>
          <p>{setupHint || slot.placeholder}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border p-6">
      <h2 className="text-lg font-bold mb-4">
        {emoji} {title}
      </h2>
      <SimpleMarkdown content={slot.content} />
    </div>
  );
}
