import logging
from multiprocessing import Process, Queue
from pathlib import Path
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


def worker(files: list[Path], keywords: list[str], queue: Queue) -> None:
    try:
        queue.put(search_files(files, keywords))
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        queue.put({})


def multiprocessing_search(files: list[Path], keywords: list[str], workers: int = 4) -> dict[str, list[str]]:
    queue: Queue = Queue()
    processes = [
        Process(target=worker, args=(chunk, keywords, queue))
        for chunk in split_files(files, workers)
    ]
    for p in processes:
        p.start()

    # drain the queue before join(), otherwise a child with a big result
    # blocks on the pipe and join() never returns
    results: dict[str, list[str]] = {kw: [] for kw in keywords}
    for _ in processes:
        merge_results(results, queue.get())

    for p in processes:
        p.join()
    return sort_results(results)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser("Keyword search with multiprocessing").parse_args()

    try:
        files = collect_files(args.dir)
    except NotADirectoryError as e:
        raise SystemExit(e)

    start = perf_counter()
    results = multiprocessing_search(files, args.keywords, args.workers)
    elapsed = perf_counter() - start

    print_results(results)
    print(f"\nmultiprocessing: {len(files)} files, {args.workers} workers, {elapsed:.4f} s")
