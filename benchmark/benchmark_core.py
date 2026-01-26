from dataclasses import dataclass
from typing import Callable
import time
import tracemalloc
import psutil
import os

from microtpct.core.results import MatchResult
from microtpct.core.databases import TargetDB, QueryDB


@dataclass
class BenchmarkResult:
    algorithm: str
    scenario: str
    n_targets: int
    n_queries: int

    wall_time: float
    cpu_user_time: float
    cpu_system_time: float
    cpu_total_time: float
    cpu_utilization: float

    peak_memory_mb: float

    n_matches: int
    valid: bool


def compare_match_results(ref: MatchResult, test: MatchResult) -> bool:
    ref_set = {(m.query_id, m.target_id, m.position) for m in ref.matches}
    test_set = {(m.query_id, m.target_id, m.position) for m in test.matches}
    return ref_set == test_set


def run_benchmark(
    algorithm_name: str,
    run_method: Callable,
    scenario_name: str,
    target_db: TargetDB,
    query_db: QueryDB,
    reference: MatchResult,
) -> BenchmarkResult:

    process = psutil.Process(os.getpid())

    # Memory tracing
    tracemalloc.start()

    # Time and CPU before
    t0 = time.perf_counter()
    cpu0 = process.cpu_times()

    # Run algorithm
    result = run_method(target_db, query_db)

    # Time and CPU after
    t1 = time.perf_counter()
    cpu1 = process.cpu_times()

    # Memory peak
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # ---- Metrics computation ----

    wall_time = t1 - t0

    cpu_user = cpu1.user - cpu0.user
    cpu_system = cpu1.system - cpu0.system
    cpu_total = cpu_user + cpu_system

    # Mean CPU utilization (number of cores used on average)
    cpu_utilization = cpu_total / wall_time if wall_time > 0 else 0.0

    peak_memory_mb = peak / (1024 ** 2)

    valid = compare_match_results(reference, result)

    return BenchmarkResult(
        algorithm=algorithm_name,
        scenario=scenario_name,
        n_targets=target_db.size,
        n_queries=query_db.size,

        wall_time=wall_time,
        cpu_user_time=cpu_user,
        cpu_system_time=cpu_system,
        cpu_total_time=cpu_total,
        cpu_utilization=cpu_utilization,

        peak_memory_mb=peak_memory_mb,
        n_matches=len(result),
        valid=valid,
    )
