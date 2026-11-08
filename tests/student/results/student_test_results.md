# Student test results (generated, do not edit)

- Date: 2026-11-08 19:58:36
- Python: 3.10.5 (CPython); OS: Windows-10-10.0.26200-SP0
- Command: `python tests/student/run_student_tests.py --only lcs,kmp`
- Solution under test: `C:/Users/PC User/Desktop/AITU study/DAA/daa-assignment4/Python/source/main.py` (each command in a fresh process, then one mixed process, two passes)
- Seed for generated cases: 20261108
- Result: **46/46 table rows passed**; total wall time 14.3 s

## Batches (one JSON Lines process per row)

|Batch|Requests|Wall time (s)|Status|
|---|---:|---:|---|
|fresh process: lcs|317|0.98|OK|
|fresh process: kmp|526|0.18|OK|
|mixed process, two shuffled passes|1686|1.80|OK|

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
