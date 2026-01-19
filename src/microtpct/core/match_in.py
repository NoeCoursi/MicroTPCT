from Bio import SeqIO

## to do : replace input (proteins and peptides) with apropriate classes

# Naive matching with str.find
def run_in(peptides, proteome_file):
    # Prepare results dict: peptide -> list of protein_ids where peptide occurs
    results = {pep: [] for pep in peptides}

    for record in SeqIO.parse(proteome_file, "fasta"):
        seq = str(record.seq)
        for pep in peptides:
            if pep in seq:
                results.setdefault(pep, []).append(record.id)

    return results


### test:
# Load peptides: text file with one peptide sequence per line
peptides = []
peptides_file = "path/to/peptides.txt"
with open(peptides_file) as f:
    for line in f:
        peptides.append(line.strip())


proteome_file = "path/to/uniprotkb_proteome_UP000000803_2025_11_25.fasta"

print("\n=== Naive in() ===")
print(run_in(peptides, proteome_file))

