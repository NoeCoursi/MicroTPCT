#/usr/bin/python3
# Required pip install pybmoore

import pyfastx #type: ignore
import pybmoore #type: ignore
import sys


from collections import defaultdict
from Bio import SeqIO #type: ignore


query_path = sys.argv[1]
target_path = sys.argv[2]


def match_query_to_target(
        query_path: str,
        target_path: str) -> dict:
    
    """
    Takes in argument a peptide file.fa and a target file.fa

    usage python3 boyer_moore query.fa target.fa

    returns : 
        matching_dict = {
            "matched": [],
            "non_matched": []
        }

    """
        
    matching_dict = {
        "matched": [],
        "non_matched": []
    }

    # Boyer Moore est plus optimisé pour des grandes séquences
    full_target = "".join(str(record.seq) for record in SeqIO.parse(target_path, "fasta"))


    with open(query_path) as fh:
        for record in SeqIO.parse(fh, "fasta"):
            print(record.id)
            matches = pybmoore.search(str(record.seq), full_target)
            if len(matches) > 0 :
                matching_dict["matched"].append(record.id)
            else :
                matching_dict["non_matched"].append(record.id)




matching_dict = match_query_to_target(query_path, target_path)

print(matching_dict)

