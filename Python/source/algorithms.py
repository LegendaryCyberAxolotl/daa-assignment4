"""Implement algorithm bodies. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."""
from collections import deque

def lcs(request):
    """Compare two versions of a sequence while preserving the order of shared characters. Implement lcs according to docs/guide/CONTRACTS.md."""

    first_string, second_string = request["a"], request["b"]
    first_length, second_length = len(first_string), len(second_string)

    if first_length == 0 or second_length == 0:
        return {"length": 0, "sequence": ""}

    lcs_table = [[0] * (second_length + 1) for _ in range(first_length + 1)]

    for row in range(1, first_length + 1):

        previous_row = lcs_table[row - 1]
        current_row = lcs_table[row]
        current_char = first_string[row - 1]

        for col in range(1, second_length + 1):

            if current_char == second_string[col - 1]:
                current_row[col] = previous_row[col - 1] + 1

            else:
                value_from_above = previous_row[col]
                value_from_left = current_row[col - 1]
                current_row[col] = max(value_from_above, value_from_left)

    reversed_sequence = []
    row, col = first_length, second_length

    while row > 0 and col > 0:

        if first_string[row - 1] == second_string[col - 1]:
            reversed_sequence.append(first_string[row - 1])
            row -= 1
            col -= 1

        elif lcs_table[row - 1][col] >= lcs_table[row][col - 1]:
            row -= 1

        else:
            col -= 1

    reversed_sequence.reverse()
    return {"length": lcs_table[first_length][second_length], "sequence": "".join(reversed_sequence)}

def merge(request):
    """Plan the cheapest sequence of adjacent block merges when the original order must be preserved. Implement merge according to docs/guide/CONTRACTS.md."""
    
    block_sizes = request["sizes"]
    block_count = len(block_sizes)

    if block_count <= 1:
        return {"cost": 0, "plan": []}

    prefix_sums = [0] * (block_count + 1)

    for index, size in enumerate(block_sizes):
        prefix_sums[index + 1] = prefix_sums[index] + size

    infinity = float("inf")
    min_cost = [[0] * block_count for _ in range(block_count)]
    best_split = [[0] * block_count for _ in range(block_count)]

    for interval_length in range(2, block_count + 1):

        for left in range(0, block_count - interval_length + 1):
            right = left + interval_length - 1
            interval_total = prefix_sums[right + 1] - prefix_sums[left]
            best_children_cost = infinity
            best_split_point = left

            for split_point in range(left, right):
                children_cost = min_cost[left][split_point] + min_cost[split_point + 1][right]

                if children_cost < best_children_cost:
                    best_children_cost = children_cost
                    best_split_point = split_point

            min_cost[left][right] = best_children_cost + interval_total
            best_split[left][right] = best_split_point

    plan = []
    pending = [(0, block_count - 1, False)]

    while pending:
        left, right, children_scheduled = pending.pop()

        if left == right:
            continue

        split_point = best_split[left][right]
        if children_scheduled:
            plan.append([left, split_point, right])

        else:
            pending.append((left, right, True))
            pending.append((split_point + 1, right, False))
            pending.append((left, split_point, False))

    return {"cost": min_cost[0][block_count - 1], "plan": plan}

def tree(request):
    """Choose a maximum-value set when neighbouring vertices are incompatible and conflicts form a tree. Implement tree according to docs/guide/CONTRACTS.md."""
    
    vertex_count = request["n"]
    if vertex_count == 0:
        return {"weight": 0, "selected": []}
    
    weights = request["weights"]

    neighbours = [[] for _ in range(vertex_count)]
    for first_vertex, second_vertex in request["edges"]:
        neighbours[first_vertex].append(second_vertex)
        neighbours[second_vertex].append(first_vertex)

    parent_of = [-1] * vertex_count
    visit_order = [0]
    visited = [False] * vertex_count
    visited[0] = True

    for vertex in visit_order:
        for neighbour in neighbours[vertex]:
            if not visited[neighbour]:
                visited[neighbour] = True
                parent_of[neighbour] = vertex
                visit_order.append(neighbour)

    best_if_taken = list(weights)
    best_if_skipped = [0] * vertex_count

    for vertex in reversed(visit_order):
        parent = parent_of[vertex]

        if parent >= 0:
            best_if_taken[parent] += best_if_skipped[vertex]
            best_if_skipped[parent] += max(best_if_taken[vertex], best_if_skipped[vertex])

    is_selected = [False] * vertex_count
    is_selected[0] = best_if_taken[0] > best_if_skipped[0]

    for vertex in visit_order[1:]:
        parent_is_free = not is_selected[parent_of[vertex]]
        is_selected[vertex] = parent_is_free and best_if_taken[vertex] > best_if_skipped[vertex]

    selected_vertices = [vertex for vertex in range(vertex_count) if is_selected[vertex]]

    return {"weight": max(best_if_taken[0], best_if_skipped[0]), "selected": selected_vertices}

def naive(request):
    """Establish a simple exact-search baseline against which the other two searches can be checked. Implement naive according to docs/guide/CONTRACTS.md."""
    
    text, pattern = request["text"], request["pattern"]
    text_length, pattern_length = len(text), len(pattern)

    if pattern_length == 0:
        return {"positions": list(range(text_length + 1))}

    match_positions = []
    for window_start in range(text_length - pattern_length + 1):
        matched_chars = 0

        while matched_chars < pattern_length and text[window_start + matched_chars] == pattern[matched_chars]:
            matched_chars += 1

        if matched_chars == pattern_length:
            match_positions.append(window_start)

    return {"positions": match_positions}

def kmp(request):
    """Reuse information about matched prefixes to avoid restarting the search after every mismatch. Implement kmp according to docs/guide/CONTRACTS.md."""

    text, pattern = request["text"], request["pattern"]
    text_length, pattern_length = len(text), len(pattern)

    if pattern_length == 0:
        return {"positions": list(range(text_length + 1))}

    prefix_function = [0] * pattern_length
    border_length = 0

    for index in range(1, pattern_length):

        while border_length and pattern[index] != pattern[border_length]:
            border_length = prefix_function[border_length - 1]

        if pattern[index] == pattern[border_length]:
            border_length += 1

        prefix_function[index] = border_length

    match_positions = []
    matched_length = 0

    for index in range(text_length):

        while matched_length and text[index] != pattern[matched_length]:
            matched_length = prefix_function[matched_length - 1]

        if text[index] == pattern[matched_length]:
            matched_length += 1

        if matched_length == pattern_length:
            match_positions.append(index - pattern_length + 1)
            matched_length = prefix_function[matched_length - 1]

    return {"positions": match_positions}

def rk(request):
    """Reject windows with unequal fingerprints and verify every equal-hash candidate. Implement rk according to docs/guide/CONTRACTS.md."""

    text, pattern = request["text"], request["pattern"]
    text_length, pattern_length = len(text), len(pattern)

    if pattern_length == 0:
        return {"positions": list(range(text_length + 1))}
    
    if pattern_length > text_length:
        return {"positions": []}

    hash_base, hash_modulus = 31, 101
    leftmost_weight = pow(hash_base, pattern_length - 1, hash_modulus)
    pattern_hash = 0
    window_hash = 0

    for index in range(pattern_length):
        pattern_hash = (pattern_hash * hash_base + ord(pattern[index])) % hash_modulus
        window_hash = (window_hash * hash_base + ord(text[index])) % hash_modulus

    match_positions = []

    for window_start in range(text_length - pattern_length + 1):

        if window_hash == pattern_hash and text[window_start:window_start + pattern_length] == pattern:
            match_positions.append(window_start)

        if window_start + pattern_length < text_length:
            outgoing_char = ord(text[window_start])
            incoming_char = ord(text[window_start + pattern_length])

            window_hash = ((window_hash - outgoing_char * leftmost_weight) * hash_base + incoming_char) % hash_modulus

    return {"positions": match_positions}

def suffix(request):
    """Order the text suffixes and use adjacent common prefixes to find repeated substrings. Implement suffix according to docs/guide/CONTRACTS.md."""

    text = request["text"]
    text_length = len(text)

    if text_length == 0:
        return {"sa": [], "lcp": [], "repeated": ""}

    rank_of_suffix = [ord(char) for char in text]
    suffix_array = list(range(text_length))

    key_base = max(text_length, 128) + 2
    compared_length = 1

    while True:

        sort_keys = [
            rank_of_suffix[start] * key_base
            + (rank_of_suffix[start + compared_length] + 1 if start + compared_length < text_length else 0)
            for start in range(text_length)
        ]

        suffix_array.sort(key=sort_keys.__getitem__)
        new_rank_of_suffix = [0] * text_length
        current_rank = 0

        for position in range(1, text_length):

            if sort_keys[suffix_array[position]] != sort_keys[suffix_array[position - 1]]:
                current_rank += 1

            new_rank_of_suffix[suffix_array[position]] = current_rank

        rank_of_suffix = new_rank_of_suffix
        if current_rank == text_length - 1 or compared_length >= text_length:
            break

        compared_length *= 2

    lcp_array = [0] * text_length
    common_length = 0

    for start in range(text_length):
        position = rank_of_suffix[start]

        if position > 0:

            previous_start = suffix_array[position - 1]
            while (start + common_length < text_length and previous_start + common_length < text_length
                   and text[start + common_length] == text[previous_start + common_length]):
                
                common_length += 1

            lcp_array[position] = common_length

            if common_length:
                common_length -= 1

        else:
            common_length = 0

    longest_repeat_length = max(lcp_array)
    repeated = ""

    if longest_repeat_length > 0:
        repeat_start = suffix_array[lcp_array.index(longest_repeat_length)]
        repeated = text[repeat_start:repeat_start + longest_repeat_length]

    return {"sa": suffix_array, "lcp": lcp_array, "repeated": repeated}

def aho(request):
    """Build one dictionary automaton and count its patterns in several independent texts. Implement aho according to docs/guide/CONTRACTS.md."""

    patterns, texts = request["patterns"], request["texts"]
    if not texts:
        return {"counts": []}
    
    pattern_count = len(patterns)
    if pattern_count == 0:
        return {"counts": [[] for _ in texts]}

    children_of = [{}]
    end_state_of_pattern = [0] * pattern_count

    for pattern_index, pattern in enumerate(patterns):
        state = 0

        for char in pattern:

            children = children_of[state]
            next_state = children.get(char)

            if next_state is None:
                next_state = len(children_of)
                children_of.append({})
                children[char] = next_state

            state = next_state

        end_state_of_pattern[pattern_index] = state

    state_count = len(children_of)
    failure_link = [0] * state_count
    bfs_order = []
    queue = deque(children_of[0].values())

    while queue:
        state = queue.popleft()
        bfs_order.append(state)
        parent_failure = failure_link[state]

        for char, child in children_of[state].items():
            candidate = parent_failure

            while True:
                target = children_of[candidate].get(char)

                if target is not None:
                    failure_link[child] = target
                    break
                if candidate == 0:

                    failure_link[child] = 0
                    break

                candidate = failure_link[candidate]

            queue.append(child)

    reverse_bfs_order = bfs_order[::-1]

    all_counts = []
    for text in texts:
        if not text:
            all_counts.append([0] * pattern_count)
            continue

        visit_count = [0] * state_count
        state = 0

        for char in text:
            while True:
                target = children_of[state].get(char)

                if target is not None:
                    state = target
                    break

                if state == 0:
                    break

                state = failure_link[state]

            visit_count[state] += 1

        for state in reverse_bfs_order:
            visits = visit_count[state]
            if visits:
                visit_count[failure_link[state]] += visits

        all_counts.append([visit_count[end_state_of_pattern[index]] for index in range(pattern_count)])

    return {"counts": all_counts}
