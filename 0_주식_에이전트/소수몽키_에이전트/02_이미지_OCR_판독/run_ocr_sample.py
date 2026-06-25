#!/usr/bin/env python3
"""Run local OCR on a balanced sample of original Telegram photos."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


STOP_TICKERS = {
    "AI",
    "API",
    "ATH",
    "BPS",
    "CAPEX",
    "CEO",
    "CFO",
    "CPI",
    "EPS",
    "ETF",
    "FED",
    "FOMC",
    "GDP",
    "IPO",
    "IR",
    "LLM",
    "MTD",
    "NASA",
    "NEW",
    "OLD",
    "PCE",
    "PMI",
    "SEC",
    "TOP",
    "USA",
    "USD",
    "WSJ",
    "YOY",
    "YTD",
}

KNOWN_ETFS = {
    "ARKK",
    "BOTZ",
    "BLOK",
    "DIA",
    "DRNZ",
    "ETHA",
    "GLD",
    "HYG",
    "IBIT",
    "IWM",
    "LQD",
    "NLR",
    "QQQ",
    "ROBO",
    "SLV",
    "SMH",
    "SOXX",
    "SPY",
    "TLT",
    "URA",
    "WGMI",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLU",
    "XLV",
    "XLY",
}

KEYWORD_GROUPS = {
    "섹터": [
        "AI",
        "데이터센터",
        "반도체",
        "메모리",
        "우주",
        "드론",
        "방산",
        "원전",
        "전력",
        "에너지",
        "항공",
        "여행",
        "숙박",
        "금융",
        "은행",
        "비트코인",
        "암호화폐",
    ],
    "매크로": [
        "금리",
        "환율",
        "유가",
        "물가",
        "PCE",
        "CPI",
        "인플레이션",
        "고용",
        "채권",
        "달러",
    ],
    "이벤트": [
        "실적",
        "가이던스",
        "목표주가",
        "계약",
        "정책",
        "관세",
        "보고서",
        "승인",
        "상장",
        "구독",
        "인수",
        "합병",
    ],
    "리스크": [
        "적자",
        "고변동",
        "급락",
        "조정",
        "리스크",
        "상하한가",
        "과열",
        "관망",
        "하락",
    ],
}

TICKER_RE = re.compile(r"(?<![A-Z0-9$])\$?([A-Z][A-Z0-9]{0,5}(?:\.[A-Z])?)(?![A-Z0-9])")
PERCENT_RE = re.compile(r"[-+−]?\d+(?:\.\d+)?\s?%")


def load_index(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def choose_dates(records: list[dict[str, object]], from_date: str | None, to_date: str | None) -> list[str]:
    dates = sorted({str(record.get("date")) for record in records if record.get("date")})
    if from_date or to_date:
        start = from_date or dates[0]
        end = to_date or dates[-1]
        return [day for day in dates if start <= day <= end]
    return dates[-3:]


def collect_photos(records: list[dict[str, object]], dates: set[str], export_dir: Path) -> list[dict[str, object]]:
    photos: list[dict[str, object]] = []
    for record in records:
        if record.get("date") not in dates:
            continue
        for href in record.get("photos") or []:
            if "_thumb" in str(href):
                continue
            photos.append(
                {
                    "date": record.get("date", ""),
                    "time": record.get("time", ""),
                    "message_id": record.get("message_id", ""),
                    "html_file": record.get("html_file", ""),
                    "context_text": record.get("text", ""),
                    "photo": href,
                    "photo_path": str(export_dir / str(href)),
                }
            )
    return photos


def balanced_sample(items: list[dict[str, object]], max_images: int) -> list[dict[str, object]]:
    if max_images <= 0 or len(items) <= max_images:
        return items

    by_date: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in items:
        by_date[str(item["date"])].append(item)

    dates = sorted(by_date)
    base = max_images // len(dates)
    remainder = max_images % len(dates)
    selected: list[dict[str, object]] = []
    seen: set[str] = set()

    for index, day in enumerate(dates):
        quota = base + (1 if index < remainder else 0)
        quota = max(1, quota)
        for item in even_sample(by_date[day], quota):
            key = str(item["photo"])
            if key not in seen:
                selected.append(item)
                seen.add(key)

    if len(selected) > max_images:
        return selected[:max_images]
    return selected


def even_sample(items: list[dict[str, object]], quota: int) -> list[dict[str, object]]:
    if quota <= 0:
        return []
    if len(items) <= quota:
        return items
    if quota == 1:
        return [items[0]]
    indexes = [round(i * (len(items) - 1) / (quota - 1)) for i in range(quota)]
    result: list[dict[str, object]] = []
    seen: set[int] = set()
    for index in indexes:
        if index not in seen:
            result.append(items[index])
            seen.add(index)
    return result


def run_tesseract(
    image_path: Path,
    tesseract_bin: str,
    lang: str,
    psm: str,
    timeout: int,
) -> tuple[str, str]:
    if not image_path.exists():
        return "", f"missing image: {image_path}"
    command = [tesseract_bin, str(image_path), "stdout", "-l", lang, "--psm", psm]
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return "", str(exc)
    if completed.returncode != 0:
        return completed.stdout.strip(), completed.stderr.strip()
    return completed.stdout.strip(), ""


def extract_features(ocr_text: str, context_text: str) -> dict[str, object]:
    source = f"{context_text}\n{ocr_text}"
    tickers = []
    for match in TICKER_RE.finditer(source):
        ticker = match.group(1).strip("$")
        if ticker in STOP_TICKERS:
            continue
        if len(ticker) == 1 and f"${ticker}" not in source:
            continue
        if ticker not in tickers:
            tickers.append(ticker)

    etfs = [ticker for ticker in tickers if ticker in KNOWN_ETFS]
    percentages = []
    for match in PERCENT_RE.finditer(source):
        value = match.group(0).replace("−", "-").replace(" ", "")
        if value not in percentages:
            percentages.append(value)

    keywords: dict[str, list[str]] = {}
    for group, values in KEYWORD_GROUPS.items():
        found = [value for value in values if value.lower() in source.lower()]
        if found:
            keywords[group] = found

    return {
        "tickers": tickers[:20],
        "etfs": etfs[:10],
        "percentages": percentages[:20],
        "keywords": keywords,
        "image_type": guess_image_type(ocr_text, tickers, percentages),
    }


def guess_image_type(ocr_text: str, tickers: list[str], percentages: list[str]) -> str:
    lines = [line for line in ocr_text.splitlines() if line.strip()]
    if len(percentages) >= 8 and len(tickers) >= 5:
        return "히트맵/수익률표 후보"
    if len(lines) >= 8 or len(percentages) >= 3:
        return "표/리스트 후보"
    if len(ocr_text.strip()) < 30:
        return "판독곤란"
    return "단일 캡처 후보"


def write_jsonl(records: Iterable[dict[str, object]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_markdown(
    records: list[dict[str, object]],
    total_candidates: int,
    dates: list[str],
    lang: str,
    psm: str,
    path: Path,
) -> None:
    type_counts = Counter(str(record.get("image_type", "")) for record in records)
    lines = [
        f"# OCR 샘플 {dates[0]} ~ {dates[-1]}",
        "",
        f"- 생성 기준: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- OCR 설정: `tesseract -l {lang} --psm {psm}`",
        f"- 후보 원본 사진: {total_candidates:,}",
        f"- OCR 샘플: {len(records):,}",
        "- 썸네일 제외: `_thumb` 파일 미포함",
        "",
        "## 분류 집계",
        "",
        "| 분류 | 수 |",
        "|------|---:|",
    ]
    for image_type, count in type_counts.most_common():
        lines.append(f"| {image_type} | {count} |")

    lines.extend(
        [
            "",
            "## 샘플 상세",
            "",
            "| 날짜 | 시간 | 메시지 | 이미지 | 분류 | 티커/ETF | 퍼센트 | 키워드 |",
            "|------|------|--------|--------|------|----------|--------|--------|",
        ]
    )
    for record in records:
        tickers = ", ".join(record.get("tickers") or [])
        percentages = ", ".join(record.get("percentages") or [])
        keyword_text = "; ".join(
            f"{group}: {', '.join(values)}"
            for group, values in (record.get("keywords") or {}).items()
        )
        lines.append(
            "| {date} | {time} | {message_id} | {image} | {image_type} | {tickers} | {percentages} | {keywords} |".format(
                date=record.get("date", ""),
                time=record.get("time", ""),
                message_id=record.get("message_id", ""),
                image=Path(str(record.get("photo", ""))).name,
                image_type=record.get("image_type", ""),
                tickers=_markdown_cell(tickers),
                percentages=_markdown_cell(percentages),
                keywords=_markdown_cell(keyword_text),
            )
        )

    for index, record in enumerate(records, start=1):
        lines.extend(
            [
                "",
                f"## OCR 원문 샘플 {index}: {Path(str(record.get('photo', ''))).name}",
                "",
                f"- 메시지: {record.get('message_id', '')} / {record.get('date', '')} {record.get('time', '')}",
                f"- 이미지: `{record.get('photo', '')}`",
                f"- 문맥: {_snippet(str(record.get('context_text') or ''), 220)}",
                "",
                "```text",
                _snippet(str(record.get("ocr_text") or record.get("ocr_error") or ""), 800),
                "```",
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _snippet(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _markdown_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " / ")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--export-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--max-images", type=int, default=12)
    parser.add_argument("--tesseract", default="tesseract")
    parser.add_argument("--lang", default="kor+eng")
    parser.add_argument("--psm", default="6")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    index_records = load_index(args.index)
    dates = choose_dates(index_records, args.from_date, args.to_date)
    candidates = collect_photos(index_records, set(dates), args.export_dir)
    sample = balanced_sample(candidates, args.max_images)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    ocr_records: list[dict[str, object]] = []
    for item in sample:
        image_path = Path(str(item["photo_path"]))
        ocr_text, ocr_error = run_tesseract(
            image_path=image_path,
            tesseract_bin=args.tesseract,
            lang=args.lang,
            psm=args.psm,
            timeout=args.timeout,
        )
        features = extract_features(ocr_text, str(item.get("context_text") or ""))
        ocr_records.append({**item, **features, "ocr_text": ocr_text, "ocr_error": ocr_error})

    suffix = f"{dates[0]}_{dates[-1]}"
    write_jsonl(ocr_records, args.output_dir / f"OCR_샘플_{suffix}.jsonl")
    write_markdown(
        ocr_records,
        total_candidates=len(candidates),
        dates=dates,
        lang=args.lang,
        psm=args.psm,
        path=args.output_dir / f"OCR_샘플_{suffix}.md",
    )

    print(f"candidate_photos={len(candidates)}")
    print(f"ocr_sample={len(ocr_records)}")
    print(f"dates={','.join(dates)}")
    errors = sum(1 for record in ocr_records if record.get("ocr_error"))
    print(f"ocr_errors={errors}")


if __name__ == "__main__":
    main()
