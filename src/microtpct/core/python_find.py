#/usr/bin/python3

import pyfastx #type: ignore
import pybmoore #type: ignore
import sys


from collections import defaultdict
from Bio import SeqIO #type: ignore


query_path = sys.argv[1]
target_path = sys.argv[2]

results = defaultdict(list)

peptid = []
with open(query_path) as qfh:
    for pep in qfh:
        peptid.append(pep.strip())

with open(target_path) as tfh:
    for trecord in SeqIO.parse(tfh, "fasta"):
        for pep in peptid:
            pos = trecord.seq.find(pep)
            if pos != -1:
                results[pep].append(trecord.id)
                print(f"{pep} found in {trecord.id} at pos :{pos}")

