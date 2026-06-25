#!/usr/bin/env python3
"""Build an index from a Telegram Desktop HTML export."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


DATE_TITLE_RE = re.compile(
    r"(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4}) "
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) "
    r"(?P<tz>UTC[+-]\d{2}:\d{2})"
)


@dataclass
class RawMessage:
    html_file: str
    message_id: str
    classes: list[str]
    datetime_title: str = ""
    text: str = ""
    photos: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)

    @property
    def is_service(self) -> bool:
        return "service" in self.classes


class TelegramExportParser(HTMLParser):
    """Small HTMLParser tailored to Telegram Desktop export pages."""

    def __init__(self, html_file: str) -> None:
        super().__init__(convert_charrefs=True)
        self.html_file = html_file
        self.messages: list[RawMessage] = []
        self.current: RawMessage | None = None
        self.div_stack: list[list[str]] = []
        self.text_depth: int | None = None
        self.text_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}

        if tag == "div":
            classes = _class_tokens(attr.get("class", ""))
            if self.current is None and "message" in classes:
                self.current = RawMessage(
                    html_file=self.html_file,
                    message_id=attr.get("id", ""),
                    classes=classes,
                )
                self.div_stack = [classes]
                return

            if self.current is not None:
                self.div_stack.append(classes)
                if "date" in classes and "details" in classes and attr.get("title"):
                    self.current.datetime_title = attr["title"]
                if "text" in classes:
                    self.text_depth = len(self.div_stack)
                    self.text_buffer = []
                return

        if self.current is None:
            return

        if tag == "a":
            href = attr.get("href", "")
            if href.startswith("photos/") and "_thumb" not in href:
                _append_unique(self.current.photos, href)
            elif href.startswith("files/"):
                _append_unique(self.current.files, href)
            return

        if tag == "br" and self.text_depth is not None:
            self.text_buffer.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag != "div" or self.current is None:
            return

        if self.text_depth is not None and len(self.div_stack) == self.text_depth:
            self.current.text = _normalize_text("".join(self.text_buffer))
            self.text_depth = None
            self.text_buffer = []

        if self.div_stack:
            self.div_stack.pop()

        if not self.div_stack:
            self.messages.append(self.current)
            self.current = None

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.text_depth is not None:
            self.text_buffer.append(data)


def _class_tokens(value: str) -> list[str]:
    return [token for token in value.split() if token]


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    lines = [line.strip() for line in text.splitlines()]
    cleaned: list[str] = []
    blank = False
    for line in lines:
        if not line:
            if cleaned and not blank:
                cleaned.append("")
            blank = True
            continue
        cleaned.append(re.sub(r"[ \t]+", " ", line))
        blank = False
    return "\n".join(cleaned).strip()


def _parse_datetime(title: str) -> tuple[str, str, str, str]:
    match = DATE_TITLE_RE.search(title)
    if not match:
        return "", "", "", ""
    value = datetime.strptime(
        f"{match.group('year')}-{match.group('month')}-{match.group('day')} "
        f"{match.group('hour')}:{match.group('minute')}:{match.group('second')}",
        "%Y-%m-%d %H:%M:%S",
    )
    return value.date().isoformat(), value.time().isoformat(), value.isoformat(), match.group("tz")


def _html_sort_key(path: Path) -> tuple[int, str]:
    if path.name == "messages.html":
        return (1, path.name)
    match = re.fullmatch(r"messages(\d+)\.html", path.name)
    if match:
        return (int(match.group(1)), path.name)
    return (999, path.name)


def parse_export(export_dir: Path) -> tuple[list[dict[str, object]], Counter[str]]:
    html_files = sorted(export_dir.glob("messages*.html"), key=_html_sort_key)
    if not html_files:
        raise FileNotFoundError(f"No messages*.html files found in {export_dir}")

    records: list[dict[str, object]] = []
    counters: Counter[str] = Counter()

    for html_file in html_files:
        parser = TelegramExportParser(html_file.name)
        parser.feed(html_file.read_text(encoding="utf-8"))
        parser.close()
        counters["message_divs"] += len(parser.messages)

        for raw in parser.messages:
            if raw.is_service:
                counters["service_messages"] += 1
                continue
            counters["content_messages"] += 1

            day, time_value, iso_dt, timezone = _parse_datetime(raw.datetime_title)
            if not day:
                counters["undated_content_messages"] += 1

            records.append(
                {
                    "date": day,
                    "time": time_value,
                    "datetime": iso_dt,
                    "timezone": timezone,
                    "message_id": raw.message_id,
                    "html_file": raw.html_file,
                    "text": raw.text,
                    "has_text": bool(raw.text),
                    "photos": raw.photos,
                    "photo_count": len(raw.photos),
                    "files": raw.files,
                    "file_count": len(raw.files),
                }
            )

    return records, counters


def summarize_by_date(records: Iterable[dict[str, object]]) -> dict[str, Counter[str]]:
    summary: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        day = str(record.get("date") or "undated")
        photos = list(record.get("photos") or [])
        files = list(record.get("files") or [])
        text = str(record.get("text") or "")
        summary[day]["messages"] += 1
        summary[day]["text_messages"] += int(bool(text))
        summary[day]["photo_messages"] += int(bool(photos))
        summary[day]["photo_links"] += len(photos)
        summary[day]["file_messages"] += int(bool(files))
        summary[day]["file_links"] += len(files)
    return dict(sorted(summary.items()))


def choose_recent_dates(
    records: list[dict[str, object]], from_date: str | None, to_date: str | None
) -> list[str]:
    dates = sorted({str(record["date"]) for record in records if record.get("date")})
    if from_date or to_date:
        start = from_date or dates[0]
        end = to_date or dates[-1]
        return [day for day in dates if start <= day <= end]
    return dates[-3:]


def write_csv(records: list[dict[str, object]], path: Path) -> None:
    fields = [
        "date",
        "time",
        "datetime",
        "timezone",
        "message_id",
        "html_file",
        "has_text",
        "photo_count",
        "file_count",
        "photos",
        "files",
        "text",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["photos"] = "; ".join(record.get("photos") or [])
            row["files"] = "; ".join(record.get("files") or [])
            writer.writerow({field: row.get(field, "") for field in fields})


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_summary_csv(summary: dict[str, Counter[str]], path: Path) -> None:
    fields = [
        "date",
        "messages",
        "text_messages",
        "photo_messages",
        "photo_links",
        "file_messages",
        "file_links",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for day, counts in summary.items():
            writer.writerow({"date": day, **{field: counts.get(field, 0) for field in fields[1:]}})


def write_recent_markdown(
    records: list[dict[str, object]],
    summary: dict[str, Counter[str]],
    counters: Counter[str],
    recent_dates: list[str],
    path: Path,
) -> None:
    dated_records = [record for record in records if record.get("date")]
    date_range = ""
    if dated_records:
        date_range = f"{dated_records[0]['date']} ~ {dated_records[-1]['date']}"

    lines: list[str] = [
        "# 소수몽키 최근 3일 원천 인덱스",
        "",
        f"- 생성 기준: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 전체 날짜 범위: {date_range}",
        f"- 메시지 div: {counters.get('message_divs', 0):,}",
        f"- 일반 메시지: {counters.get('content_messages', 0):,}",
        f"- 서비스 메시지: {counters.get('service_messages', 0):,}",
        "",
        "## 최근 3일 집계",
        "",
        "| 날짜 | 메시지 | 텍스트 | 사진 메시지 | 원본 사진 링크 | 파일 메시지 | 파일 링크 |",
        "|------|-------:|-------:|------------:|---------------:|------------:|----------:|",
    ]

    for day in recent_dates:
        counts = summary.get(day, Counter())
        lines.append(
            "| {day} | {messages:,} | {text_messages:,} | {photo_messages:,} | "
            "{photo_links:,} | {file_messages:,} | {file_links:,} |".format(
                day=day,
                messages=counts.get("messages", 0),
                text_messages=counts.get("text_messages", 0),
                photo_messages=counts.get("photo_messages", 0),
                photo_links=counts.get("photo_links", 0),
                file_messages=counts.get("file_messages", 0),
                file_links=counts.get("file_links", 0),
            )
        )

    selected = [record for record in records if record.get("date") in set(recent_dates)]
    for day in recent_dates:
        day_records = [record for record in selected if record.get("date") == day]
        lines.extend(
            [
                "",
                f"## {day}",
                "",
                "| 시간 | 메시지 ID | 사진 | 파일 | 요약 |",
                "|------|-----------|-----:|-----:|------|",
            ]
        )
        for record in day_records:
            text = _markdown_cell(_snippet(str(record.get("text") or ""), 160))
            if not text:
                text = _asset_summary(record)
            lines.append(
                "| {time} | {message_id} | {photo_count} | {file_count} | {text} |".format(
                    time=record.get("time", ""),
                    message_id=record.get("message_id", ""),
                    photo_count=record.get("photo_count", 0),
                    file_count=record.get("file_count", 0),
                    text=text,
                )
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _asset_summary(record: dict[str, object]) -> str:
    photos = list(record.get("photos") or [])
    files = list(record.get("files") or [])
    parts: list[str] = []
    if photos:
        parts.append(f"사진: {Path(photos[0]).name}" + (f" 외 {len(photos) - 1}" if len(photos) > 1 else ""))
    if files:
        parts.append(f"파일: {Path(files[0]).name}" + (f" 외 {len(files) - 1}" if len(files) > 1 else ""))
    return _markdown_cell(" / ".join(parts))


def _snippet(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _markdown_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " / ")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    args = parser.parse_args()

    records, counters = parse_export(args.export_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = summarize_by_date(records)
    recent_dates = choose_recent_dates(records, args.from_date, args.to_date)

    write_csv(records, args.output_dir / "소수몽키_원천인덱스_전체.csv")
    write_jsonl(records, args.output_dir / "소수몽키_원천인덱스_전체.jsonl")
    write_summary_csv(summary, args.output_dir / "소수몽키_일자별_집계.csv")
    write_recent_markdown(
        records,
        summary,
        counters,
        recent_dates,
        args.output_dir / "소수몽키_최근3일_인덱스.md",
    )

    dated = [record for record in records if record.get("date")]
    first_day = dated[0]["date"] if dated else ""
    last_day = dated[-1]["date"] if dated else ""
    photo_links = sum(int(record.get("photo_count", 0)) for record in records)
    file_links = sum(int(record.get("file_count", 0)) for record in records)

    print(f"indexed_messages={len(records)}")
    print(f"date_range={first_day}..{last_day}")
    print(f"photo_links={photo_links}")
    print(f"file_links={file_links}")
    print(f"recent_dates={','.join(recent_dates)}")


if __name__ == "__main__":
    main()
