"use client";

/** 연속 빈 줄·제로폭 문자를 줄여 가독성 개선 */
function compactLines(content: string): string[] {
  const lines = content.replace(/\u200b/g, "").split("\n");
  const out: string[] = [];
  let prevBlank = false;
  for (const line of lines) {
    const blank = !line.trim();
    if (blank) {
      if (!prevBlank) out.push("");
      prevBlank = true;
      continue;
    }
    prevBlank = false;
    out.push(line);
  }
  return out;
}

export function MarkdownView({
  content,
  compact = true,
  reader = false,
}: {
  content: string;
  compact?: boolean;
  /** 칼럼 PC 읽기 — 글씨 약간 축소 */
  reader?: boolean;
}) {
  const lines = compact ? compactLines(content) : content.split("\n");
  const className = [
    "md-content",
    compact ? "md-content-compact" : "",
    reader ? "md-content-reader" : "",
    reader ? "" : "text-sm",
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <div className={className}>
      {lines.map((line, i) => {
        if (line.startsWith("# "))
          return <h1 key={i}>{line.slice(2)}</h1>;
        if (line.startsWith("## "))
          return <h2 key={i}>{line.slice(3)}</h2>;
        if (line.startsWith("### "))
          return <h3 key={i}>{line.slice(4)}</h3>;
        if (line.startsWith("- ") || line.startsWith("* "))
          return <li key={i}>{line.slice(2)}</li>;
        if (line.startsWith("> "))
          return <blockquote key={i}>{line.slice(2)}</blockquote>;
        if (line.trim() === "") return null;
        return <p key={i}>{line}</p>;
      })}
    </div>
  );
}
