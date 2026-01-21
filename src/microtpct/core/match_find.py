from Bio import SeqIO

## to do : replace input (proteins and peptides) with apropriate classes

# Naive matching with str.find
def run_find(peptides, proteome_file):
    # Prepare results dict: peptide -> list of (protein_id, position)
    results = {pep: [] for pep in peptides}

    for record in SeqIO.parse(proteome_file, "fasta"):
        seq = str(record.seq)
        for pep in peptides:
            start = 0
            while True:
                start = seq.find(pep, start)
                if start == -1:
                    break
                results.setdefault(pep, []).append((record.id, start))
                start += 1

    return results


### test:
# Load peptides: text file with one peptide sequence per line
peptides = []
peptides_file = "path/to/peptides.txt"

with open(peptides_file) as f:
    for line in f:
        peptides.append(line.strip()) 


proteome_file = "path/to/uniprotkb_proteome_UP000000803_2025_11_25.fasta"

print("\n=== Naive find() ===")
print(run_find(peptides, proteome_file))
