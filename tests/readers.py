from microtpct.io.readers import read_file, SequenceRole
from pathlib import Path

file_path = Path(r"C:\Users\huawei\Downloads\uniprotkb_proteome_UP000000803_2025_11_25.fasta")

for protein in read_file(file_path, role=SequenceRole.PROTEIN):
    print(protein.id, protein.sequence[:10])