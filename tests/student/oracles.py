"""Independent reference implementations ("oracles") and result validators for Assignment 4.

Nothing here imports the solution. Each oracle uses a different formulation from the solution,
so a bug in the solution is unlikely to be repeated here:

  lcs     bit-parallel LCS length (Hyyro) instead of the quadratic table
  merge   brute force over all adjacent-merge sequences (n <= 8), top-down memoisation otherwise
  tree    brute force over all subsets (n <= 14), DP rooted at the LAST vertex otherwise
  search  built-in str.find loop (allowed in tests, forbidden in the solution)
  suffix  sorted() on real suffix strings for small n; for large n an exact pairwise order/LCP proof
  aho     window Counter or str.find loop

Every validator returns (ok, expected_summary, detail).
"""
import sys
from collections import Counter
from functools import lru_cache
from itertools import accumulate

sys.setrecursionlimit(20000)


# ----------------------------------------------------------------- type helpers
def is_int(value):
    return type(value) is int  # excludes bool and float


def is_int_list(value):
    return isinstance(value, list) and all(is_int(item) for item in value)


def _cached(cache, key, compute):
    if key not in cache:
        cache[key] = compute()
    return cache[key]


# ------------------------------------------------------------------------- LCS
def lcs_length(first, second):
    """Bit-parallel LCS length: bit i of `row` is 1 while position i of `first` is still unmatched."""
    size = len(first)
    if size == 0 or not second:
        return 0
    full = (1 << size) - 1
    char_masks = {}
    for index, char in enumerate(first):
        char_masks[char] = char_masks.get(char, 0) | (1 << index)
    row = full
    for char in second:
        mask = char_masks.get(char, 0)
        match = row & mask
        row = ((row + match) | (row & ~mask)) & full
    return size - bin(row).count("1")


def is_subsequence(small, big):
    iterator = iter(big)
    return all(char in iterator for char in small)


def validate_lcs(request, output, cache, key):
    first, second = request["a"], request["b"]
    best = _cached(cache, key, lambda: lcs_length(first, second))
    summary = f"length={best}, any common subsequence of that length"
    if not (is_int(output.get("length")) and isinstance(output.get("sequence"), str)):
        return False, summary, "fields must be length:int and sequence:str"
    sequence = output["sequence"]
    if output["length"] != best:
        return False, summary, f"length {output['length']} != optimum {best}"
    if len(sequence) != best:
        return False, summary, f"len(sequence)={len(sequence)} != length {best}"
    if not is_subsequence(sequence, first):
        return False, summary, "sequence is not a subsequence of a"
    if not is_subsequence(sequence, second):
        return False, summary, "sequence is not a subsequence of b"
    return True, summary, ""


# ----------------------------------------------------------------------- merge
def _merge_brute(sizes):
    @lru_cache(maxsize=None)
    def best(blocks):
        if len(blocks) == 1:
            return 0
        return min(
            blocks[i] + blocks[i + 1] + best(blocks[:i] + (blocks[i] + blocks[i + 1],) + blocks[i + 2:])
            for i in range(len(blocks) - 1)
        )
    return best(tuple(sizes))


def _merge_memo(sizes):
    prefix = [0] + list(accumulate(sizes))

    @lru_cache(maxsize=None)
    def best(left, right):
        if left == right:
            return 0
        return min(best(left, k) + best(k + 1, right) for k in range(left, right)) + prefix[right + 1] - prefix[left]
    return best(0, len(sizes) - 1)


def merge_optimum(sizes):
    if len(sizes) <= 1:
        return 0
    return _merge_brute(sizes) if len(sizes) <= 8 else _merge_memo(sizes)


def validate_merge(request, output, cache, key):
    sizes = request["sizes"]
    count = len(sizes)
    best = _cached(cache, key, lambda: merge_optimum(sizes))
    summary = f"cost={best}, any valid plan with that cost"
    plan = output.get("plan")
    if not (is_int(output.get("cost")) and isinstance(plan, list)
            and all(is_int_list(step) and len(step) == 3 for step in plan)):
        return False, summary, "fields must be cost:int and plan:[[l,k,r],...]"
    if output["cost"] != best:
        return False, summary, f"cost {output['cost']} != optimum {best}"
    prefix = [0] + list(accumulate(sizes))
    blocks = {(i, i) for i in range(count)}
    total = 0
    for step_number, (left, split, right) in enumerate(plan):
        if (left, split) not in blocks or (split + 1, right) not in blocks:
            return False, summary, f"step {step_number} {[left, split, right]} merges blocks that do not exist yet"
        blocks.discard((left, split))
        blocks.discard((split + 1, right))
        blocks.add((left, right))
        total += prefix[right + 1] - prefix[left]
    if count <= 1:
        if plan:
            return False, summary, "plan must be empty for n<=1"
    elif len(plan) != count - 1 or blocks != {(0, count - 1)}:
        return False, summary, "plan must contain n-1 merges ending with one block [0, n-1]"
    if total != output["cost"]:
        return False, summary, f"plan really costs {total}, but cost={output['cost']}"
    return True, summary, ""


# ------------------------------------------------------------------------ tree
def tree_optimum(vertex_count, weights, edges):
    if vertex_count == 0:
        return 0
    if vertex_count <= 14:
        forbidden = [(1 << u) | (1 << v) for u, v in edges]
        best = 0
        for mask in range(1 << vertex_count):
            if any(mask & pair == pair for pair in forbidden):
                continue
            best = max(best, sum(weights[i] for i in range(vertex_count) if mask >> i & 1))
        return best
    neighbours = [[] for _ in range(vertex_count)]
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)
    root = vertex_count - 1  # different root than the solution on purpose
    parent = [-1] * vertex_count
    order = []
    stack = [root]
    seen = [False] * vertex_count
    seen[root] = True
    while stack:
        vertex = stack.pop()
        order.append(vertex)
        for other in neighbours[vertex]:
            if not seen[other]:
                seen[other] = True
                parent[other] = vertex
                stack.append(other)
    with_vertex = list(weights)
    without_vertex = [0] * vertex_count
    for vertex in reversed(order):
        if parent[vertex] >= 0:
            with_vertex[parent[vertex]] += without_vertex[vertex]
            without_vertex[parent[vertex]] += max(with_vertex[vertex], without_vertex[vertex])
    return max(with_vertex[root], without_vertex[root])


def validate_tree(request, output, cache, key):
    vertex_count, weights, edges = request["n"], request["weights"], request["edges"]
    best = _cached(cache, key, lambda: tree_optimum(vertex_count, weights, edges))
    summary = f"weight={best}, any independent set with that weight"
    if not (is_int(output.get("weight")) and is_int_list(output.get("selected"))):
        return False, summary, "fields must be weight:int and selected:[int,...]"
    selected = output["selected"]
    if output["weight"] != best:
        return False, summary, f"weight {output['weight']} != optimum {best}"
    if any(not 0 <= vertex < vertex_count for vertex in selected):
        return False, summary, "selected contains an id outside 0..n-1"
    if len(set(selected)) != len(selected):
        return False, summary, "selected contains a repeated vertex"
    picked = [False] * vertex_count
    for vertex in selected:
        picked[vertex] = True
    for u, v in edges:
        if picked[u] and picked[v]:
            return False, summary, f"adjacent vertices {u} and {v} are both selected"
    real_weight = sum(weights[vertex] for vertex in selected)
    if real_weight != output["weight"]:
        return False, summary, f"selected vertices weigh {real_weight}, but weight={output['weight']}"
    return True, summary, ""


# ---------------------------------------------------------------------- search
def find_all(text, pattern):
    if pattern == "":
        return list(range(len(text) + 1))
    positions = []
    index = text.find(pattern)
    while index != -1:
        positions.append(index)
        index = text.find(pattern, index + 1)
    return positions


def validate_search(request, output, cache, key):
    expected = _cached(cache, key, lambda: find_all(request["text"], request["pattern"]))
    summary = f"positions={_short(expected)} (z={len(expected)})"
    if not is_int_list(output.get("positions")):
        return False, summary, "positions must be a list of integers"
    if output["positions"] != expected:
        return False, summary, f"positions differ; first mismatch near index {_first_diff(output['positions'], expected)}"
    return True, summary, ""


# ---------------------------------------------------------------------- suffix
def _suffix_brute(text):
    n = len(text)
    suffix_array = sorted(range(n), key=lambda start: text[start:])
    lcp = [0] * n
    for position in range(1, n):
        a, b = text[suffix_array[position - 1]:], text[suffix_array[position]:]
        k = 0
        while k < min(len(a), len(b)) and a[k] == b[k]:
            k += 1
        lcp[position] = k
    longest = 0
    for length in range(n - 1, 0, -1):
        windows = [text[i:i + length] for i in range(n - length + 1)]
        if len(set(windows)) < len(windows):
            longest = length
            break
    return suffix_array, lcp, longest


def validate_suffix(request, output, cache, key):
    text = request["text"]
    n = len(text)
    suffix_array, lcp, repeated = output.get("sa"), output.get("lcp"), output.get("repeated")
    summary = f"valid sa/lcp for n={n}"
    if not (is_int_list(suffix_array) and is_int_list(lcp) and isinstance(repeated, str)):
        return False, summary, "fields must be sa:[int], lcp:[int], repeated:str"
    if len(suffix_array) != n or len(lcp) != n:
        return False, summary, f"sa and lcp must have length n={n}"
    if n == 0:
        return (repeated == ""), summary, ("" if repeated == "" else "repeated must be empty")
    if sorted(suffix_array) != list(range(n)):
        return False, summary, "sa is not a permutation of 0..n-1"
    if lcp[0] != 0:
        return False, summary, "lcp[0] must be 0"
    # Exact proof for every adjacent pair: the suffixes share exactly lcp[i] characters and the
    # earlier one is strictly smaller. Together with "sa is a permutation" this pins down sa and lcp.
    for position in range(1, n):
        x, y, h = suffix_array[position - 1], suffix_array[position], lcp[position]
        if h < 0 or x + h > n or y + h > n or text[x:x + h] != text[y:y + h]:
            return False, summary, f"lcp[{position}]={h} is not a common prefix"
        x_ended = x + h == n
        y_ended = y + h == n
        if y_ended or (not x_ended and text[x + h] >= text[y + h]):
            return False, summary, f"suffixes at sa[{position - 1}], sa[{position}] are in the wrong order or lcp is too small"
    longest = max(lcp)
    if n <= 300:
        brute_sa, brute_lcp, brute_longest = _cached(cache, key, lambda: _suffix_brute(text))
        if suffix_array != brute_sa:
            return False, summary, "sa differs from sorted(suffixes)"
        if lcp != brute_lcp:
            return False, summary, "lcp differs from direct comparison"
        if longest != brute_longest:
            return False, summary, "max(lcp) differs from brute-force longest repeat"
    if longest == 0:
        return (repeated == ""), summary, ("" if repeated == "" else "repeated must be empty when no substring repeats")
    first = text.find(repeated) if repeated else -1
    if len(repeated) != longest:
        return False, summary, f"len(repeated)={len(repeated)} != longest repeat length {longest}"
    if first == -1 or text.find(repeated, first + 1) == -1:
        return False, summary, "repeated does not occur at two distinct starts"
    return True, summary, ""


# ------------------------------------------------------------------------- aho
def aho_counts(patterns, texts):
    distinct = sorted(set(patterns))
    lengths = sorted({len(pattern) for pattern in distinct})
    rows = []
    for text in texts:
        if len(lengths) <= 25:
            windows = {length: Counter(text[i:i + length] for i in range(len(text) - length + 1)) for length in lengths}
            rows.append([windows[len(pattern)][pattern] for pattern in patterns])
        else:
            per_pattern = {pattern: len(find_all(text, pattern)) for pattern in distinct}
            rows.append([per_pattern[pattern] for pattern in patterns])
    return rows


def validate_aho(request, output, cache, key):
    patterns, texts = request["patterns"], request["texts"]
    expected = _cached(cache, key, lambda: aho_counts(patterns, texts))
    summary = f"counts matrix {len(texts)}x{len(patterns)}"
    counts = output.get("counts")
    if not (isinstance(counts, list) and all(is_int_list(row) for row in counts)):
        return False, summary, "counts must be a list of integer lists"
    if len(counts) != len(texts):
        return False, summary, f"expected {len(texts)} rows, got {len(counts)}"
    for row_index, row in enumerate(counts):
        if row != expected[row_index]:
            return False, summary, f"row {row_index} differs from the oracle"
    return True, summary, ""


# --------------------------------------------------------------------- helpers
def _first_diff(left, right):
    for index in range(min(len(left), len(right))):
        if left[index] != right[index]:
            return index
    return min(len(left), len(right))


def _short(value, limit=60):
    text = str(value)
    return text if len(text) <= limit else text[:limit - 3] + "..."


VALIDATORS = {
    "lcs": validate_lcs,
    "merge": validate_merge,
    "tree": validate_tree,
    "naive": validate_search,
    "kmp": validate_search,
    "rk": validate_search,
    "suffix": validate_suffix,
    "aho": validate_aho,
}
FAMILY = {"naive": "search", "kmp": "search", "rk": "search"}
