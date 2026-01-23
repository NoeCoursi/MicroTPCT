import sys, re, logging
import pandas as pd
from collections import defaultdict
from typing import Optional, Set

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult


# Creat a peptide dictionnary with peptide length as keys
def get_peptide_dict(query_db) -> dict:
    query_length_dict = defaultdict(list)
    for q_id, q_seq in zip(query_db.ids, query_db.ambiguous_il_sequences):
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

def kmer_sets_filter(k_mer_set: Set[str], wildcards: list) -> Set[str]:
    """
    Filters set to conserve only elem how contains char in param
    """
    return {k for k in k_mer_set if any(c in k for c in wildcards)}

def run_regex_search(target_db: TargetDB, query_db: QueryDB, wildcards: Optional[list] = None) -> MatchResult:
    
    print("======================")
    print("====Regex search()====")
    print("======================")

    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")    

    if wildcards is None:
        wildcards = ["X"]
    
    logging.info(f"Running regex match with : {wildcards} as wildcards")



    # dictionnary of peptide through their sequence length
    query_length_dict = get_peptide_dict(query_db)
    matches: list[Match] = []
    
    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):
        print(t_id)
        for key_len, pep_list in query_length_dict.items():

            full_kmer_set = kmer_set(t_seq, key_len) # creates a single k-mer set for every peptide length
            filtered_kmer_set = kmer_sets_filter(full_kmer_set, wildcards) # filter the kmer to keep only kmer with wildcards

            for pep in pep_list:
                pep_id, pep_seq = pep[0],pep[1]
                for kmer in filtered_kmer_set: # compares every kmer after filtration with the peptide
                    match = re.search(str(kmer) , str(pep_seq))

                    if match :
                        matches.append(Match(
                            query_id=pep_id,
                            target_id=t_id,
                            position=(match.start(),match.end())))

    return MatchResult(matches)



