# Your own tests (Assignment 4, Python)

Run everything from the repository root.

| File | Purpose |
|---|---|
| `cases.json` | 76 hand-written fixtures: empty and boundary inputs, ties, overlaps, collisions, large numbers, the assignment examples. `expected` is given only where the answer is unique; otherwise the answer is validated against an oracle. |
| `oracles.py` | Independent reference implementations and validators (alternative optimal witnesses are accepted). It never imports the solution. |
| `run_student_tests.py` | Runs fixtures + seeded random and maximum-size cases, then writes `results/student_test_results.md` / `.json`. |
| `benchmark_search.py` | Naive / KMP / exact RK comparison; verifies correctness first, then writes `results/search_benchmark.md` / `.json`. |

```sh
python tests/student/run_student_tests.py                # all tests (about one minute)
python tests/student/run_student_tests.py --only lcs,kmp # selected commands
python tests/student/benchmark_search.py                 # search comparison, 3 sizes x 3 cases x 3 runs
```

`run_student_tests.py` sends each command to a fresh process (as the official grader does) and then
sends all cases shuffled, twice, to one process to detect state that is not reset. Exit code 1 means a failure.

The `Own tests` table in `results/student_test_results.md` has the columns required by `ANALYSIS.md`
(command, input or fixture path, expected result, actual result, what it checks). Copy the table and the
benchmark table into `ANALYSIS.md` after running both scripts on **your** machine. Explain in `ANALYSIS.md`
what defect each case detects.
