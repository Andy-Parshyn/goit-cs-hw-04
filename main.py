import logging
from time import perf_counter

from common import build_parser, collect_files, print_results
from multiprocessing_search import multiprocessing_search
from threading_search import threading_search


def timed(func, *args):
    start = perf_counter()
    result = func(*args)
    return result, perf_counter() - start


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser("Compare threading and multiprocessing keyword search").parse_args()

    try:
        files = collect_files(args.dir)
    except NotADirectoryError as e:
        raise SystemExit(e)

    if not files:
        raise SystemExit(f"No .txt files in {args.dir}")

    t_res, t_time = timed(threading_search, files, args.keywords, args.workers)
    m_res, m_time = timed(multiprocessing_search, files, args.keywords, args.workers)

    print(f"Files: {len(files)}, workers: {args.workers}, keywords: {args.keywords}\n")
    print_results(t_res)
    print(f"\nthreading:       {t_time:.4f} s")
    print(f"multiprocessing: {m_time:.4f} s")
    print(f"results match:   {t_res == m_res}")
