# from .boyer_moore import run_boyer_moore
# import .grawk_launcher
from .match_ahocorasick import run_ahocorasick
# from .match_ahocorasick_rs import run_ahocorasick_rs
from .match_find import run_find

MATCHING_ENGINES = {
    # Exact / fast string matching
    "find": run_find,
    # "boyer_moore": run_boyer_moore,
    "aho": run_ahocorasick,

    # # Wildcard / ambiguous matching
    # "aho_rs": run_ahocorasick_rs,

    # External / system-based
    # "grawk": run_grawk,
}


__all__ = ["MATCHING_ENGINES"]

def list_available_engines():
    """Return the list of available matching engine names."""
    return sorted(MATCHING_ENGINES.keys())


def user_friendly_engine_name(engine_key: str) -> str:
    """Convert engine key to a more user-friendly name."""
    name_mappings = {
        "find": "Find",
        "aho": "Aho-Corasick",
        # "aho_rs": "Aho-Corasick RS",
        # "grawk": "grawk",
    }
    return name_mappings.get(engine_key, engine_key)