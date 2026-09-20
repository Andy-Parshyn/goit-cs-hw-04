import logging
from pathlib import Path
from threading import Lock, Thread
from time import perf_counter

from common import (
    build_parser,
    collect_files,
    merge_results,
    print_results,
    search_files,
    sort_results,
    split_files,
)

logger = logging.getLogger(__name__)


def worker(files: list[Path], keywords: list[str], results: dict, lock: Lock) -> None:
    try:
        partial = search_files(files, keywords)
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        return
    with lock:
        merge_results(results, partial)


def threading_search(files: list[Path], keywords: list[str], workers: int = 4) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {kw: [] for kw in keywords}
    lock = Lock()
    threads = [
        Thread(target=worker, args=(chunk, keywords, results, lock))
        for chunk in split_files(files, workers)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return sort_results(results)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser("Keyword search with threading").parse_args()

    try:
        files = collect_files(args.dir)
    except NotADirectoryError as e:
        raise SystemExit(e)

    start = perf_counter()
    results = threading_search(files, args.keywords, args.workers)
    elapsed = perf_counter() - start

    print_results(results)
    print(f"\nthreading: {len(files)} files, {args.workers} workers, {elapsed:.4f} s")
