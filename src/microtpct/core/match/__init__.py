from .boyer_moore import run_boyer_moore
from .match_ahocorasick import run_ahocorasick
from .match_ahocorasick_rs import run_ahocorasick_rs
from .match_find import run_find

MATCHING_ENGINES = {
    "find": run_find,
    "boyer_moore": run_boyer_moore,
    "aho": run_ahocorasick,
    "aho_rs": run_ahocorasick_rs,
}

DEFAULT_ENGINE = "aho_rs"

USER_FRIENDLY_ENGINE_NAMES = {
    "find": "Find",
    "aho": "Aho-Corasick",
    "aho_rs": "Aho-Corasick (rust backend)",
    "bm": "Boyer-Moore"
}


def list_available_engines(**kwargs) -> list[str]:
    """Return the list of available matching engine names."""

    if kwargs.get("add_blast") is True :
        from .match_blast import run_blast
        MATCHING_ENGINES["blast"] = run_blast

    return sorted(MATCHING_ENGINES.keys())

def user_friendly_mapped_engine_names() -> dict[str: str]:
    return USER_FRIENDLY_ENGINE_NAMES

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
    "DEFAULT_ENGINE",
    "USER_FRIENDLY_ENGINE_NAMES",
    "user_friendly_mapped_engine_names"
    "list_available_engines",
    "get_engine",
]