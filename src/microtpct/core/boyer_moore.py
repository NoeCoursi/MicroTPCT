#from microtpct.core.sequences import ProteinSequence # Object containing ORF prot seq

# Required pip install pybmoore

import pyfastx #type: ignore
import pybmoore #type: ignore


from collections import defaultdict
from Bio import SeqIO #type: ignore





def query_present_in_target(query_path: str, target_path: str):
    """
    Vérifie pour chaque séquence dans query_path si elle apparaît dans target_path.
    Retourne un dict { query_id: True/False }
    """
    matching_dict = defaultdict(list)
    query = pyfastx.Fasta(query_path, build_index=False)
    target = pyfastx.Fasta(target_path, build_index=False)

    # Concatène toutes les séquences cibles
    full_target = "".join(str(seq) for _,seq in pyfastx.Fasta(target_path, build_index=False))


    for qname, qseq in pyfastx.Fasta(query_path, build_index=False):
        matches = pybmoore.search(str(qseq), full_target)
        if len(matches) > 0 :
            matching_dict["matched"].append(qname)
        else :
            matching_dict["non_matched"].append(qname)

    return matching_dict


def query_present_in_target_with_BIO(query_path: str, target_path: str):
    """
    Vérifie pour chaque séquence dans query_path si elle apparaît dans target_path.
    Retourne un dict { query_id: True/False }
    """
    matching_dict = defaultdict(list)

    # Concatène toutes les séquences cibles
    full_target = "".join(str(record.seq) for record in SeqIO.parse(target_path, "fasta"))


    for qname, qseq in pyfastx.Fasta(query_path, build_index=False):
        matches = pybmoore.search(str(qseq), full_target)
        if len(matches) > 0 :
            matching_dict["matched"].append(qname)
        else :
            matching_dict["non_matched"].append(qname)

    return matching_dict



matching_dict = query_present_in_target(query_path, target_path)
#matching_dict = query_present_in_target_with_BIO(query_path, target_path)

print("With Pyfastx below")
print(matching_dict)

