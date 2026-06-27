export interface SignalSummary {
  grade: string;
  signal: string;
  tags: string;
  evidence: string;
}

export interface SignalDetail {
  title: string;
  [key: string]: string;
}

export interface SignalBoard {
  date: string;
  file: string;
  meta: Record<string, string>;
  summary: SignalSummary[];
  details: SignalDetail[];
  rebalancing: { target: string; impact: string }[];
  gradeDistribution: { grade: string; count: string; memo: string }[];
}

export interface TodaySummary {
  headline: string;
  bullets: string[];
  action: string;
}

export interface Agent {
  id: string;
  name: string;
  emoji: string;
  role: string;
  status: "active" | "waiting";
}

export interface BriefingSlot {
  ready: boolean;
  content: string | null;
  placeholder?: string;
}

export interface ContentSlot {
  ready: boolean;
  content: string | null;
}

export interface ColumnArticle {
  id: string;
  title: string;
  date?: string;
  dateLabel?: string;
}

export interface ColumnCategory {
  name: string;
  count: number;
  articles: ColumnArticle[];
  /** @deprecated use articles */
  samples?: string[];
}

export interface DailySnapshot {
  date: string;
  headline: string;
  gradeCounts: Record<string, number>;
  telegramMessages?: string;
  savedAt?: string;
}

export interface TelegramPhoto {
  date: string;
  time: string;
  messageId: string;
  caption: string;
  url: string;
}

export interface TelegramPhotoStats {
  downloaded: number;
  pending: number;
  cutoff?: string;
  months?: number;
}

export interface DashboardData {
  generatedAt: string;
  archivePath: string;
  today: TodaySummary;
  latestSignalDate: string | null;
  pendingInputs?: number;
  dailyHistory?: DailySnapshot[];
  signals: SignalBoard[];
  telegramStats: Record<string, string>[];
  telegramPhotos?: TelegramPhoto[];
  telegramPhotoStats?: TelegramPhotoStats;
  columns: ColumnCategory[];
  portfolio: BriefingSlot;
  asset: BriefingSlot;
  meeting: BriefingSlot;
  currentPan: ContentSlot;
  sosumonkeyReport: ContentSlot;
  rebalance: ContentSlot;
  agents: Agent[];
}
