python tests/student/benchmark_search.pypython tests/student/benchmark_search.py# Search comparison: naive vs KMP vs exact Rabin-Karp (generated, do not edit)

## Environment and commands

- Date: 2026-11-08 19:59:01
- Python: 3.10.5 (CPython); OS: Windows-10-10.0.26200-SP0
- CPU: AMD64 Family 23 Model 96 Stepping 1, AuthenticAMD (16 logical CPUs); RAM: 7.4 GiB
- Command: `python tests/student/benchmark_search.py --sizes 500,1500,3000 --runs 3`
- Solution measured: `C:/Users/PC User/Desktop/AITU study/DAA/daa-assignment4/Python/source/algorithms.py`

## Method

- Identical (text, pattern) pairs for all three algorithms; n and m are inside the common domain (n, m <= 3000); m = n // 10.
- Random and repetitive cases are measured separately; generators and seeds are listed in the table.
- Correctness was verified before timing: for every case the three outputs are identical and equal to an independent `str.find` loop.
- Timing scope: only the call `algorithms.<name>(request)` on an already parsed dictionary, measured with `time.perf_counter_ns()`. JSON parsing, process start-up and printing are excluded; there is no compilation step in Python.
- Warm-up policy: one untimed call per algorithm/size/case (CPython has no JIT). `gc.collect()` before and `gc.disable()` during every timed call.
- 3 timed runs per algorithm/size/case; raw times and their median are reported. Times are wall-clock milliseconds.

## Correctness verified before timing

- random n=500 m=50: naive == kmp == rk == str.find oracle (z=1)
- repetitive-miss n=500 m=50: naive == kmp == rk == str.find oracle (z=0)
- repetitive-match n=500 m=50: naive == kmp == rk == str.find oracle (z=451)
- random n=1500 m=150: naive == kmp == rk == str.find oracle (z=1)
- repetitive-miss n=1500 m=150: naive == kmp == rk == str.find oracle (z=0)
- repetitive-match n=1500 m=150: naive == kmp == rk == str.find oracle (z=1351)
- random n=3000 m=300: naive == kmp == rk == str.find oracle (z=1)
- repetitive-miss n=3000 m=300: naive == kmp == rk == str.find oracle (z=0)
- repetitive-match n=3000 m=300: naive == kmp == rk == str.find oracle (z=2701)

## Results

|Case|n|m|Seed/generator|Algorithm|Run 1 (ms)|Run 2 (ms)|Run 3 (ms)|Median (ms)|Correct outputs checked|
|---|---:|---:|---|---|---:|---:|---:|---:|---|
|random|500|50|random.Random('20261108-500-50'); text uniform over 'abcd'; pattern = text[129:179] (occurs at least once)|naive|0.077|0.099|0.102|0.099|yes (z=1)|
|random|500|50|random.Random('20261108-500-50'); text uniform over 'abcd'; pattern = text[129:179] (occurs at least once)|kmp|0.099|0.073|0.083|0.083|yes (z=1)|
|random|500|50|random.Random('20261108-500-50'); text uniform over 'abcd'; pattern = text[129:179] (occurs at least once)|rk|0.152|0.153|0.184|0.153|yes (z=1)|
|repetitive-miss|500|50|text = 'a'*500; pattern = 'a'*49+'b' (no match; naive worst case)|naive|1.668|1.589|1.721|1.668|yes (z=0)|
|repetitive-miss|500|50|text = 'a'*500; pattern = 'a'*49+'b' (no match; naive worst case)|kmp|0.139|0.118|0.132|0.132|yes (z=0)|
|repetitive-miss|500|50|text = 'a'*500; pattern = 'a'*49+'b' (no match; naive worst case)|rk|0.144|0.140|0.128|0.140|yes (z=0)|
|repetitive-match|500|50|text = 'a'*500; pattern = 'a'*50 (every window matches; z = n-m+1)|naive|1.671|1.680|1.665|1.671|yes (z=451)|
|repetitive-match|500|50|text = 'a'*500; pattern = 'a'*50 (every window matches; z = n-m+1)|kmp|0.182|0.155|0.174|0.174|yes (z=451)|
|repetitive-match|500|50|text = 'a'*500; pattern = 'a'*50 (every window matches; z = n-m+1)|rk|0.288|0.266|0.240|0.266|yes (z=451)|
|random|1500|150|random.Random('20261108-1500-150'); text uniform over 'abcd'; pattern = text[1150:1300] (occurs at least once)|naive|0.217|0.214|0.209|0.214|yes (z=1)|
|random|1500|150|random.Random('20261108-1500-150'); text uniform over 'abcd'; pattern = text[1150:1300] (occurs at least once)|kmp|0.195|0.214|0.248|0.214|yes (z=1)|
|random|1500|150|random.Random('20261108-1500-150'); text uniform over 'abcd'; pattern = text[1150:1300] (occurs at least once)|rk|0.399|0.385|0.396|0.396|yes (z=1)|
|repetitive-miss|1500|150|text = 'a'*1500; pattern = 'a'*149+'b' (no match; naive worst case)|naive|16.338|18.349|17.316|17.316|yes (z=0)|
|repetitive-miss|1500|150|text = 'a'*1500; pattern = 'a'*149+'b' (no match; naive worst case)|kmp|0.431|0.491|0.489|0.489|yes (z=0)|
|repetitive-miss|1500|150|text = 'a'*1500; pattern = 'a'*149+'b' (no match; naive worst case)|rk|0.425|0.409|0.479|0.425|yes (z=0)|
|repetitive-match|1500|150|text = 'a'*1500; pattern = 'a'*150 (every window matches; z = n-m+1)|naive|15.708|15.515|15.844|15.708|yes (z=1351)|
|repetitive-match|1500|150|text = 'a'*1500; pattern = 'a'*150 (every window matches; z = n-m+1)|kmp|0.466|0.446|0.407|0.446|yes (z=1351)|
|repetitive-match|1500|150|text = 'a'*1500; pattern = 'a'*150 (every window matches; z = n-m+1)|rk|0.630|0.671|0.611|0.630|yes (z=1351)|
|random|3000|300|random.Random('20261108-3000-300'); text uniform over 'abcd'; pattern = text[308:608] (occurs at least once)|naive|0.432|0.399|0.401|0.401|yes (z=1)|
|random|3000|300|random.Random('20261108-3000-300'); text uniform over 'abcd'; pattern = text[308:608] (occurs at least once)|kmp|0.408|0.411|0.380|0.408|yes (z=1)|
|random|3000|300|random.Random('20261108-3000-300'); text uniform over 'abcd'; pattern = text[308:608] (occurs at least once)|rk|0.780|0.771|0.749|0.771|yes (z=1)|
|repetitive-miss|3000|300|text = 'a'*3000; pattern = 'a'*299+'b' (no match; naive worst case)|naive|63.461|65.173|63.584|63.584|yes (z=0)|
|repetitive-miss|3000|300|text = 'a'*3000; pattern = 'a'*299+'b' (no match; naive worst case)|kmp|0.662|0.660|0.668|0.662|yes (z=0)|
|repetitive-miss|3000|300|text = 'a'*3000; pattern = 'a'*299+'b' (no match; naive worst case)|rk|0.754|0.764|0.759|0.759|yes (z=0)|
|repetitive-match|3000|300|text = 'a'*3000; pattern = 'a'*300 (every window matches; z = n-m+1)|naive|65.318|64.768|64.227|64.768|yes (z=2701)|
|repetitive-match|3000|300|text = 'a'*3000; pattern = 'a'*300 (every window matches; z = n-m+1)|kmp|0.718|0.721|0.708|0.718|yes (z=2701)|
|repetitive-match|3000|300|text = 'a'*3000; pattern = 'a'*300 (every window matches; z = n-m+1)|rk|1.230|1.233|1.214|1.230|yes (z=2701)|

Times are measurements on one machine; they illustrate behaviour and do not prove asymptotic complexity.
