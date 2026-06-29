"use client";

import { useState } from "react";
import type { DashboardData } from "@/lib/types";
import { TabNav, type TabId } from "./TabNav";
import { TodayTab } from "./tabs/TodayTab";
import { SignalTab } from "./tabs/SignalTab";
import { BriefingTab } from "./tabs/BriefingTab";
import { PortfolioTab } from "./tabs/PortfolioTab";
import { ColumnsTab } from "./tabs/ColumnsTab";
import { MeetingTab } from "./tabs/MeetingTab";

export function Dashboard({ data }: { data: DashboardData }) {
  const [tab, setTab] = useState<TabId>("today");

  return (
    <div>
      <TabNav active={tab} onChange={setTab} />

      {tab === "today" && (
        <TodayTab
          today={data.today}
          agents={data.agents}
          latestDate={data.latestSignalDate}
          generatedAt={data.generatedAt}
          meeting={data.meeting}
          pendingInputs={data.pendingInputs}
          dailyHistory={data.dailyHistory}
        />
      )}
      {tab === "signal" && (
        <SignalTab
          signals={data.signals}
          latestDate={data.latestSignalDate}
          telegramPhotos={data.telegramPhotos}
          telegramPhotoStats={data.telegramPhotoStats}
        />
      )}
      {tab === "portfolio" && (
        <PortfolioTab
          portfolio={data.portfolio}
          rebalance={data.rebalance}
          pendingInputs={data.pendingInputs}
        />
      )}
      {tab === "asset" && (
        <BriefingTab
          slot={data.asset}
          title="자산제곱 실행판"
          emoji="🧠"
          setupHint="아카이브/1_브리핑/자산제곱_브리핑/00_운용판단/이번주_실행판.md 파일을 만들거나 Cursor에서 자산제곱 에이전트를 실행하세요."
        />
      )}
      {tab === "meeting" && <MeetingTab slot={data.meeting} />}
      {tab === "columns" && <ColumnsTab columns={data.columns} />}
    </div>
  );
}
