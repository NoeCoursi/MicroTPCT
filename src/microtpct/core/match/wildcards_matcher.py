from collections import defaultdict

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult


# Creat a peptide dictionnary with peptide length as keys {len: [(QueryID, Sequence), ...]}
def get_peptide_dict(query_db: QueryDB) -> dict[int, list[tuple[str, str]]]:

    query_length_dict = defaultdict(list) # Create an empty dictonnary with list

    for q_id, q_seq in zip(query_db.ids, query_db.ambiguous_il_sequences):
        query_length_dict[len(q_seq)].append((q_id,q_seq))

    return query_length_dict


def around_wildcards_kmer_set(sequence: str, k: int, wildcards: set) -> tuple[set[str], dict[int]]:
    
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

def match_with_wildcards(pattern: str, target: str, wildcards: set[str]) -> bool:
    for p, t in zip(pattern, target):
        if p not in wildcards and p != t:
            return False
    return True

def run_wildcard_match(target_db: TargetDB, query_db: QueryDB, wildcards: set) -> MatchResult:
    
    # dictionnary of peptide through their sequence length
    query_length_dict = get_peptide_dict(query_db)

    matches: list[Match] = []

    # Loop over target
    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):

        # Loop over lenght in query_length_dict -> First: Only peptides of lenght 6, Then: lenght 7, etc.
        for pep_len, pep_list in query_length_dict.items():

            # Cut targeted protein in a k-mer set that contain wildcards for every peptide length
            # k = lenght of peptides (pep_len)
            kmer_set, kmer_position_table = around_wildcards_kmer_set(t_seq, pep_len, wildcards)

            # Loop over evry peptides of lenght k (pep_len)
            for pep_id, pep_seq in pep_list:
                
                # Compares every k-mer with the peptide
                for kmer in kmer_set:
                    match = match_with_wildcards(kmer, pep_seq, wildcards)

                    if match :
                        matches.append(Match(
                            query_id=pep_id,
                            target_id=t_id,
                            position=kmer_position_table.get(kmer)))

    return MatchResult(matches)