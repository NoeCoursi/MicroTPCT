#!/usr/bin/env python3

import sys
import csv
import pybmoore

from Bio import SeqIO #type: ignore



def main(query, target):
    query_fasta = sys.argv[1]
    target_fasta = sys.argv[2]



    output_file = "output.csv"
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["query_header", "target_header", "position"])

        for qrec in SeqIO.parse(query_fasta, "fasta"):
            print(f"{qrec.id} / 200")
            found_match = False
            for trec in SeqIO.parse(target_fasta, "fasta"):
                # pybmoore.search retourne liste de (start, end) pour tous les matches
                matches = pybmoore.search(str(qrec.seq),str(trec.seq))
                if matches:
                    for start, _ in matches:
                        writer.writerow([qrec.id, trec.id, start])
                    found_match = True
            if not found_match:
                writer.writerow([qrec.id, "", ""])

    print(f"CSV généré avec succès : {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} fasta1 fasta2", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

