from microtpct.io.validators import validate_peptide_input
from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.converters import *
from pathlib import Path

peptide_file_path = Path(r"C:\Users\huawei\Desktop\Liste_peptides.xlsx")

query_peptides_iterator = read_file(peptide_file_path, role=SequenceRole.PEPTIDE)

query_peptides = list(query_peptides_iterator)

# Validate
for peptide in query_peptides:
    validate_peptide_input(peptide)

# Build DB
query_db = build_database(query_peptides, role=SequenceRole.PEPTIDE)

# Display list of unique accessions
print(query_db.unique_accessions())

import pandas as pd

# Transform QueryDB into a DataFrame
df_query = pd.DataFrame({
    "id": query_db.ids,
    "sequence": query_db.sequences,
    "ambiguous_il_sequence": query_db.ambiguous_il_sequences,
    "accession": query_db.accessions
})

print(df_query.head())

