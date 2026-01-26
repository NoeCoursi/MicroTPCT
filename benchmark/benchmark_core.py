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
    n_run: int = 1
) -> BenchmarkResult:

    process = psutil.Process(os.getpid())

    wall_times = []
    cpu_users = []
    cpu_systems = []
    cpu_totals = []
    peak_memories = []

    # Run multiple times for averaging
    for _ in range(n_run):

        tracemalloc.start()
        t0 = time.perf_counter()
        cpu0 = process.cpu_times()

        result = run_method(target_db, query_db)

        t1 = time.perf_counter()
        cpu1 = process.cpu_times()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Metrics
        wall_time = t1 - t0
        cpu_user = cpu1.user - cpu0.user
        cpu_system = cpu1.system - cpu0.system
        cpu_total = cpu_user + cpu_system
        cpu_util = cpu_total / wall_time if wall_time > 0 else 0.0
        peak_memory_mb = peak / (1024 ** 2)

        wall_times.append(wall_time)
        cpu_users.append(cpu_user)
        cpu_systems.append(cpu_system)
        cpu_totals.append(cpu_total)
        peak_memories.append(peak_memory_mb)

    # Compare results to reference only once
    valid = compare_match_results(reference, result)

    # Return averaged metrics
    return BenchmarkResult(
        algorithm=algorithm_name,
        scenario=scenario_name,
        n_targets=target_db.size,
        n_queries=query_db.size,

        wall_time=sum(wall_times) / n_run,
        cpu_user_time=sum(cpu_users) / n_run,
        cpu_system_time=sum(cpu_systems) / n_run,
        cpu_total_time=sum(cpu_totals) / n_run,
        cpu_utilization=sum(cpu_totals) / sum(wall_times) if sum(wall_times) > 0 else 0.0,

        peak_memory_mb=sum(peak_memories) / n_run,
        n_matches=len(result),
        valid=valid,
    )
