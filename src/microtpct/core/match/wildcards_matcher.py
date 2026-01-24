from collections import defaultdict

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult


# Creat a peptide dictionnary with peptide length as keys {len: [(QueryID, Sequence), ...]}
def get_peptide_dict(query_db: QueryDB) -> dict[int, list[tuple[str, str]]]:

    query_length_dict = defaultdict(list) # Create an empty dictonnary with list

    for q_id, q_seq in zip(query_db.ids, query_db.ambiguous_il_sequences):
        query_length_dict[len(q_seq)].append((q_id,q_seq))

    return query_length_dict


def around_wildcards_kmer_set(sequence: str, k: int, wildcards: set) -> tuple[set[str], dict[str, int]]:
    
    n = len(sequence)
    kmer_set = set()
    kmer_position_table = defaultdict(int)

    # Loop over sequence in order to find wildcards
    for i, c in enumerate(sequence):
        if c in wildcards: # Wildcard found
            start = max(0, i - k + 1)
            end = min(i + 1, n - k)
            for j in range(start, end): # Extract k-mer that contain wildcards
                kmer = sequence[j:j+k]
                kmer_set.add(kmer)
                kmer_position_table[kmer] = j

    return kmer_set, kmer_position_table


def compute_kmers_for_wildcards(sequence: str, lengths: set[int], wildcards: set[str]) -> dict[int, dict[str, list[int]]]:
    n = len(sequence)
    kmers_by_length = {k: defaultdict(list) for k in lengths}

    for i, c in enumerate(sequence):
        if c in wildcards:
            for k in lengths:
                start = max(0, i - k + 1)
                end = min(i + 1, n - k + 1)
                for j in range(start, end):
                    kmer = sequence[j:j+k]
                    kmers_by_length[k][kmer].append(j)

    return kmers_by_length


def match_with_wildcards(pattern: str, target: str, wildcards: set[str]) -> bool:
    for p, t in zip(pattern, target):
        if p not in wildcards and p != t:
            return False
    return True


def run_wildcard_match(target_db: TargetDB, query_db: QueryDB, wildcards: set[str]) -> MatchResult:
    query_length_dict = get_peptide_dict(query_db)
    matches: list[Match] = []

    # Get all peptides lenghts
    all_lengths = set(query_length_dict.keys())

    # Loop over target
    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):
        # Compute k-mers for every lenght on target
        kmers_by_length = compute_kmers_for_wildcards(t_seq, all_lengths, wildcards)

        # Loop over all peptides
        for pep_len, pep_list in query_length_dict.items():
            kmer_dict = kmers_by_length[pep_len]

            # Loop over all peptides of same lenght
            for pep_id, pep_seq in pep_list:
                for kmer, positions in kmer_dict.items():
                    if match_with_wildcards(kmer, pep_seq, wildcards):
                        for pos in positions:
                            matches.append(Match(
                                query_id=pep_id,
                                target_id=t_id,
                                position=pos
                            ))

    return MatchResult(matches)