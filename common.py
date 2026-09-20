import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def collect_files(directory: str | Path, pattern: str = "*.txt") -> list[Path]:
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"Directory not found: {root}")
    return sorted(p for p in root.rglob(pattern) if p.is_file())


def split_files(files: list[Path], parts: int) -> list[list[Path]]:
    parts = max(1, min(parts, len(files)))
    return [files[i::parts] for i in range(parts)]


def search_in_file(path: Path, keywords: list[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError as e:
        logger.error(f"Cannot read {path}: {e}")
        return found
    for kw in keywords:
        if kw.lower() in text:
            found.setdefault(kw, []).append(str(path))
    return found


def search_files(files: list[Path], keywords: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {kw: [] for kw in keywords}
    for path in files:
        merge_results(result, search_in_file(path, keywords))
    return result


def merge_results(target: dict[str, list[str]], source: dict[str, list[str]]) -> None:
    for kw, paths in source.items():
        target.setdefault(kw, []).extend(paths)


def sort_results(results: dict[str, list[str]]) -> dict[str, list[str]]:
    return {kw: sorted(paths) for kw, paths in results.items()}


def print_results(results: dict[str, list[str]]) -> None:
    for kw, paths in results.items():
        print(f"{kw!r}: {len(paths)} file(s)")
        for p in paths:
            print(f"    {p}")


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("keywords", nargs="+", help="words to search for")
    parser.add_argument("-d", "--dir", default="texts", help="directory with .txt files")
    parser.add_argument("-w", "--workers", type=int, default=4)
    return parser
