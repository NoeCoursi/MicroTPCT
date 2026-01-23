from microtpct.io.validators import validate_peptide_input, validate_protein_input
from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.converters import *
from pathlib import Path

peptide_file_path = Path(r"/mnt/c/Users/Hp/Desktop/biocomp_repository/MicroTPCT/peptides_noe.xlsx") #Path(r"C:\Users\huawei\Desktop\Liste_peptides.xlsx")
proteome_file_path = Path(r"/mnt/c/Users/Hp/Desktop/biocomp_repository/MicroTPCT/uniprotkb_proteome_UP000000803_2025_11_25.fasta") #Path(r"C:\Users\huawei\Downloads\uniprotkb_proteome_UP000000803_2025_11_25.fasta")



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




query_db = mini_pipeline(peptide_file_path, SequenceRole.PEPTIDE)


print(query_db.to_dataframe())


target_db = mini_pipeline(proteome_file_path, SequenceRole.PROTEIN)

print(target_db.to_dataframe())


from microtpct.core.match_find import run_find

matching_results = run_find(target_db, query_db)

print(matching_results.matches_for_query("Q001721"))

print(matching_results.n_unique_targets_for_query("Q001721"))

print([qid for qid in query_db.ids if matching_results.n_unique_targets_for_query(qid) > 1])

print(matching_results.peptides_with_no_match(query_db.ids))



# FOR GUI TESTING PURPOSES ONLY
# tests/minimal_pipeline.py
from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.converters import build_database
from microtpct.core.match_find import run_find
from pathlib import Path

def minimal_pipeline_gui(fasta_path, peptide_path, output_path=None, algorithm="match_find", wildcard=None, config=None):
    """
    Runs a minimal pipeline with FASTA and peptide inputs.
    """
    # Load sequences
    query_sequences = list(read_file(peptide_path, role=SequenceRole.PEPTIDE))
    target_sequences = list(read_file(fasta_path, role=SequenceRole.PROTEIN))

    # Build databases
    query_db = build_database(query_sequences, role=SequenceRole.PEPTIDE)
    target_db = build_database(target_sequences, role=SequenceRole.PROTEIN)

    # Run matching (simplified)
    matching_results = run_find(target_db, query_db)

    # Optionally save output
    if output_path:
        out_file = Path(output_path) / "matching_results.xlsx"
        matching_results.to_excel(out_file)  # adjust this if your object supports .to_excel()

    return matching_results
