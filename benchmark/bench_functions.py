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

