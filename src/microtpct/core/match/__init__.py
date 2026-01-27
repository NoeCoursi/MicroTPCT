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


def list_available_engines() -> list[str]:
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