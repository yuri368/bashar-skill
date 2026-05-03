#!/usr/bin/env python3
"""Search the bundled Bashar source library.

The script intentionally uses only the Python standard library so the skill stays
portable inside Codex workspaces.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TEXT_SUFFIXES = {".md", ".txt"}
INDEX_NAME = "search_index.jsonl"


def load_articles(sources_dir: Path) -> list[dict]:
    meta_path = sources_dir / "_meta" / "articles.jsonl"
    articles: list[dict] = []
    with meta_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                articles.append(json.loads(line))
    return articles


def load_precomputed_index(sources_dir: Path) -> list[dict]:
    index_path = sources_dir / "_meta" / INDEX_NAME
    records: list[dict] = []
    with index_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def text_for(article: dict, sources_dir: Path, cache: dict[str, str], max_bytes: int) -> str:
    if "body" in article:
        return article.get("body", "")

    path = sources_dir / article["path"]
    key = str(path)
    if key in cache:
        return cache[key]
    if path.suffix.lower() not in TEXT_SUFFIXES or not path.exists():
        cache[key] = ""
        return ""
    if max_bytes >= 0 and path.stat().st_size > max_bytes:
        cache[key] = ""
        return ""
    try:
        cache[key] = path.read_text(encoding="utf-8", errors="ignore")
        return cache[key]
    except OSError:
        cache[key] = ""
        return ""


def contains_all(haystack: str, needles: list[str]) -> bool:
    folded = haystack.casefold()
    return all(needle.casefold() in folded for needle in needles)


def snippet(text: str, terms: list[str], width: int = 110) -> str:
    if not text or not terms:
        return ""

    folded = text.casefold()
    positions = [folded.find(term.casefold()) for term in terms]
    positions = [position for position in positions if position >= 0]
    if not positions:
        return ""

    start = max(min(positions) - width // 2, 0)
    end = min(start + width, len(text))
    sample = " ".join(text[start:end].split())
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{sample}{suffix}"


def score(
    article: dict,
    terms: list[str],
    include_content: bool,
    sources_dir: Path,
    cache: dict[str, str],
    max_bytes: int,
) -> int:
    title = article.get("title", "")
    tags = " ".join(article.get("tags", []))
    category = article.get("primary_category", "")
    path = article.get("path", "")
    persona = article.get("source_persona", "")
    file_format = article.get("format", "")
    fields = f"{title} {tags} {category} {persona} {file_format} {path}"

    result = 0
    folded_title = title.casefold()
    folded_tags = tags.casefold()
    folded_category = category.casefold()
    folded_path = path.casefold()

    for term in terms:
        needle = term.casefold()
        if needle in folded_title:
            result += 8
        if needle in folded_tags:
            result += 5
        if needle in folded_category:
            result += 3
        if needle in folded_path:
            result += 2

    if terms and contains_all(fields, terms):
        result += 5
    if include_content and terms and contains_all(text_for(article, sources_dir, cache, max_bytes), terms):
        result += 1
    return result


def matches(article: dict, args: argparse.Namespace, sources_dir: Path, cache: dict[str, str]) -> bool:
    if args.persona and args.persona != article.get("source_persona", ""):
        return False

    if args.format and args.format != article.get("format", ""):
        return False

    if args.category and args.category not in article.get("primary_category", ""):
        return False

    article_tags = set(article.get("tags", []))
    for tag in args.tag:
        if tag not in article_tags:
            return False

    terms = args.query
    if not terms:
        return True

    fields = " ".join(
        [
            article.get("title", ""),
            article.get("primary_category", ""),
            " ".join(article.get("tags", [])),
            article.get("source_persona", ""),
            article.get("format", ""),
            article.get("path", ""),
        ]
    )
    if contains_all(fields, terms):
        return True
    if args.content and contains_all(text_for(article, sources_dir, cache, args.max_bytes), terms):
        return True
    return False


def format_result(
    article: dict,
    terms: list[str],
    include_content: bool,
    sources_dir: Path,
    cache: dict[str, str],
    max_bytes: int,
) -> str:
    tags = "、".join(article.get("tags", []))
    output = [
        f"- {article.get('title', '(untitled)')}",
        f"  path: sources/{article.get('path', '')}",
        f"  category: {article.get('primary_category', '')}",
        f"  tags: {tags}",
    ]
    if article.get("source_persona") or article.get("format"):
        output.append(f"  persona/format: {article.get('source_persona', '')} / {article.get('format', '')}")
    if include_content:
        sample = snippet(text_for(article, sources_dir, cache, max_bytes), terms)
        if sample:
            output.append(f"  snippet: {sample}")
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Bashar source metadata and text.")
    parser.add_argument("query", nargs="*", help="Terms to search. All terms must match.")
    parser.add_argument("--tag", action="append", default=[], help="Require a tag. Repeatable.")
    parser.add_argument("--persona", default="Bashar", help="Require source_persona; defaults to Bashar. Use empty string to disable.")
    parser.add_argument("--format", help="Require an exact format, such as 文本、问答、视频转录、节选.")
    parser.add_argument("--category", help="Require a primary category substring.")
    parser.add_argument("--content", action="store_true", help="Also scan .txt/.md body text.")
    parser.add_argument("--no-index", action="store_true", help="Ignore sources/_meta/search_index.jsonl and use articles.jsonl.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum results to print.")
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=1_000_000,
        help="Skip body text files larger than this when --content is used; use -1 for no limit.",
    )
    parser.add_argument(
        "--sources-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "sources",
        help="Path to the sources directory.",
    )
    args = parser.parse_args()
    if args.persona == "":
        args.persona = None

    index_path = args.sources_dir / "_meta" / INDEX_NAME
    if index_path.exists() and not args.no_index:
        articles = load_precomputed_index(args.sources_dir)
    else:
        articles = load_articles(args.sources_dir)
    content_cache: dict[str, str] = {}
    filtered = [article for article in articles if matches(article, args, args.sources_dir, content_cache)]
    ranked = sorted(
        filtered,
        key=lambda article: (
            score(article, args.query, args.content, args.sources_dir, content_cache, args.max_bytes),
            article.get("title", ""),
        ),
        reverse=True,
    )

    shown = ranked[: max(args.limit, 0)]
    print(f"Found {len(filtered)} result(s); showing {len(shown)}.")
    for article in shown:
        print(format_result(article, args.query, args.content, args.sources_dir, content_cache, args.max_bytes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
