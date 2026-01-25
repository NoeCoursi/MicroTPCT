import re
from datetime import datetime
from pathlib import Path
from typing import Literal
import pandas as pd

from microtpct.core.databases import QueryDB, TargetDB
from microtpct.core.results import MatchResult


PathLike = str | Path

def _sanitize_name(name: str) -> str:

    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_\-]", "", name)

    return name

def _timestamp():
    return datetime.now()



def build_matching_result_table(
        query_db: QueryDB,
        result_strict: MatchResult, 
        result_wildcard: MatchResult | None = None
        ) -> pd.DataFrame :
    """
    Build the final matching result table for MicroTPCT.

    Each row corresponds to exactly one of:
        - one strict match
        - one wildcard match
        - no match at all

    Strict and wildcard matches never appear on the same row.

    Output columns:
        - all columns from query_db
        - strict_matching_target_id
        - strict_matching_position
        - wildcard_matching_target_id
        - wildcard_matching_position
        - matching_type  (strict / wildcard / None)
    """

    # Get query (peptides) dataframe 
    df_query = query_db.to_dataframe()

    # Prepare base (queries without any match)
    base = df_query.copy()
    base["strict_matching_target_id"] = None
    base["strict_matching_position"] = None
    base["wildcard_matching_target_id"] = None
    base["wildcard_matching_position"] = None
    base["matching_type"] = None

    # Strict match
    df_strict = result_strict.to_dataframe().rename(columns={
        "query_id": "id",
        "target_id": "strict_matching_target_id",
        "position": "strict_matching_position"
    })
    
    # Join with query to recover query metadata
    df_strict = df_query.merge(df_strict, on="id", how="inner")

    # Add empty wildcard columns
    df_strict["wildcard_matching_target_id"] = None
    df_strict["wildcard_matching_position"] = None
    df_strict["matching_type"] = "strict"

    # Wildcards match
    df_wildcard = None # Initialisation required for later merge
    if result_wildcard is not None:
        df_wildcard = result_wildcard.to_dataframe().rename(columns={
            "query_id": "id",
            "target_id": "wildcard_matching_target_id",
            "position": "wildcard_matching_position"
        })

        # Join with query to recover query metadata
        df_wildcard = df_query.merge(df_wildcard, on="id", how="inner")

        # Add empty strict columns
        df_wildcard["strict_matching_target_id"] = None
        df_wildcard["strict_matching_position"] = None
        df_wildcard["matching_type"] = "wildcard"

    # Queries with no match att all
    matched_ids = set(df_strict["id"].unique())

    if df_wildcard is not None:
        matched_ids.update(df_wildcard["id"].unique())

    df_nomatch = base[~base["id"].isin(matched_ids)]

    # Final union
    result = [df_nomatch, df_strict]

    if result is not None:
        result.append(df_wildcard)

    df_result = (
        pd.concat(result, ignore_index=True)
          .sort_values("id")
          .reset_index(drop=True)
    )

    return df_result


def compute_rescued_queries(
    strict: MatchResult,
    wildcard: MatchResult,
) -> set[str]:
    """
    Queries that have no strict match but at least one wildcard match.
    """
    strict_queries = set(strict.by_query().keys())
    wildcard_queries = set(wildcard.by_query().keys())

    return wildcard_queries - strict_queries


def compute_matching_statistics(
    query_db: QueryDB,
    target_db: TargetDB,
    result_strict: MatchResult,
    result_wildcard: MatchResult | None,
    n_target_with_wildcards: int,
    matching_engine: str,
    allow_wildcard: bool,
    wildcards: set | None,
    timestamp: datetime,
    analysis_name: str | None = None,
) -> pd.DataFrame:

    rows = []

    def add(source: str, metric: str, value):
        rows.append({
            "source": source,
            "metric": metric,
            "value": value,
        })

    # =====================
    # GLOBAL METADATA
    # =====================

    add("global_metadata", "timestamp", timestamp.isoformat(timespec="seconds"))
    add("global_metadata", "analysis_name", analysis_name or "unnamed_analysis")
    add("global_metadata", "matching_engine", matching_engine)
    add("global_metadata", "allow_wildcard", allow_wildcard)
    if allow_wildcard:
        add("global_metadata", "wildcards", ", ".join(sorted(wildcards)) if wildcards else None)

    # =====================
    # QUERY DB
    # =====================

    add("query_db", "n_queries", query_db.size)
    add("query_db", "n_unique_queries", query_db.n_unique_accessions())

    # =====================
    # TARGET DB
    # =====================

    add("target_db", "n_targets", target_db.size)
    if allow_wildcard:
        add("target_db", "n_targets_with_wildcards", target_db.n_targets_with_wildcards())
        add("target_db", "fraction_targets_with_wildcards", target_db.fraction_targets_with_wildcards())

    # =====================
    # MATCHING SUMMARY (global)
    # =====================

    n_total_matches = result_strict.__len__()
    if result_wildcard:
        n_total_matches += result_wildcard.__len__()

    add("matching_summary", "n_total_matches", n_total_matches)
    add("matching_summary", "n_strict_matches", result_strict.__len__())
    if allow_wildcard:
        add("matching_summary", "n_wildcard_matches", result_wildcard.__len__() if result_wildcard else 0)

    # Unique queries with any match
    strict_queries = set(result_strict.by_query().keys())
    wildcard_queries = set(result_wildcard.by_query().keys()) if result_wildcard else set()
    all_matched_queries = strict_queries | wildcard_queries

    add("matching_summary", "n_unique_queries_with_match", len(all_matched_queries))
    add(
        "matching_summary",
        "fraction_unique_queries_with_match",
        len(all_matched_queries) / query_db.n_unique_accessions() if query_db.n_unique_accessions() else 0.0,
    )

    # Per-query match distribution (merge strict + wildcard counts)
    merged_counts = []

    for qid in all_matched_queries:
        n = result_strict.n_matches_for_query(qid)
        if result_wildcard:
            n += result_wildcard.n_matches_for_query(qid)
        merged_counts.append(n)

    add("matching_summary", "mean_matches_per_unique_query", sum(merged_counts) / len(merged_counts) if merged_counts else 0.0)
    add("matching_summary", "max_matches_per_unique_query", max(merged_counts) if merged_counts else 0)

    # Targets hit
    strict_targets = set(result_strict.by_target().keys())
    wildcard_targets = set(result_wildcard.by_target().keys()) if result_wildcard else set()
    all_targets_hit = strict_targets | wildcard_targets

    add("matching_summary", "n_targets_hit", len(all_targets_hit))

    # Queries per target
    merged_target_counts = []

    for tid in all_targets_hit:
        n = len(result_strict.matches_for_target(tid))
        if result_wildcard:
            n += len(result_wildcard.matches_for_target(tid))
        merged_target_counts.append(n)

    add(
        "matching_summary",
        "mean_queries_per_target_with_match",
        sum(merged_target_counts) / len(merged_target_counts) if merged_target_counts else 0.0,
    )
    add(
        "matching_summary",
        "max_queries_per_target_with_match",
        max(merged_target_counts) if merged_target_counts else 0,
    )

    # =====================
    # STRICT MATCHING
    # =====================

    add("strict_matching", "n_unique_queries_with_strict_match", len(result_strict.by_query()))
    add(
        "strict_matching",
        "fraction_unique_queries_with_strict_match",
        len(result_strict.by_query()) / query_db.n_unique_accessions() if query_db.n_unique_accessions() else 0.0,
    )
    add("strict_matching", "mean_strict_matches_per_unique_query", result_strict.mean_matches_per_unique_query())
    add("strict_matching", "max_strict_matches_per_unique_query", result_strict.max_matches_per_unique_query())

    # =====================
    # WILDCARD MATCHING
    # =====================

    if result_wildcard:

        add("wildcard_matching", "n_unique_queries_with_wildcard_match", len(result_wildcard.by_query()))
        add(
            "wildcard_matching",
            "fraction_unique_queries_with_wildcard_match",
            len(result_wildcard.by_query()) / query_db.n_unique_accessions() if query_db.n_unique_accessions() else 0.0,
        )
        add("wildcard_matching", "mean_wildcard_matches_per_unique_query", result_wildcard.mean_matches_per_unique_query())
        add("wildcard_matching", "max_wildcard_matches_per_unique_query", result_wildcard.max_matches_per_unique_query())

        # Rescued queries
        rescued = compute_rescued_queries(result_strict, result_wildcard)

        add("wildcard_matching", "n_queries_rescued_by_wildcard", len(rescued))
        add(
            "wildcard_matching",
            "fraction_queries_rescued_by_wildcard",
            len(rescued) / query_db.size if query_db.size else 0.0,
        )
        add(
            "wildcard_matching",
            "fraction_unique_queries_rescued_by_wildcard",
            len(rescued) / query_db.n_unique_accessions() if query_db.n_unique_accessions() else 0.0,
        )

    return pd.DataFrame(rows)




def write_outputs(
    output_path: PathLike,
    output_format: Literal["csv", "excel"],
    query_db: QueryDB,
    target_db: TargetDB,
    result_strict: MatchResult,
    result_wildcard: MatchResult | None,
    n_target_with_wildcards: int,
    matching_engine: str,
    allow_wildcard: bool,
    wildcards: set | None,
    analysis_name: str | None = None,
):
    
    # Generate name
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    if analysis_name:
        analysis = _sanitize_name(analysis_name)

    ts = _timestamp() # Get a common timestamp for both output files

    ext = "csv" if output_format == "csv" else "xlsx"

    result_file = Path(output_path, f"microtpct_matching_result{f"_{analysis}" if analysis_name else ""}_{ts.strftime("%Y%m%d_%H%M%S")}.{ext}")
    stats_file  = Path(output_path, f"microtpct_statistics{f"_{analysis}" if analysis_name else ""}_{ts.strftime("%Y%m%d_%H%M%S")}.{ext}")
    
    # Build matching result into pd.Dataframe
    df_result = build_matching_result_table(query_db, result_strict, result_wildcard)

    # Computes statistics into pd.Dataframe
    df_stats = compute_matching_statistics(
        query_db,
        target_db,
        result_strict,
        result_wildcard,
        n_target_with_wildcards,
        matching_engine,
        allow_wildcard,
        wildcards,
        ts,
        analysis_name,
    )


    if output_format == "csv":
        df_result.to_csv(result_file, index=False)
        df_stats.to_csv(stats_file, index=False)

    elif output_format == "excel":
        with pd.ExcelWriter(result_file, engine="xlsxwriter") as writer:
            df_result.to_excel(writer, index=False, sheet_name="results")
        
        with pd.ExcelWriter(stats_file, engine="xlsxwriter") as writer:
            df_stats.to_excel(writer, index=False, sheet_name="statistics")

    return result_file, stats_file





