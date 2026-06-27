import type { BriefingSlot } from "@/lib/types";
import { MarkdownView } from "../MarkdownView";

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
      <MarkdownView content={slot.content} />
    </div>
  );
}
