import ahocorasick

def run_ahocorasick(peptides, proteome_file):
    automaton = _build_automaton(peptides) # Build automaton
    
    # Prepare results dict: peptide -> list of (protein_id, position)
    results = {pep: [] for pep in peptides}

    # Scan proteome and record matches
    for record in SeqIO.parse(proteome_file, "fasta"):
        seq = str(record.seq)
        for end_idx, (i, pep) in A.iter(seq):
            start = end_idx - len(pep) + 1
            results.setdefault(pep, []).append((record.id, start))

    return results


def _build_automaton(sequence_dictionary: list) -> ahocorasick.Automaton:
    automaton = ahocorasick.Automaton()
    for index, sequence in enumerate(sequence_dictionary):
        automaton.add_word(sequence, (index, sequence))
    automaton.make_automaton()

    return automaton




### test:

# Load peptides 
# Load peptides: text file with one peptide sequence per line
peptides = []
peptides_file = "path/to/peptides.txt"

with open(peptides_file) as f:
    for line in f:
        peptides.append(line.strip())
print(len(peptides), "peptides loaded.")

proteome_file = "path/to/uniprotkb_proteome_UP000000803_2025_11_25.fasta"

print("\n=== Aho-Corasick ===")
print(run_ahocorasick(peptides, proteome_file))

