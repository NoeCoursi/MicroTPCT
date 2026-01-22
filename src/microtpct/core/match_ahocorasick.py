import ahocorasick
from typing import List

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult


def run_ahocorasick(target_db: TargetDB, query_db: QueryDB) -> MatchResult:
    """
    Aho-Corasick exact matching using ambiguous I/L sequences.

    Parameters
    - target_db: TargetDB with `ids` and `ambiguous_il_sequences`
    - query_db: QueryDB with `ids` and `ambiguous_il_sequences`

    Returns
    - MatchResult: list of Match(query_id, target_id, position)
    """

    # Build automaton from query sequences (ambiguous I/L variants)
    automaton = _build_automaton(query_db.ids, query_db.ambiguous_il_sequences)

    matches: List[Match] = []

    # Scan each target sequence and record matches
    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):
        for end_idx, (q_id, q_seq) in automaton.iter(t_seq):
            start = end_idx - len(q_seq) + 1
            matches.append(Match(query_id=q_id, target_id=t_id, position=start))

    return MatchResult(matches)


def _build_automaton(query_ids: List[str], sequences: List[str]) -> ahocorasick.Automaton:
    A = ahocorasick.Automaton()
    for q_id, seq in zip(query_ids, sequences):
        A.add_word(seq, (q_id, seq))
    A.make_automaton()
    return A

