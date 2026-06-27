"use client";

export function MarkdownView({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="md-content text-sm">
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
        if (line.trim() === "") return <br key={i} />;
        return <p key={i}>{line}</p>;
      })}
    </div>
  );
}
