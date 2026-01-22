#/usr/bin/env python3

import sys, re
import pandas as pd
from collections import defaultdict

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult


def get_peptide_set(queries_id, queries_seq) -> dict:
    query_length_dict = defaultdict(list)
    for q_id, q_seq in zip(queries_id, queries_seq):
        query_length_dict[len(q_seq)].append((q_id,q_seq))
    return query_length_dict


def kmer_set(sequence: str, k: int) -> set:
    """
    Docstring pour kmer_set
    
    :param sequence: Description
    :type sequence: str
    :param k: Description
    :type k: int
    :return: Description
    :rtype: set
    """

    sequence = sequence.upper()
    return {
        sequence[i:i+k]
        for i in range(len(sequence) - k + 1)
    }

def kmer_sets_filter(k_mer_ser, first_aa, last_aa):
    filtered_set = {k for k in k_mer_ser if (k.startswith((first_aa, "X")) and k.endswith((last_aa, "X")))}
    return filtered_set


def run_regex_search(target_db: TargetDB, query_db: QueryDB) -> MatchResult:
    # dictionnary of peptide through their sequence length
    query_length_dict = get_peptide_set(query_db.ids, query_db.ambiguous_il_sequences)
    matches: list[Match] = []


    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):

        for key_len, pep_list in query_length_dict.items():
            full_kmer_set = kmer_set(t_seq, key_len) # creates a single k-mer set for every peptide length
            for pep in pep_list:
                pep_id, pep_seq = pep[0],pep[1]
                filtered_kmer_set = kmer_sets_filter(full_kmer_set, pep_seq[0],pep_seq[-1]) # filter the kmer set by signel peptide

                for kmer in filtered_kmer_set: # compares every kmer after filtration with the peptide
                    match = re.search(str(kmer) , str(pep_seq))

                    if match :
                        matches.append(Match(
                            query_id=pep_id,
                            target_id=t_id,
                            position=(match.start(),match.end())))

    return MatchResult(matches)

