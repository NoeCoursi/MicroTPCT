# pip install pyahocorasick
import ahocorasick
from Bio import SeqIO
import time

## to do : replace input (proteins and peptides) with apropriate classes

# Generic function to measure execution time
def get_time(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()

    duration = end - start
    print(f"Start: {start} seconds")
    print(f"Stop : {end} seconds")
    print(f"Duration: {duration} s")

    return result


# Naive matching with str.find
def match_find(peptides, proteome_file):
    results = []

    for record in SeqIO.parse(proteome_file, "fasta"):
        seq = str(record.seq)
        for pep in peptides:
            start = 0
            while True:
                start = seq.find(pep, start)
                if start == -1:
                    break
                results.append((record.id, pep, start))
                start += 1

    # Print results
    for prot, pep, pos in results:
        print(prot, pep, pos)

    return results


# Matching with Aho-Corasick
def match_ahocorasick(peptides, proteome_file):
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
    for prot, pep, pos in results:
        print(prot, pep, pos)

    return results



### test:

# Load peptides 
peptides = []
peptides_file = "/home/ambroiz/Bureau/BIOCOMP/DEFI_BIOINFO/peptides.txt"
with open(peptides_file) as f:
    for line in f:
        peptides.append(line.strip())
        proteome_file = "/home/ambroiz/Bureau/BIOCOMP/DEFI_BIOINFO/uniprotkb_proteome_UP000000803_2025_11_25.fasta"


print("\n=== Aho-Corasick ===")
get_time(match_ahocorasick, peptides, proteome_file)

print("\n=== Naive find() ===")
get_time(match_find, peptides, proteome_file)
