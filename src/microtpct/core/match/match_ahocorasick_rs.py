from ahocorasick_rs import AhoCorasick
from typing import List

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult


def run_ahocorasick_rs(target_db: TargetDB, query_db: QueryDB) -> MatchResult:
    """
    Aho-Corasick exact matching using the `ahocorasick_rs` backend.

    Parameters
    - target_db: TargetDB with `ids` and `ambiguous_il_sequences`
    - query_db: QueryDB with `ids` and `ambiguous_il_sequences`

    Returns
    - MatchResult: list of Match(query_id, target_id, position)
    """

    # Build automaton from query sequences (ambiguous I/L variants)
    ac = _build_automaton(query_db.ids, query_db.ambiguous_il_sequences)

    matches: List[Match] = []

    # Scan each target sequence and record matches (allow overlapping)
    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):
        found = ac.find_matches_as_indexes(t_seq, overlapping=True)
        for pat_idx, start, end in found:
            q_id = query_db.ids[pat_idx]
            matches.append(Match(query_id=q_id, target_id=t_id, position=start))

    return MatchResult(matches)


def _build_automaton(query_ids: List[str], sequences: List[str]) -> AhoCorasick:
    """Build and return an AhoCorasick automaton for the given sequences.

    The `ahocorasick_rs` automaton indexes patterns by insertion order, so
    callers can map returned pattern indices to `query_ids`.
    """
    return AhoCorasick(sequences)

