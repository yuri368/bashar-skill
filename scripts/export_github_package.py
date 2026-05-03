#!/usr/bin/env python3
"""Export a GitHub-ready Bashar-only skill package."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path


ROOT_FILES = [
    "SKILL.md",
    "巴夏词汇定义.md",
    "巴夏主题索引.md",
    "迭代历史.md",
]


def load_articles(source_root: Path) -> list[dict]:
    meta_path = source_root / "sources" / "_meta" / "articles.jsonl"
    articles: list[dict] = []
    with meta_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                articles.append(json.loads(line))
    return articles


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree(source: Path, target: Path) -> None:
    if not source.exists():
        return
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_indexes(target_root: Path, articles: list[dict]) -> None:
    index_root = target_root / "sources" / "_indexes"
    by_tag_root = index_root / "by-tag"
    by_tag_root.mkdir(parents=True, exist_ok=True)

    by_category: dict[str, list[dict]] = defaultdict(list)
    by_tag: dict[str, list[dict]] = defaultdict(list)
    for article in articles:
        by_category[article.get("primary_category", "未分类")].append(article)
        for tag in article.get("tags", []):
            by_tag[tag].append(article)

    category_lines = ["# Categories", ""]
    for category in sorted(by_category):
        category_lines.append(f"## {category}")
        category_lines.append("")
        for article in sorted(by_category[category], key=lambda row: row.get("title", "")):
            category_lines.append(f"- `{article.get('path', '')}` — {article.get('title', '')}")
        category_lines.append("")
    (index_root / "categories.md").write_text("\n".join(category_lines), encoding="utf-8")

    readme = [
        "# Source Indexes",
        "",
        "This directory is generated from the Bashar-only article metadata during export.",
        "",
        "- `categories.md`: sources grouped by primary category.",
        "- `by-tag/`: sources grouped by tag.",
        "",
    ]
    (index_root / "README.md").write_text("\n".join(readme), encoding="utf-8")

    for tag in sorted(by_tag):
        safe_name = tag.replace("/", "_").replace("\\", "_")
        lines = [f"# {tag}", ""]
        for article in sorted(by_tag[tag], key=lambda row: row.get("title", "")):
            lines.append(f"- `{article.get('path', '')}` — {article.get('title', '')}")
        lines.append("")
        (by_tag_root / f"{safe_name}.md").write_text("\n".join(lines), encoding="utf-8")


def write_gitignore(target_root: Path) -> None:
    lines = [
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        ".DS_Store",
        "Thumbs.db",
        "",
    ]
    (target_root / ".gitignore").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a Bashar-only package for GitHub publishing.")
    parser.add_argument(
        "--target",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "bashar-github",
        help="Target directory for the exported package.",
    )
    parser.add_argument(
        "--persona",
        default="Bashar",
        help="source_persona value to include.",
    )
    parser.add_argument("--force", action="store_true", help="Remove the target directory before export.")
    args = parser.parse_args()

    source_root = Path(__file__).resolve().parents[1]
    target_root = args.target.resolve()

    if target_root.exists():
        if not args.force:
            raise SystemExit(f"Target already exists: {target_root}. Use --force to replace it.")
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True)

    articles = load_articles(source_root)
    included = [article for article in articles if article.get("source_persona") == args.persona]
    excluded = [article for article in articles if article.get("source_persona") != args.persona]

    for root_file in ROOT_FILES:
        copy_file(source_root / root_file, target_root / root_file)
    copy_tree(source_root / "agents", target_root / "agents")
    copy_tree(source_root / "scripts", target_root / "scripts")

    meta_root = target_root / "sources" / "_meta"
    write_jsonl(meta_root / "articles.jsonl", included)
    for name in ["tags.yaml", "maintenance.md"]:
        source = source_root / "sources" / "_meta" / name
        if source.exists():
            copy_file(source, meta_root / name)

    for article in included:
        copy_file(source_root / "sources" / article["path"], target_root / "sources" / article["path"])

    write_indexes(target_root, included)
    write_gitignore(target_root)

    print(f"Exported {len(included)} {args.persona} source record(s) to {target_root}.")
    print(f"Excluded {len(excluded)} non-{args.persona} source record(s).")
    print("Run this inside the export directory to rebuild the precomputed index:")
    print("  python scripts/build_search_index.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

