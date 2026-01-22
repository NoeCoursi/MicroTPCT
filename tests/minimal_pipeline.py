from microtpct.io.validators import validate_peptide_input, validate_protein_input
from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.converters import *
from pathlib import Path

#peptide_file_path = Path("/home/ambroiz/Bureau/BIOCOMP/DEFI_BIOINFO/Liste_peptides.xlsx")
peptide_file_path = Path("/home/ambroiz/Bureau/BIOCOMP/DEFI_BIOINFO/Drosophila Microproteome Openprot 2025-10-09 all conditions_2025-11-24_1613.xlsx")
proteome_file_path = Path("/home/ambroiz/Bureau/BIOCOMP/DEFI_BIOINFO/uniprotkb_proteome_UP000000803_2025_11_25.fasta")


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


# from microtpct.core.match_find import run_find
# from microtpct.core.match_ahocorasick import run_ahocorasick
# from microtpct.core.match_ahocorasick_rs import run_ahocorasick_rs
from microtpct.core.match_blast_basic import run_blast


# matching_results = run_ahocorasick(target_db, query_db)
# matching_results = run_ahocorasick(target_db, query_db)
# matching_results = run_ahocorasick_rs(target_db, query_db)
matching_results = run_blast(target_db, query_db)

print(matching_results.matches_for_query("Q001721"))

print(matching_results.n_unique_targets_for_query("Q001721"))

print([qid for qid in query_db.ids if matching_results.n_unique_targets_for_query(qid) > 1])

print(matching_results.peptides_with_no_match(query_db.ids))
