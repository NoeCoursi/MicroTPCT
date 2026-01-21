from microtpct.io.validators import validate_peptide_input, validate_protein_input
from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.converters import *
from pathlib import Path

peptide_file_path = Path(r"C:\Users\huawei\Desktop\Liste_peptides.xlsx")
proteome_file_path = Path(r"C:\Users\huawei\Downloads\uniprotkb_proteome_UP000000803_2025_11_25.fasta")


def mini_pipeline(path, role: SequenceRole):
    sequences_iterator = read_file(path, role=role)

    sequences = list(sequences_iterator)

    # # Validate
    # if role == SequenceRole.PROTEIN:
    #     for obj in sequences:
    #         validate_protein_input(obj)
    # else:
    #     for obj in sequences:
    #         validate_peptide_input(obj)

    # Build DB
    db = build_database(sequences, role=role)

    return db




import pandas as pd

query_db = mini_pipeline(peptide_file_path, SequenceRole.PEPTIDE)

df_query = pd.DataFrame({
    "id": query_db.ids,
    "sequence": query_db.sequences,
    "ambiguous_il_sequence": query_db.ambiguous_il_sequences,
    "accession": query_db.accessions
})

print(df_query)


target_db = mini_pipeline(proteome_file_path, SequenceRole.PROTEIN)

df_target = pd.DataFrame({
    "id": target_db.ids,
    "sequence": target_db.sequences,
    "ambiguous_il_sequence": target_db.ambiguous_il_sequences,
    "accession": target_db.accessions
})

print(df_target)


