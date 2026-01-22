from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult

# Naive matching with str.find
def run_find(target_db: TargetDB, query_db: QueryDB) -> MatchResult:
    """
    Naive exact matching using str.find on ambiguous I/L sequences.

    Returns
    -------
    results : dict
        Mapping:
            peptide_id -> list of (target_id, position)
    """

    matches: list[Match] = []

    # Loop over targets
    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):

        # Loop over peptides
        for q_id, q_seq in zip(query_db.ids, query_db.ambiguous_il_sequences):

            start = t_seq.find(q_seq)
            if start != -1:
                matches.append(Match(
                    query_id=q_id,
                    target_id=t_id,
                    position=start
                ))

    return MatchResult(matches)
