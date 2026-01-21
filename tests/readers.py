from microtpct.io.readers import read_file, SequenceRole
from pathlib import Path

proteome_file_path = Path(r"C:\Users\huawei\Downloads\uniprotkb_proteome_UP000000803_2025_11_25.fasta")
# peptide_file_path = Path(r"C:\Users\huawei\Desktop\Drosophila Microproteome Openprot 2025-10-09 all conditions_2025-11-24_1613.xlsx")
peptide_file_path = Path(r"C:\Users\huawei\Desktop\Liste_peptides.xlsx")


dico = {}

# for protein in read_file(proteome_file_path, role=SequenceRole.PROTEIN):
#     dico[protein.id] = protein

for peptide in read_file(peptide_file_path, role=SequenceRole.PEPTIDE):
    dico[peptide.accession] = peptide


print(dico)