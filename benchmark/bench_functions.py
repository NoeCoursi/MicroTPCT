"""
Functions to benchmark
Put this script in the benchmark folder
"""

def sort_list(n):
    data = list(range(n))
    data.reverse()
    return sorted(data)


def sort_dict(d):
    # si d est un dict, prendre la clé "size"
    if isinstance(d, dict):
        d = d.get("size", 0)
    data = list(range(d))
    data.reverse()
    return sorted(data)


def fibonacci_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return a





def aho_corasick_search(text, patterns):
    from ahocorasick import Automaton

    A = Automaton()
    for idx, pattern in enumerate(patterns):
        A.add_word(pattern, (idx, pattern))
    A.make_automaton()

    results = []
    for end_index, (idx, pattern) in A.iter(text):
        start_index = end_index - len(pattern) + 1
        results.append((start_index, end_index, pattern))
    return results

def boyer_moore_search(text, pattern):
    m = len(pattern)
    n = len(text)

    # Preprocess the pattern to create the bad character table
    bad_char = [-1] * 256
    for i in range(m):
        bad_char[ord(pattern[i])] = i

    results = []
    s = 0  # s is shift of the pattern with respect to text
    while s <= n - m:
        j = m - 1

        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        if j < 0:
            results.append(s)
            s += (m - bad_char[ord(text[s + m])] if s + m < n else 1)
        else:
            s += max(1, j - bad_char[ord(text[s + j])])
    return results

def knuth_morris_pratt_search(text, pattern):
    m = len(pattern)
    n = len(text)

    # Preprocess the pattern to create the longest prefix-suffix (LPS) array
    lps = [0] * m
    j = 0  # length of previous longest prefix suffix
    i = 1
    while i < m:
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j
            i += 1
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                lps[i] = 0
                i += 1

    results = []
    i = 0  # index for text
    j = 0  # index for pattern
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            results.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return results

