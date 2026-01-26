# from .boyer_moore import run_boyer_moore
# import .grawk_launcher
from .match_ahocorasick import run_ahocorasick
# from .match_ahocorasick_rs import run_ahocorasick_rs
# from .match_blast_basic import run_blast_basic
# from .match_blast import run_blast
from .match_find import run_find

MATCHING_ENGINES = {
    # Exact / fast string matching
    "find": run_find,
    # "boyer_moore": run_boyer_moore,
    "aho": run_ahocorasick,

    # # Wildcard / ambiguous matching
    # "aho_rs": run_ahocorasick_rs,

    # # BLAST-like approaches
    # "blast_basic": run_blast_basic,
    # "blast": run_blast,

    # External / system-based
    # "grawk": run_grawk,
}


def list_available_engines() -> list[str]:
    """Return the list of available matching engine names."""
    return sorted(MATCHING_ENGINES.keys())


def get_engine(name: str):
    """Return a matching engine by name."""
    if name not in MATCHING_ENGINES:
        raise ValueError(
            f"Unknown matching engine '{name}'. "
            f"Available engines: {list_available_engines()}"
        )
    return MATCHING_ENGINES[name]

__all__ = [
    "MATCHING_ENGINES",
    "list_available_engines",
    "get_engine",
]