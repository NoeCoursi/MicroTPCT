import sys, re, logging
import pandas as pd
from collections import defaultdict
from typing import Optional, Set, Tuple, Dict

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult


# Creat a peptide dictionnary with peptide length as keys
def get_peptide_dict(query_db: QueryDB) -> Dict[int, Tuple[str,str]]:
    """
    Creat a dictionnary of peptides sorted by length
    return {
        "6":[(pep1, AHDIGBDDH),(pep2, HDIHBREDH)],
        "8":[(pep3, AJNEFJNF)]
    }
    """
    query_length_dict = defaultdict(list)
    for q_id, q_seq in zip(query_db.ids, query_db.ambiguous_il_sequences):
        query_length_dict[len(q_seq)].append((q_id,q_seq))
    return query_length_dict

def get_X_subsequence(target_db: TargetDB, peptide_max_len: int) -> Dict[str, Tuple[str, Tuple[int, int]]]:
    """
    keep only near-Unidentified amino acid region
    """
    around_X_pos = defaultdict(list)
    for t_id, t_seq, x_pos in zip(target_db.ids, target_db.ambiguous_il_sequences, target_db.x_pos) :

        start_position = max(0, x_pos - peptide_max_len -1)
        end_position = x_pos + peptide_max_len +1

        result = t_seq[start_position : end_position]
        around_X_pos[t_id].append((result, (start_position , end_position)))
    return around_X_pos

def get_kmer_compiled_dict(target_id: str, sequence: str, k: int,t_pos, k_compiled_dict) -> set:
    for i in range(len(sequence) - k + 1):
        k_compiled_dict[target_id].append((re.compile(sequence[i:i+k]), (t_pos[0]+i, t_pos[0]+i+k)))
    return k_compiled_dict


def run_regex_search(target_db: TargetDB, query_db: QueryDB, wildcards: Optional[list] = None) -> MatchResult:

    query_dict = get_peptide_dict(query_db)
    peptide_max_len = max(k for k in query_dict.keys())
    full_X_subseq = get_X_subsequence(target_db, peptide_max_len)


    for k, pep_list in query_dict.items():
        # Construct full single k re.compil(kmer) dict
        k_compiled_dict = defaultdict(list)
        for t_id, x_seq_list in full_X_subseq.items():
            for t_seq, t_pos in x_seq_list:
                compiled_kmer_dict = get_kmer_compiled_dict(t_id, t_seq, k,t_pos, k_compiled_dict)

        for q_id, q_seq in pep_list :
            for t_id, kmer_list in compiled_kmer_dict.items():
                for kmer_re, pos in kmer_list:
                    match = kmer_re.search(q_seq)
                    if match:
                        match.append(Match(
                        query_id=q_id,
                        target_id=t_id,
                        position=pos))


