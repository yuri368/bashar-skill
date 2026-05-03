#!/usr/bin/env python3
"""Build a precomputed JSONL search index for the Bashar source library."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


TEXT_SUFFIXES = {".md", ".txt"}


def load_articles(sources_dir: Path) -> list[dict]:
    meta_path = sources_dir / "_meta" / "articles.jsonl"
    articles: list[dict] = []
    with meta_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                articles.append(json.loads(line))
    return articles


def read_body(path: Path, max_bytes: int) -> tuple[str, bool, int]:
    if path.suffix.lower() not in TEXT_SUFFIXES or not path.exists():
        return "", False, 0

    try:
        size_bytes = path.stat().st_size
    except OSError:
        return "", False, 0

    if max_bytes >= 0 and size_bytes > max_bytes:
        return "", False, size_bytes

    try:
        return path.read_text(encoding="utf-8", errors="ignore"), True, size_bytes
    except OSError:
        return "", False, size_bytes


def build_record(article: dict, sources_dir: Path, max_bytes: int, indexed_at: str) -> dict:
    source_path = sources_dir / article["path"]
    body, body_indexed, size_bytes = read_body(source_path, max_bytes)
    metadata_text = " ".join(
        [
            article.get("title", ""),
            article.get("primary_category", ""),
            " ".join(article.get("tags", [])),
            article.get("source_persona", ""),
            article.get("format", ""),
            article.get("path", ""),
        ]
    )

    return {
        "id": article.get("id", ""),
        "title": article.get("title", ""),
        "path": article.get("path", ""),
        "primary_category": article.get("primary_category", ""),
        "tags": article.get("tags", []),
        "source_persona": article.get("source_persona", ""),
        "format": article.get("format", ""),
        "size_bytes": size_bytes,
        "body_indexed": body_indexed,
        "indexed_at": indexed_at,
        "body": body,
        "search_text": f"{metadata_text}\n{body}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build sources/_meta/search_index.jsonl.")
    parser.add_argument(
        "--sources-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "sources",
        help="Path to the sources directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSONL path. Defaults to sources/_meta/search_index.jsonl.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=1_000_000,
        help="Skip body text files larger than this; use -1 for no limit.",
    )
    args = parser.parse_args()

    output = args.output or args.sources_dir / "_meta" / "search_index.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)

    indexed_at = datetime.now(timezone.utc).isoformat()
    articles = load_articles(args.sources_dir)
    indexed_bodies = 0

    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for article in articles:
            record = build_record(article, args.sources_dir, args.max_bytes, indexed_at)
            if record["body_indexed"]:
                indexed_bodies += 1
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"Wrote {len(articles)} record(s) to {output}.")
    print(f"Indexed {indexed_bodies} body file(s); max_bytes={args.max_bytes}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

