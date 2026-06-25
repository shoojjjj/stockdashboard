import type { BriefingSlot, ContentSlot } from "@/lib/types";
import { BriefingTab } from "./BriefingTab";

interface PortfolioTabProps {
  portfolio: BriefingSlot;
  rebalance: ContentSlot;
}

export function PortfolioTab({ portfolio, rebalance }: PortfolioTabProps) {
  return (
    <div className="space-y-6">
      <BriefingTab
        slot={portfolio}
        title="실제 보유현황"
        emoji="💼"
        setupHint="1_브리핑/포트폴리오_브리핑/00_현황/실제_보유현황.md 에 계좌 숫자를 입력하세요."
      />
      {rebalance.ready && rebalance.content && (
        <BriefingTab
          slot={{ ready: true, content: rebalance.content }}
          title="목표 및 리밸런싱"
          emoji="🎯"
          setupHint=""
        />
      )}
    </div>
  );
}
