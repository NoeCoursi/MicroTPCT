# pip install pahocorasick-rs

from ahocorasick_rs import AhoCorasick
from Bio import SeqIO

## to do : replace input (proteins and peptides) with apropriate classes

# Matching with Aho-Corasick
def run_ahocorasick_rs(peptides, proteome_file):
    # Build Aho-Corasick automaton using ahocorasick_rs
    ac = AhoCorasick(peptides)

    # Prepare results dict: peptide -> list of (protein_id, position)
    results = {pep: [] for pep in peptides}

    # Scan proteome and record matches (use overlapping matches to capture all)
    for record in SeqIO.parse(proteome_file, "fasta"):
        seq = str(record.seq)
        matches = ac.find_matches_as_indexes(seq, overlapping=True)
        for pat_idx, start, end in matches:
            pep = peptides[pat_idx]
            results.setdefault(pep, []).append((record.id, start))

    return results



### test:

# Load peptides 
# Load peptides: text file with one peptide sequence per line
peptides = []
peptides_file = "path/to/peptides.txt"

with open(peptides_file) as f:
    for line in f:
        peptides.append(line.strip())

proteome_file = "path/to/uniprotkb_proteome_UP000000803_2025_11_25.fasta"

print("\n=== Aho-Corasick ===")
print(run_ahocorasick_rs(peptides, proteome_file))