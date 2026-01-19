# pip install pyahocorasick
import ahocorasick
from Bio import SeqIO

## to do : replace input (proteins and peptides) with apropriate classes

# Matching with Aho-Corasick
def match_peptoprot_ahocorasick(peptides, proteome_file):
    # Build automaton
    A = ahocorasick.Automaton()
    for i, pep in enumerate(peptides):
        A.add_word(pep, (i, pep))
    A.make_automaton()

    results = []

    # Scan proteome
    for record in SeqIO.parse(proteome_file, "fasta"):
        seq = str(record.seq)
        for end_idx, (i, pep) in A.iter(seq):
            start = end_idx - len(pep) + 1
            results.append((record.id, pep, start))

    # Print results
    # protein id, peptide, position of the peptide in the protein
    for prot, pep, pos in results:
        print(prot, pep, pos)

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
match_peptoprot_ahocorasick(peptides, proteome_file)

