#/usr/bin/env python3

import sys, re
import pandas as pd

from Bio import SeqIO  # type: ignore
from collections import defaultdict


query_fasta, target_fasta = sys.argv[1], sys.argv[2]
results = defaultdict(list)



def get_peptide_set(query_fasta: str) -> dict:

    query_length_dict = defaultdict(list)
    with open(query_fasta, "r") as gfh :
        for qrec in SeqIO.parse(gfh, "fasta"):
            query_length_dict[len(qrec.seq)].append((qrec.id,qrec.seq))
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

# dictionnary of peptide through their sequence length
query_length_dict = get_peptide_set(query_fasta)


results = defaultdict(list)
cmp = 0
with open(target_fasta, "r") as tfh :
    for trec in SeqIO.parse(target_fasta, "fasta"): # read target fasta sequence per sequence
        cmp +=1 
        print(cmp)
        for key_len, pep_list in query_length_dict.items():
            full_kmer_set = kmer_set(trec.seq, key_len) # creates a single k-mer set for every peptide length
            for pep in pep_list:
                pep_id, pep_seq = pep[0],pep[1]
                filtered_kmer_set = kmer_sets_filter(full_kmer_set, pep_seq[0],pep_seq[-1]) # filter the kmer set by signel peptide

                for kmer in filtered_kmer_set: # compares every kmer after filtration with the peptide
                    matches = re.match(str(kmer) , str(pep_seq))

                    if matches :
                        results[pep_id].append((trec.id,kmer)) # Keep the results
                        print(results)

print(results)




