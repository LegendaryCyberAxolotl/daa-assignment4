#!/usr/bin/env python3
"""Compare naive / KMP / exact Rabin-Karp for the "Search comparison" section of ANALYSIS.md.

Usage (from the repository root):
    python tests/student/benchmark_search.py
    python tests/student/benchmark_search.py --sizes 1000,2000,3000 --runs 5

Method (printed into the report as well)
  * Same (text, pattern) pairs for all three algorithms, three increasing sizes, all inside the
    common domain n, m <= 3000. Seeded generators, so the inputs are reproducible.
  * Random and repetitive cases are measured separately.
  * Correctness FIRST: before timing, the three outputs must be identical and equal to an
    independent str.find loop. If not, the script stops without timing anything.
  * Timing scope: only the call algorithms.<name>(request) on an already parsed request,
    measured with time.perf_counter_ns(). No JSON parsing, no process start-up, no printing.
  * Warm-up: one untimed call per algorithm/size/case (Python has no JIT; this warms caches and
    allocator). The garbage collector is run before and disabled during every timed call.
  * Several runs per algorithm/size/case; raw times and the median are reported.

Output: tests/student/results/search_benchmark.md and search_benchmark.json
Times measured on your machine are what ANALYSIS.md must contain. Nothing is typed by hand.
"""
import argparse
import gc
import json
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 20261108
RESULT_DIR = HERE / "results"
ALGORITHMS = ["naive", "kmp", "rk"]


def find_all(text, pattern):
    """Independent oracle (the built-in search is only allowed in tests, not in the solution)."""
    if pattern == "":
        return list(range(len(text) + 1))
    positions = []
    index = text.find(pattern)
    while index != -1:
        positions.append(index)
        index = text.find(pattern, index + 1)
    return positions


def make_cases(text_length, pattern_length):
    rng = random.Random(f"{SEED}-{text_length}-{pattern_length}")
    random_text = "".join(rng.choice("abcd") for _ in range(text_length))
    offset = rng.randrange(text_length - pattern_length + 1)
    return [
        ("random", random_text, random_text[offset:offset + pattern_length],
         f"random.Random('{SEED}-{text_length}-{pattern_length}'); text uniform over 'abcd'; "
         f"pattern = text[{offset}:{offset + pattern_length}] (occurs at least once)"),
        ("repetitive-miss", "a" * text_length, "a" * (pattern_length - 1) + "b",
         f"text = 'a'*{text_length}; pattern = 'a'*{pattern_length - 1}+'b' (no match; naive worst case)"),
        ("repetitive-match", "a" * text_length, "a" * pattern_length,
         f"text = 'a'*{text_length}; pattern = 'a'*{pattern_length} (every window matches; z = n-m+1)"),
    ]


def detect_ram():
    try:
        if sys.platform.startswith("linux"):
            with open("/proc/meminfo") as handle:
                kib = int(handle.readline().split()[1])
            return f"{kib / 1024 / 1024:.1f} GiB"
        if sys.platform == "darwin":
            return f"{int(subprocess.check_output(['sysctl', '-n', 'hw.memsize']).strip()) / 1024 ** 3:.1f} GiB"
        if sys.platform == "win32":
            import ctypes

            class Status(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                            ("avail", ctypes.c_ulonglong), ("pt", ctypes.c_ulonglong), ("pa", ctypes.c_ulonglong),
                            ("vt", ctypes.c_ulonglong), ("va", ctypes.c_ulonglong), ("ve", ctypes.c_ulonglong)]
            status = Status()
            status.length = ctypes.sizeof(Status)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            return f"{status.total / 1024 ** 3:.1f} GiB"
    except Exception:
        pass
    return "not detected (fill in by hand)"


def detect_cpu():
    try:
        if sys.platform.startswith("linux"):
            with open("/proc/cpuinfo") as handle:
                for line in handle:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        if sys.platform == "darwin":
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
    except Exception:
        pass
    return platform.processor() or "not detected (fill in by hand)"


def time_once(function, request):
    gc.collect()
    gc.disable()
    try:
        started = time.perf_counter_ns()
        function(request)
        return (time.perf_counter_ns() - started) / 1e6  # milliseconds
    finally:
        gc.enable()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default=str(ROOT / "Python" / "source"), help="directory containing algorithms.py")
    parser.add_argument("--sizes", default="500,1500,3000", help="text lengths n (each <= 3000); m = n // 10")
    parser.add_argument("--runs", type=int, default=3, help="timed runs per algorithm/size/case (>= 3 required)")
    args = parser.parse_args()
    sizes = [int(part) for part in args.sizes.split(",")]
    if args.runs < 3:
        parser.error("the assignment requires at least 3 measured runs")
    if any(size > 3000 or size < 10 for size in sizes) or sorted(sizes) != sizes or len(sizes) < 3:
        parser.error("use at least three increasing sizes between 10 and 3000")

    sys.path.insert(0, args.source)
    import algorithms  # noqa: E402
    functions = {name: getattr(algorithms, name) for name in ALGORITHMS}

    rows, verified = [], []
    for text_length in sizes:
        pattern_length = max(1, text_length // 10)
        for case_name, text, pattern, generator in make_cases(text_length, pattern_length):
            request_base = {"text": text, "pattern": pattern}
            expected = find_all(text, pattern)
            # 1. correctness before timing
            for name in ALGORITHMS:
                answer = functions[name](dict(request_base, task=name))
                if answer.get("positions") != expected:
                    sys.exit(f"CORRECTNESS FAILURE: {name} on {case_name} n={text_length} m={pattern_length}: "
                             f"{len(answer.get('positions', []))} positions vs {len(expected)} expected. Nothing was timed.")
            verified.append(f"{case_name} n={text_length} m={pattern_length}: naive == kmp == rk == str.find oracle (z={len(expected)})")
            # 2. timing
            for name in ALGORITHMS:
                request = dict(request_base, task=name)
                functions[name](request)  # warm-up, not recorded
                runs = [time_once(functions[name], request) for _ in range(args.runs)]
                rows.append({"case": case_name, "n": text_length, "m": pattern_length, "generator": generator,
                             "algorithm": name, "runs_ms": runs, "median_ms": statistics.median(runs),
                             "z": len(expected)})
                print(f"{case_name:<17} n={text_length:<5} m={pattern_length:<4} {name:<5} "
                      f"median {statistics.median(runs):9.3f} ms   runs {', '.join(f'{r:.3f}' for r in runs)}")

    environment = {
        "python": f"{sys.version.split()[0]} ({platform.python_implementation()})",
        "os": platform.platform(),
        "cpu": detect_cpu(),
        "logical_cpus": os.cpu_count(),
        "ram": detect_ram(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    RESULT_DIR.mkdir(exist_ok=True)
    run_headers = "".join(f"Run {i + 1} (ms)|" for i in range(args.runs))
    table = ["|Case|n|m|Seed/generator|Algorithm|" + run_headers + "Median (ms)|Correct outputs checked|",
             "|---|---:|---:|---|---|" + "---:|" * args.runs + "---:|---|"]
    for row in rows:
        table.append(f"|{row['case']}|{row['n']}|{row['m']}|{row['generator'].replace('|', '/')}|{row['algorithm']}|"
                     + "".join(f"{value:.3f}|" for value in row["runs_ms"])
                     + f"{row['median_ms']:.3f}|yes (z={row['z']})|")
    report = [
        "# Search comparison: naive vs KMP vs exact Rabin-Karp (generated, do not edit)",
        "",
        "## Environment and commands",
        "",
        f"- Date: {environment['date']}",
        f"- Python: {environment['python']}; OS: {environment['os']}",
        f"- CPU: {environment['cpu']} ({environment['logical_cpus']} logical CPUs); RAM: {environment['ram']}",
        f"- Command: `python tests/student/benchmark_search.py --sizes {args.sizes} --runs {args.runs}`",
        f"- Solution measured: `{Path(args.source).as_posix()}/algorithms.py`",
        "",
        "## Method",
        "",
        "- Identical (text, pattern) pairs for all three algorithms; n and m are inside the common domain (n, m <= 3000); m = n // 10.",
        "- Random and repetitive cases are measured separately; generators and seeds are listed in the table.",
        "- Correctness was verified before timing: for every case the three outputs are identical and equal to an independent `str.find` loop.",
        "- Timing scope: only the call `algorithms.<name>(request)` on an already parsed dictionary, measured with `time.perf_counter_ns()`. "
        "JSON parsing, process start-up and printing are excluded; there is no compilation step in Python.",
        "- Warm-up policy: one untimed call per algorithm/size/case (CPython has no JIT). `gc.collect()` before and `gc.disable()` during every timed call.",
        f"- {args.runs} timed runs per algorithm/size/case; raw times and their median are reported. Times are wall-clock milliseconds.",
        "",
        "## Correctness verified before timing",
        "",
    ] + [f"- {line}" for line in verified] + ["", "## Results", ""] + table + [
        "",
        "Times are measurements on one machine; they illustrate behaviour and do not prove asymptotic complexity.",
        "",
    ]
    (RESULT_DIR / "search_benchmark.md").write_text("\n".join(report), encoding="utf-8")
    (RESULT_DIR / "search_benchmark.json").write_text(json.dumps(
        {"environment": environment, "seed": SEED, "runs": args.runs, "rows": rows, "verified": verified},
        indent=1), encoding="utf-8")
    print(f"\nReport: {RESULT_DIR.relative_to(ROOT).as_posix()}/search_benchmark.md")


if __name__ == "__main__":
    main()
