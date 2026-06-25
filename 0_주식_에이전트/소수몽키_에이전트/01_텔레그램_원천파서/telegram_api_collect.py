#!/usr/bin/env python3
"""Collect Telegram channel messages through the Telegram API."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date, datetime, time
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"env file not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def env_first(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def parse_local_date(value: str | None, tz: ZoneInfo, end_of_day: bool = False) -> datetime | None:
    if not value:
        return None
    day = date.fromisoformat(value)
    local_time = time.max if end_of_day else time.min
    return datetime.combine(day, local_time, tzinfo=tz)


def local_parts(value: datetime, tz: ZoneInfo) -> tuple[str, str, str, str]:
    local = value.astimezone(tz)
    offset = local.strftime("%z")
    timezone = f"UTC{offset[:3]}:{offset[3:]}" if offset else local.tzname() or ""
    return local.date().isoformat(), local.time().replace(microsecond=0).isoformat(), local.isoformat(), timezone


def normalize_text(text: str) -> str:
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


def summarize_by_date(records: Iterable[dict[str, object]]) -> dict[str, Counter[str]]:
    summary: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        day = str(record.get("date") or "undated")
        photos = list(record.get("photos") or [])
        files = list(record.get("files") or [])
        photo_count = int(record.get("photo_count") or len(photos))
        file_count = int(record.get("file_count") or len(files))
        text = str(record.get("text") or "")
        summary[day]["messages"] += 1
        summary[day]["text_messages"] += int(bool(text))
        summary[day]["photo_messages"] += int(photo_count > 0)
        summary[day]["photo_links"] += photo_count
        summary[day]["file_messages"] += int(file_count > 0)
        summary[day]["file_links"] += file_count
    return dict(sorted(summary.items()))


def choose_recent_dates(
    records: list[dict[str, object]], from_date: str | None, to_date: str | None
) -> list[str]:
    dates = sorted({str(record["date"]) for record in records if record.get("date")})
    if not dates:
        return []
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
        "source",
        "api_message_id",
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


def write_jsonl(records: Iterable[dict[str, object]], path: Path) -> None:
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

    lines = [
        "# 소수몽키 최근 3일 원천 인덱스",
        "",
        f"- 생성 기준: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 수집 방식: Telegram API",
        f"- 전체 날짜 범위: {date_range}",
        f"- 일반 메시지: {counters.get('content_messages', 0):,}",
        f"- 서비스/액션 메시지: {counters.get('service_messages', 0):,}",
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
            text = markdown_cell(snippet(str(record.get("text") or ""), 160))
            if not text:
                text = asset_summary(record)
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


def asset_summary(record: dict[str, object]) -> str:
    photos = list(record.get("photos") or [])
    files = list(record.get("files") or [])
    photo_count = int(record.get("photo_count") or len(photos))
    file_count = int(record.get("file_count") or len(files))
    parts: list[str] = []
    if photos:
        parts.append(f"사진: {Path(photos[0]).name}" + (f" 외 {len(photos) - 1}" if len(photos) > 1 else ""))
    elif photo_count:
        parts.append(f"사진: API 미다운로드 {photo_count}")
    if files:
        parts.append(f"파일: {Path(files[0]).name}" + (f" 외 {len(files) - 1}" if len(files) > 1 else ""))
    elif file_count:
        parts.append(f"파일: API 미다운로드 {file_count}")
    return markdown_cell(" / ".join(parts))


def snippet(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def markdown_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " / ")


def import_telegram_client():
    try:
        from telethon import TelegramClient
    except ImportError as exc:
        raise SystemExit(
            "telethon is not installed. Install it with: "
            "python3 -m pip install -r 0_주식_에이전트/소수몽키_에이전트/requirements.txt"
        ) from exc
    return TelegramClient


def full_peer_id(entity: object) -> str:
    entity_id = getattr(entity, "id", "")
    if not entity_id:
        return ""
    if getattr(entity, "broadcast", False) or getattr(entity, "megagroup", False):
        return f"-100{entity_id}"
    return str(entity_id)


async def list_dialogs(args: argparse.Namespace) -> None:
    TelegramClient = import_telegram_client()
    client = TelegramClient(args.session, args.api_id, args.api_hash)
    async with client:
        print("kind\tpeer_id\tusername\ttitle")
        async for dialog in client.iter_dialogs(limit=args.dialog_limit):
            entity = dialog.entity
            title = getattr(dialog, "name", "") or getattr(entity, "title", "") or ""
            username = getattr(entity, "username", "") or ""
            if getattr(dialog, "is_channel", False):
                kind = "channel"
            elif getattr(dialog, "is_group", False):
                kind = "group"
            elif getattr(dialog, "is_user", False):
                kind = "user"
            else:
                kind = "unknown"
            print(f"{kind}\t{full_peer_id(entity)}\t{username}\t{title}")


async def resolve_entity(client: object, args: argparse.Namespace) -> object:
    if args.entity_title:
        needle = args.entity_title.casefold()
        matches: list[object] = []
        async for dialog in client.iter_dialogs(limit=args.dialog_limit):
            title = getattr(dialog, "name", "") or getattr(dialog.entity, "title", "") or ""
            if needle in title.casefold():
                matches.append(dialog)

        if not matches:
            raise SystemExit(f"no Telegram dialog title matched: {args.entity_title}")
        if len(matches) > 1:
            print("multiple dialog title matches:")
            for dialog in matches:
                entity = dialog.entity
                title = getattr(dialog, "name", "") or getattr(entity, "title", "") or ""
                username = getattr(entity, "username", "") or ""
                print(f"- peer_id={full_peer_id(entity)} username={username} title={title}")
            raise SystemExit("set TG_ENTITY to one peer_id above, or use a more specific TG_ENTITY_TITLE")
        return matches[0].entity

    return await client.get_entity(args.entity)


async def collect_messages(args: argparse.Namespace) -> tuple[list[dict[str, object]], Counter[str]]:
    TelegramClient = import_telegram_client()
    tz = ZoneInfo(args.timezone)
    start = parse_local_date(args.from_date, tz, end_of_day=False)
    end = parse_local_date(args.to_date, tz, end_of_day=True)
    media_root = args.collection_dir
    photos_dir = media_root / "photos"
    files_dir = media_root / "files"

    if args.download_media:
        photos_dir.mkdir(parents=True, exist_ok=True)
        files_dir.mkdir(parents=True, exist_ok=True)

    counters: Counter[str] = Counter()
    records: list[dict[str, object]] = []

    client = TelegramClient(args.session, args.api_id, args.api_hash)
    async with client:
        entity = await resolve_entity(client, args)
        async for message in client.iter_messages(entity, limit=args.limit, reverse=args.reverse):
            counters["api_messages_seen"] += 1
            message_date = getattr(message, "date", None)
            if not message_date:
                counters["undated_messages"] += 1
                continue
            if getattr(message, "action", None):
                counters["service_messages"] += 1
                continue
            if start and message_date.astimezone(tz) < start:
                continue
            if end and message_date.astimezone(tz) > end:
                continue

            day, time_value, iso_dt, timezone = local_parts(message_date, tz)
            text = normalize_text(getattr(message, "message", "") or "")
            photos: list[str] = []
            files: list[str] = []
            has_photo = bool(getattr(message, "photo", None))
            has_file = bool(getattr(message, "document", None)) and not has_photo

            if has_photo:
                counters["photo_messages"] += 1
                if args.download_media:
                    downloaded = await client.download_media(message, file=str(photos_dir / f"message_{message.id}"))
                    if downloaded:
                        photos.append(str(Path(downloaded).relative_to(media_root)))
            elif has_file:
                counters["file_messages"] += 1
                if args.download_media:
                    downloaded = await client.download_media(message, file=str(files_dir / f"message_{message.id}"))
                    if downloaded:
                        files.append(str(Path(downloaded).relative_to(media_root)))

            counters["content_messages"] += 1
            records.append(
                {
                    "date": day,
                    "time": time_value,
                    "datetime": iso_dt,
                    "timezone": timezone,
                    "message_id": f"message{message.id}",
                    "html_file": "telegram_api",
                    "text": text,
                    "has_text": bool(text),
                    "photos": photos,
                    "photo_count": len(photos) or int(has_photo),
                    "files": files,
                    "file_count": len(files) or int(has_file),
                    "api_message_id": message.id,
                    "source": "telegram_api",
                }
            )

    records.sort(key=lambda record: str(record.get("datetime") or ""))
    return records, counters


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, help="Optional KEY=VALUE file for Telegram credentials.")
    parser.add_argument("--api-id", type=int, default=0, help="Telegram API ID. Env: TG_API_ID or TELEGRAM_API_ID.")
    parser.add_argument("--api-hash", default="", help="Telegram API hash. Env: TG_API_HASH or TELEGRAM_API_HASH.")
    parser.add_argument(
        "--entity",
        default="",
        help="Channel username, invite link, or peer id. Env: TG_ENTITY or TELEGRAM_ENTITY.",
    )
    parser.add_argument(
        "--entity-title",
        default="",
        help="Find a joined private dialog by title substring. Env: TG_ENTITY_TITLE or TELEGRAM_ENTITY_TITLE.",
    )
    parser.add_argument(
        "--session",
        default="0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/API_수집/session/sosumonkey",
        help="Telethon session path. This stores login credentials.",
    )
    parser.add_argument(
        "--collection-dir",
        type=Path,
        default=Path("0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/API_수집"),
        help="Root for downloaded API media. Use this as OCR --export-dir.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("0_주식_에이전트/소수몽키_에이전트/01_텔레그램_원천파서/API_수집/인덱스"),
        help="Directory for CSV/JSONL/Markdown index outputs.",
    )
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--dialog-limit", type=int, default=200)
    parser.add_argument("--timezone", default="Asia/Seoul")
    parser.add_argument("--download-media", action="store_true")
    parser.add_argument("--list-dialogs", action="store_true", help="List joined dialogs and exit.")
    parser.add_argument("--reverse", action="store_true", help="Ask Telegram for oldest-to-newest order.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.env_file:
        load_env_file(args.env_file)

    args.api_id = args.api_id or int(env_first("TG_API_ID", "TELEGRAM_API_ID") or "0")
    args.api_hash = args.api_hash or env_first("TG_API_HASH", "TELEGRAM_API_HASH")
    args.entity = args.entity or env_first("TG_ENTITY", "TELEGRAM_ENTITY")
    args.entity_title = args.entity_title or env_first("TG_ENTITY_TITLE", "TELEGRAM_ENTITY_TITLE")
    args.session = env_first("TG_SESSION", "TELEGRAM_SESSION") or args.session

    missing = [
        name
        for name, value in [
            ("api_id", args.api_id),
            ("api_hash", args.api_hash),
            ("entity", args.entity or args.entity_title or args.list_dialogs),
        ]
        if not value
    ]
    if missing:
        parser.error("missing required Telegram settings: " + ", ".join(missing))

    Path(args.session).parent.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.collection_dir.mkdir(parents=True, exist_ok=True)

    if args.list_dialogs:
        asyncio.run(list_dialogs(args))
        return

    records, counters = asyncio.run(collect_messages(args))
    summary = summarize_by_date(records)
    recent_dates = choose_recent_dates(records, args.from_date, args.to_date)

    write_csv(records, args.output_dir / "소수몽키_API_원천인덱스.csv")
    write_jsonl(records, args.output_dir / "소수몽키_API_원천인덱스.jsonl")
    write_summary_csv(summary, args.output_dir / "소수몽키_API_일자별_집계.csv")
    write_recent_markdown(
        records,
        summary,
        counters,
        recent_dates,
        args.output_dir / "소수몽키_API_최근3일_인덱스.md",
    )

    first_day = records[0]["date"] if records else ""
    last_day = records[-1]["date"] if records else ""
    photo_links = sum(int(record.get("photo_count", 0)) for record in records)
    file_links = sum(int(record.get("file_count", 0)) for record in records)

    print(f"indexed_messages={len(records)}")
    print(f"date_range={first_day}..{last_day}")
    print(f"photo_links={photo_links}")
    print(f"file_links={file_links}")
    print(f"recent_dates={','.join(recent_dates)}")
    print(f"collection_dir={args.collection_dir}")
    print(f"output_dir={args.output_dir}")


if __name__ == "__main__":
    main()
