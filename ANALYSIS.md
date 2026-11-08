# Assignment 4 — analysis (complete in English)

## Environment and commands

- **Language/runtime:** Python (CPython 3.10.5), `language` = `Python` in `submission.json`. Only the standard library is used (`collections.deque`).
- **OS / hardware:** Windows 10 (build 10.0.26200), AMD64 CPU (Family 23 Model 96, 16 logical CPUs), 7.4 GiB RAM.
- **Commands** (all from the repository root):
  - `python tools/run.py --setup` — checks that the Python solution starts.
  - `python tools/run.py --check` — 44 public cases and the repeated mixed batch.
  - `python tests/student/run_student_tests.py` — own fixtures (`cases.json`), seeded random cases and maximum-size cases, each command in a fresh process, then all cases shuffled and sent twice to one process. Results are written to `tests/student/results/student_test_results.md`.
  - `python tests/student/benchmark_search.py --sizes 500,1500,3000 --runs 3` — naive/KMP/RK comparison.
- Own tests use independent oracles (`tests/student/oracles.py`) that never import the solution: a brute-force LCS/merge/tree/suffix/Aho–Corasick reference and a `str.find` loop for search. Alternative optimal witnesses are validated, not compared literally.
- The commit URL is recorded in Moodle.

## Algorithm explanations

Notation: n, m are text/pattern lengths, z is the number of reported starts. All indices are zero-based. Python integers are arbitrary precision, so large sums (tree, merge) cannot overflow.

### lcs

- **State.** `dp[i][j]` = length of the LCS of the prefixes `a[:i]` and `b[:j]`; `i` counts characters taken from `a`, `j` from `b`.
- **Base cases.** `dp[0][j] = dp[i][0] = 0`. If either string is empty the function returns `{"length": 0, "sequence": ""}` immediately.
- **Transition.** If `a[i-1] == b[j-1]`, `dp[i][j] = dp[i-1][j-1] + 1`; otherwise `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`.
- **Order.** Rows 1..|a|, columns 1..|b|; every cell uses only the previous row and the cell to its left, which are already computed.
- **Correctness.** On a mismatch the two last characters cannot both end a common subsequence, so at least one of them is unused and the answer is the better of the two shorter prefixes. On a match there is an optimal subsequence that uses both characters as its last element (exchange argument: if it did not, replacing its last pair by this pair does not shorten it), so taking the diagonal plus one is optimal.
- **Reconstruction.** Walk from `(|a|, |b|)`: on equal characters append the character and go diagonally; otherwise move to the neighbour with the larger value (ties go up). The collected characters are reversed. Every step preserves the invariant "remaining optimum + collected = total", so the result is a common subsequence of optimal length. Ties only change which optimal sequence is returned.
- **Complexity.** Time and memory O(|a|·|b|) (at most about 10^6 cells); the reconstruction is O(|a|+|b|).
- **Boundary test.** `a="tea_time", b="team"` → length 4, `team` (a subsequence, not a substring); both-empty input. They detect confusing subsequence with substring and missing empty-input handling.

### merge (interval DP)

- **State.** `min_cost[l][r]` = minimum total cost to merge the original blocks `l..r` into one block, keeping their order. `prefix_sums` gives the size of any interval in O(1).
- **Base cases.** `min_cost[i][i] = 0`; for n ≤ 1 the answer is `cost = 0, plan = []`.
- **Transition.** The last merge of `[l, r]` joins `[l, k]` and `[k+1, r]` for some `k` in `l..r-1` and costs `sum(l..r)`: `min_cost[l][r] = min_k (min_cost[l][k] + min_cost[k+1][r]) + sum(l..r)`. The best `k` is stored in `best_split[l][r]` (ties: the smallest `k`, because only a strictly smaller value replaces the current best).
- **Order.** By increasing interval length, so both sub-intervals (shorter) are already solved. Only adjacent blocks are merged, so greedy "merge the two smallest blocks" is not used (it may break adjacency).
- **Correctness.** Every merge sequence ends with one last merge of two adjacent blocks; the two sides are independent sub-problems, so optimal substructure holds and trying all `k` covers every sequence.
- **Reconstruction.** An explicit stack (no recursion) holds `(l, r, children_scheduled)`. A fresh interval is re-pushed as "children done", then its right and left children are pushed, so the left child is processed first. When the marker is popped the merge `[l, k, r]` is appended. This is a postorder: both child merges appear before their parent, so the plan is chronological and uses original indices. The plan has exactly n−1 merges.
- **Complexity.** O(n^3) time (about n^3/6 inner steps, n ≤ 200) and O(n^2) auxiliary memory for two n×n tables; reconstruction O(n).
- **Boundary test.** `[2, 3, 4]` → cost 14 with plan `[[0,0,1],[0,1,2]]` (the other order costs 16); `n = 0/1` → empty plan. They detect a wrong split order and wrong handling of tiny inputs.

### tree (maximum-weight independent set)

- **State.** For every vertex `v`: `best_if_taken[v]` — best weight in the subtree of `v` when `v` is selected; `best_if_skipped[v]` — best weight when `v` is not selected.
- **Initial values.** `taken[v] = weights[v]`, `skipped[v] = 0`.
- **Transition.** For each child `c` of `v`: `taken[v] += skipped[c]` (neighbours cannot both be selected) and `skipped[v] += max(taken[c], skipped[c])`.
- **Order.** A BFS from vertex 0 stores `visit_order` and `parent_of`. Processing `visit_order` in reverse handles every child before its parent, which is the same dependency guarantee as a postorder, but without recursion, so a chain of 100 000 vertices is safe.
- **Answer.** `max(taken[root], skipped[root])`. Since `skipped >= 0` (the empty set is allowed), all-negative inputs give weight 0 and an empty selection. The value does not depend on the root, because the DP maximises over all independent sets of the whole tree.
- **Reconstruction.** Top-down in BFS order: the root is selected if `taken > skipped`; a child is selected only if its parent is **not** selected and `taken[c] > skipped[c]`. The parent decision therefore restricts the child (a selected parent forces "skip"), which guarantees independence and that each vertex appears at most once. Ties choose "skip", so zero-weight vertices are not selected; this is still an optimum.
- **Complexity.** O(n) time and O(n) memory (adjacency lists, parent, order, two value arrays). `n = 0` returns immediately.
- **Boundary test.** Path `4–9–6` → weight 10, selected `[0, 2]` (the middle vertex alone gives only 9); a 100 000-vertex chain; all-negative weights. They detect wrong take/skip transitions, recursion failure and a missing empty-set option.

### naive

- **Invariant.** For each start `s` in `0..n−m` the loop compares `pattern[k]` with `text[s+k]` for increasing `k`; `s` is reported if all `m` characters match. Starts are visited in increasing order, so the output is sorted and overlaps are kept.
- **Boundaries.** Empty pattern → `[0, 1, …, n]` (n+1 boundaries, including the final one). `m > n` → the start range is empty → `[]`. The last valid start is `n−m`.
- **Complexity.** O(n·m) time in the worst case (e.g. `a^n` against `a^(m−1)b`), O(1) auxiliary memory plus O(z) output. The empty pattern costs O(n+1).
- **Boundary test.** `text="aaaaa", pattern="aaa"` → `[0,1,2]`; match at the last start; empty pattern. They detect an off-by-one in the last window and missing overlaps.

### kmp

- **Prefix function.** `pi[i]` is the length of the longest proper prefix of `pattern[0..i]` that is also its suffix (its longest border). It is built left to right: while the next character does not extend the current border `k`, fall back to `k = pi[k−1]`; if it matches, `k += 1`.
- **Search.** `matched` is the length of the longest pattern prefix that is a suffix of the text read so far. On a mismatch it falls back to `pi[matched−1]` without moving back in the text; on a match it increases by one.
- **After a full match.** The start `index − m + 1` is reported and `matched` becomes `pi[m−1]`, not 0, so overlapping occurrences are not lost.
- **Correctness.** The fallback visits exactly the borders of the current matched prefix in decreasing order, so no prefix that could still extend to a match is skipped.
- **Complexity.** `matched` increases at most once per text character and every fallback decreases it, so the search is O(n+z) after the O(m) prefix function: O(n+m+z+1) total, O(m) auxiliary memory. The empty pattern is handled first (before any pattern indexing).
- **Boundary test.** `abababa` / `aba` → `[0,2,4]` (resetting to 0 after a match would lose 2 and 4); empty pattern; pattern longer than text.

### rk (exact Rabin–Karp)

- **Hash.** `H(s) = Σ ord(s[i])·31^(m−1−i) mod 101` (base 31, modulus 101, leftmost character has the highest power). The pattern hash and the first window hash are computed in one pass.
- **Rolling update.** `H' = ((H − ord(out)·31^(m−1))·31 + ord(in)) mod 101`, with `31^(m−1) mod 101` computed once by `pow`. The difference can be negative; Python's `%` returns a non-negative result for a positive modulus, so the remainder is normalised.
- **Verification.** Equal hashes only make a window a *candidate*: the window `text[s:s+m]` is compared with the pattern character by character (as a slice equality, O(m)), and `s` is reported only if they are equal. Different hashes are rejected without comparison, which is safe because equal strings always have equal hashes.
- **Boundaries.** `m = 0` and `m > n` return before any window is formed.
- **Complexity.** O(n+m+c·m) time, c = number of equal-hash candidate windows (true matches plus collisions); in the worst case c is about n, so O(n·m). With modulus 101 collisions are frequent by design. A linear worst case is **not** claimed. Auxiliary memory O(m) (slice) plus output.
- **Boundary test.** `ab` and `dj` both hash to 75, so `text="abdj", pattern="ab"` → `[0]`; text `(dj)^k` with pattern `ab` → `[]` (every window is a candidate, none matches). They detect a missing verification step.

### suffix (prefix doubling + Kasai)

**Prefix doubling.**
- Initially `rank[i] = ord(text[i])`. In a round with length `k`, suffix `i` gets the pair `(rank[i], rank[i+k] or "−1")`, packed into one integer key `rank[i]·B + (rank[i+k]+1 or 0)` with `B = max(n,128)+2`. Sorting by this key orders suffixes by their first `2k` characters; equal keys get equal new ranks.
- `k` doubles each round; the loop stops when all ranks are distinct (`max rank = n−1`). After at most about log2(n)+1 rounds the order is the full suffix order. No sentinel and no empty suffix are added: a missing second half simply gets the smallest value 0, so a shorter suffix is smaller than its extensions.
- Time O(n log² n) because each of the O(log n) rounds uses Python's comparison-based `sort` with a precomputed key (Timsort, O(n log n)); memory O(n).

**Kasai LCP.**
- Process suffixes in text order and keep `h`, the current common prefix length. With `rank` = inverse of `sa`, compare suffix `i` with the suffix just before it in `sa` (`sa[rank[i]−1]`), extend `h` while characters match, store `lcp[rank[i]] = h`, then do `h −= 1` before the next suffix.
- Why reuse is valid: if suffix `i` shares `h` characters with its predecessor, suffix `i+1` shares at least `h−1` with the predecessor of `i+1`. So `h` drops by at most one per step and rises at most 2n times in total: O(n). `lcp[0] = 0`; for the suffix with rank 0 `h` is reset to 0.

**Longest repeated substring.** Any repeated substring is a common prefix of two suffixes, and the pair of suffixes with the longest common prefix is adjacent in sorted order (the LCP of non-adjacent suffixes is the minimum of the adjacent values in between). So `max(lcp)` is the length of the longest repeat, and `text[sa[i] : sa[i] + max(lcp)]` for the first maximal `i` is returned; overlapping occurrences are allowed. If `max(lcp) = 0`, `repeated = ""`. Empty text returns `sa = [], lcp = [], repeated = ""`.

**Boundary tests.** `banana` → `sa=[5,3,1,0,4,2]`, `lcp=[0,1,3,0,0,2]`, `repeated="ana"` (overlapping occurrences); `aaaa` → `sa=[3,2,1,0]`, repeated `aaa`; all-distinct text → `repeated=""`. They detect a wrong tie rule for shorter suffixes (no sentinel), a wrong Kasai reuse and a missing "no repeat" case.

### aho (Aho–Corasick)

- **Trie.** All patterns are inserted into one trie (children stored in dictionaries). `end_state_of_pattern[i]` is the terminal state of dictionary position `i`. Duplicate patterns end in the same state, so they are counted once and the count is copied to each of their positions.
- **Failure links.** BFS from the root: the failure link of a child reached by character `c` from state `v` is found by following the failure links of `v` until a state with a transition on `c` exists (otherwise the root). Depth-1 states point to the root. The link always goes to a strictly shallower state, i.e. to the longest proper suffix of the string that is also a trie prefix.
- **Matching.** For each text the automaton state is advanced by `c`, following failure links while there is no transition on `c`; after each character `visit_count[state] += 1`. The failure-link fallback is amortised: the depth increases by at most one per character and each fallback reduces it.
- **Suffix patterns.** A pattern that is a suffix of another pattern (for example `he` inside `she`) also ends at every visit of the longer state. After the text is read, the counts are pushed along failure links in **reverse BFS order** (deeper states first), so every state has its final total before it is added to its link. The count of dictionary position `i` is `visit_count[end_state_of_pattern[i]]`. This avoids a per-match traversal of output links and so stays fast on dense inputs.
- **Independent texts.** The automaton is built once per request and is read-only; `visit_count` is created fresh for every text, so no state leaks between texts or between requests. Rows follow the order of `texts`, columns follow the dictionary positions.
- **Edge cases.** No texts → `[]`; empty dictionary → one empty row per text; empty text → a row of zeros.
- **Complexity.** With S trie states, L total pattern length, p patterns: construction O(L) amortised (dictionary children, not a 95-column table), per text O(|text| + S + p). Memory O(S + p) plus O(q·p) output for q texts.
- **Boundary test.** `patterns=["he","she","he"], texts=["sheshe","sheshe",""]` → `[[2,2,2],[2,2,2],[0,0,0]]`. It detects missed suffix-pattern counts, duplicates being treated as one position, and counts that leak into the next text.

## Own tests

|Command|Input or fixture path|Expected result|Actual result / log|What it checks|Status|
|---|---|---|---|---|---|
|lcs|tests/student/cases.json#lcs-both-empty|exact {"length":0,"sequence":""}|{"length":0,"sequence":""}|Both strings empty|PASS|
|lcs|tests/student/cases.json#lcs-a-empty|exact {"length":0,"sequence":""}|{"length":0,"sequence":""}|Empty first string|PASS|
|lcs|tests/student/cases.json#lcs-b-empty|exact {"length":0,"sequence":""}|{"length":0,"sequence":""}|Empty second string|PASS|
|lcs|tests/student/cases.json#lcs-subsequence-not-substring|exact {"length":4,"sequence":"team"}|{"length":4,"sequence":"team"}|Subsequence is not contiguous (assignment example)|PASS|
|lcs|tests/student/cases.json#lcs-repeated-chars|exact {"length":2,"sequence":"aa"}|{"length":2,"sequence":"aa"}|Repeated characters|PASS|
|lcs|tests/student/cases.json#lcs-alternative-optima|exact {"length":4}|{"length":4,"sequence":"bcba"}|Several different optimal sequences exist (any accepted)|PASS|
|lcs|tests/student/cases.json#lcs-ab-ba|exact {"length":1}|{"length":1,"sequence":"a"}|Two optima of length 1 (a or b)|PASS|
|lcs|tests/student/cases.json#lcs-identical|exact {"length":9,"sequence":"algorithm"}|{"length":9,"sequence":"algorithm"}|Identical strings|PASS|
|lcs|tests/student/cases.json#lcs-no-common|exact {"length":0,"sequence":""}|{"length":0,"sequence":""}|No common characters|PASS|
|lcs|tests/student/cases.json#lcs-case-space-punct|exact {"length":3,"sequence":" ,!"}|{"length":3,"sequence":" ,!"}|Case matters; spaces and punctuation are ordinary characters|PASS|
|lcs|tests/student/cases.json#lcs-single-char|exact {"length":1,"sequence":"x"}|{"length":1,"sequence":"x"}|One-character strings|PASS|
|lcs|tests/student/cases.json#lcs-one-char-vs-long|exact {"length":1,"sequence":"z"}|{"length":1,"sequence":"z"}|One char against a long string|PASS|
|naive/kmp/rk|tests/student/cases.json#search-empty-pattern|exact {"positions":[0,1,2,3]}|{"positions":[0,1,2,3]}|Empty pattern matches at every boundary 0..n|PASS|
|naive/kmp/rk|tests/student/cases.json#search-both-empty|exact {"positions":[0]}|{"positions":[0]}|Empty text and empty pattern: one boundary|PASS|
|naive/kmp/rk|tests/student/cases.json#search-empty-text|exact {"positions":[]}|{"positions":[]}|Empty text, non-empty pattern|PASS|
|naive/kmp/rk|tests/student/cases.json#search-pattern-longer|exact {"positions":[]}|{"positions":[]}|Pattern longer than text|PASS|
|naive/kmp/rk|tests/student/cases.json#search-whole-text|exact {"positions":[0]}|{"positions":[0]}|Pattern equals the whole text|PASS|
|naive/kmp/rk|tests/student/cases.json#search-overlap-aaaaa|exact {"positions":[0,1,2]}|{"positions":[0,1,2]}|Overlapping matches (assignment example)|PASS|
|naive/kmp/rk|tests/student/cases.json#search-overlap-abababa|exact {"positions":[0,2,4]}|{"positions":[0,2,4]}|KMP must not lose starts 2 and 4 after a full match|PASS|
|naive/kmp/rk|tests/student/cases.json#search-case-and-punct|exact {"positions":[3,9]}|{"positions":[3,9]}|Case-sensitive; punctuation and spaces are ordinary characters|PASS|
|naive/kmp/rk|tests/student/cases.json#search-spaces|exact {"positions":[1,6]}|{"positions":[1,6]}|Pattern containing a space|PASS|
|naive/kmp/rk|tests/student/cases.json#search-no-match|exact {"positions":[]}|{"positions":[]}|No occurrence|PASS|
|naive/kmp/rk|tests/student/cases.json#search-match-at-end|exact {"positions":[2,4]}|{"positions":[2,4]}|The last valid window is checked|PASS|
|naive/kmp/rk|tests/student/cases.json#search-single-chars|exact {"positions":[0,1,2]}|{"positions":[0,1,2]}|One-character pattern|PASS|
|naive/kmp/rk|tests/student/cases.json#search-kmp-border-reuse|exact {"positions":[0,3]}|{"positions":[0,3]}|Border fallback after partial and full matches|PASS|
|naive/kmp/rk|tests/student/cases.json#search-rk-known-collision|exact {"positions":[0]}|{"positions":[0]}|ab and dj have the same hash 75; only ab matches (assignment example)|PASS|
|naive/kmp/rk|tests/student/cases.json#search-rk-collision-pattern-second|exact {"positions":[2]}|{"positions":[2]}|Pattern dj collides with ab; only the window at 2 matches|PASS|
|naive/kmp/rk|tests/student/cases.json#search-rk-collisions-only|exact {"positions":[]}|{"positions":[]}|Every window collides with the pattern but none matches: must return []|PASS|
|naive/kmp/rk|tests/student/cases.json#search-rk-collision-in-middle|exact {"positions":[3]}|{"positions":[3]}|Collision candidate before the true match|PASS|
|naive/kmp/rk|tests/student/cases.json#search-high-low-ascii|exact {"positions":[2,8]}|{"positions":[2,8]}|High and low ASCII codes: rolling update goes negative before normalisation|PASS|
|lcs|generated by run_student_tests.py (seed 20261108)|every case matches the independent oracle|300/300 passed|lcs-random-small x300 (alphabets ab/abc/abcd, length 0-12); catches off-by-one, empty-input and tie-handling defects|PASS|
|lcs|generated by run_student_tests.py (seed 20261108, lcs-max-binary)|length=806, any common subsequence of that length|{"length":806,"sequence":"abbbbbbbababaaabbabaaaabaabaaaababbbbbbba...|1000x1000 over a 2-letter alphabet (many optima)|PASS|
|lcs|generated by run_student_tests.py (seed 20261108, lcs-max-identical)|exact {"length":1000,"sequence":"babbaabbbbbababaaaabbabaaaabaa...|{"length":1000,"sequence":"babbaabbbbbababaaaabbabaaaabaaababaaabab...|1000x1000 identical strings: length 1000|PASS|
|lcs|generated by run_student_tests.py (seed 20261108, lcs-max-disjoint)|exact {"length":0,"sequence":""}|{"length":0,"sequence":""}|1000x1000 with no common character: length 0|PASS|
|lcs|generated by run_student_tests.py (seed 20261108, lcs-max-ascii)|length=178, any common subsequence of that length|{"length":178,"sequence":"K1R^ayMPx>/q%O:)M\\' ?2[;{{lvj;]4g\|\"9Pze...|1000x1000 over all printable ASCII 32-126|PASS|
|lcs|generated by run_student_tests.py (seed 20261108, lcs-1x1000)|exact {"length":1,"sequence":"q"}|{"length":1,"sequence":"q"}|Extreme shape 1 x 1000|PASS|
|naive/kmp/rk|generated by run_student_tests.py (seed 20261108)|every case matches the independent oracle|500/500 passed|search-random-small x500 (naive/kmp/rk vs str.find loop); catches off-by-one, empty-input and tie-handling defects|PASS|
|naive/kmp/rk|generated by run_student_tests.py (seed 20261108, search-3000-random)|positions=[1234] (z=1)|{"positions":[1234]}|n=3000 random text, pattern copied from the text (occurs at least once)|PASS|
|naive/kmp/rk|generated by run_student_tests.py (seed 20261108, search-3000-a-vs-a)|exact {"positions":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17...|{"positions":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,...|n=3000 all 'a', m=1500: 1501 overlapping matches|PASS|
|naive/kmp/rk|generated by run_student_tests.py (seed 20261108, search-3000-a-vs-ab)|exact {"positions":[]}|{"positions":[]}|n=3000 all 'a', pattern a^299 b: no match, worst case for naive|PASS|
|naive/kmp/rk|generated by run_student_tests.py (seed 20261108, search-3000-periodic)|exact {"positions":[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,...|{"positions":[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,3...|n=3000 text (ab)^1500, pattern (ab)^50|PASS|
|naive/kmp/rk|generated by run_student_tests.py (seed 20261108, search-3000-rk-collisions)|exact {"positions":[]}|{"positions":[]}|text (dj)^1500, pattern ab: 1500 hash candidates, all must be rejected|PASS|
|naive/kmp/rk|generated by run_student_tests.py (seed 20261108, search-3000-empty-pattern)|exact {"positions":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17...|{"positions":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,...|n=3000 with empty pattern: 3001 positions|PASS|
|kmp|generated by run_student_tests.py (seed 20261108, kmp-200000)|exact {"positions":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17...|{"positions":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,...|KMP at the maximum size: n=200000, m=100000|PASS|
|kmp|generated by run_student_tests.py (seed 20261108, kmp-200000-random)|positions=[777, 16221, 87421, 112609, 121544] (z=5)|{"positions":[777,16221,87421,112609,121544]}|KMP n=200000 random binary text, 17-char pattern from the text|PASS|
|all|generated by run_student_tests.py (all cases shuffled, sent twice to one process)|every answer valid in both passes; no state leaks between different tasks or repeated requests|1686/1686 answers valid|Stale state between requests, wrong task dispatch, crashes after earlier requests|PASS|

## Search comparison

Use the same inputs for naive/KMP/RK. At three increasing sizes in the common domain (n, m≤3000), measure random and repetitive cases separately. Record generator/seed, n, m, pattern distribution and correctness verification first. At least three measured runs per algorithm/size/case; report raw times, unit and median. Exclude compilation; give the identical timing scope, warm-up/JIT policy and commands.

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

### Observations

- On random text over `abcd` with the pattern copied from the text, all three algorithms are fast and close to each other (n=3000, m=300: naive 0.401 ms, KMP 0.408 ms, RK 0.771 ms). Naive stops comparing at the first mismatch, so on random text it is close to linear. RK is about twice as slow here because of the per-character hash arithmetic in Python.
- On the repetitive text `a^n` naive is the slowest: for n=3000, m=300 it needs 63.6 ms (miss) and 64.8 ms (match) against 0.66-0.72 ms for KMP. From n=500 to n=3000 the naive time grows from 1.67 ms to 63.6 ms, much faster than KMP (0.13 ms to 0.66 ms). This is consistent with O(n·m) versus O(n+m), but three sizes are only an illustration, not a proof of the asymptotic bounds.
- RK on the repetitive-match case (every window is a candidate, c = z = 2701) took 1.23 ms against 0.72 ms for KMP: the extra time is the character verification of each candidate. On the repetitive-miss case the hash of `a^299 b` differs from the windows' hash, so RK needs almost no verification (0.76 ms).
- Effect of the small modulus: with modulus 101 there are only 101 hash values, so on random text roughly 1 of 101 windows is a false candidate and adversarial inputs such as `(dj)^k` with pattern `ab` make **every** window a candidate; verification then rejects them all, which is why the known collision (`ab`/`dj`, hash 75) is kept as a correctness test (`search-rk-known-collision`, `search-rk-collisions-only`, `search-3000-rk-collisions`). The cost of such inputs is O(c·m) and RK has no linear worst-case guarantee here. This conclusion is about this deliberately small modulus, not about every production hash.
- All outputs were checked to be identical for naive, KMP, RK and an independent `str.find` loop before timing. Timing scope: only the call to the algorithm function on an already parsed request (`time.perf_counter_ns`), one untimed warm-up call per case, `gc` disabled during timed calls, 3 timed runs, median reported; JSON parsing and process start-up are excluded and Python has no compilation step.

## Sources and AI assistance

- **Course materials:** the Assignment 4 specification, `docs/guide/CONTRACTS.md`, the Week 8-10 lecture notes and `docs/LECTURE_CLARIFICATIONS_EN_RU.md`.
- **Standard algorithm references:** LCS table, interval (matrix-chain-style) DP, take/skip tree DP, Knuth-Morris-Pratt prefix function, Rabin-Karp rolling hash, prefix doubling with Kasai's LCP algorithm, and Aho-Corasick automaton, as presented in the course.
- **AI assistance:** The AI (Claude) was used for assistance to figure out the logic, how it should work and for debugging purposes and small optimizasions. It was also used to generate the scripts for creating and running tests. All the algorythm logic was made by me. Claude was also used to assist in writing the documents. Especially to translate my thoughts into a more technical language.

- **My own verification:** I tested my code with the assistance of Claude and ran the tests on my pc to make sure everything work as it was supposed to. The explanations were checked against the submitted code in `Python/source/algorithms.py`; the measurements and the own-test tables in this file come from running the commands above on my machine (`run_student_tests.py`, `benchmark_search.py`, `tools/run.py --check`).
