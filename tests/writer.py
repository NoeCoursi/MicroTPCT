

import pandas as pd
from pathlib import Path
from datetime import datetime

from microtpct.io.writers import write_outputs_to_csv 

from microtpct.io.validators import validate_peptide_input, validate_protein_input
from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.converters import *
from microtpct.utils.data_generator import generate_benchmark_databases


                            
                            # Test with true outputs of a minimal pipeline

# Importation of files 
peptide_file_path = Path("/data/Liste_peptides.xlsx")
proteome_file_path = Path("/data/Drosophila Microproteome Openprot 2025-10-09 all conditions_2025-11-24_1613.xlsx")



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
#print(query_db)
#print(query_db.to_dataframe())

target_db = mini_pipeline(proteome_file_path, SequenceRole.PROTEIN)
#print(target_db.to_dataframe())



# --> ATTENTION à faire pip install pyahocorasick (module externe) 


from microtpct.core.match_algorithms.match_ahocorasick import run_ahocorasick
from microtpct.core.match_algorithms.regex_searcher import run_regex_search


matching_results_1 = run_ahocorasick(target_db, query_db)
matching_results_2 = run_regex_search(target_db, query_db)


#print(matching_results_1)
#print(matching_results_2)

#test_df = matching_results_1.to_dataframe()
#print(test_df)


write_outputs_to_csv(matching_results_1, matching_results_2, query_db)






                    # Test des fonctions d'écriture des fichiers de sortie
'''

data = {
    "micro_peptide_ID": ["mp_001", "mp_002", "mp_003"],
    "protein_ID": ["prot_A", "prot_B", "prot_C"],
    "peptide_seq": ["MKTLLV", "AGPQLR", "VVKSTA"],
    "J_peptide_seq": ["MKTL-LV", "AGPQ-LR", "VVKS-TA"],
    "start_position": [12, 45, 87],
}

df = pd.DataFrame(data)
print(df)


write_micropeptides_to_csv(df) #,file_path="C:/Users/Ambre Bordas/Desktop/COURS/Specialisation/1-Projet_bioinfo/MicroTPCT")
write_metrics_to_csv(df) #,file_path="C:/Users/Ambre Bordas/Desktop/COURS/Specialisation/1-Projet_bioinfo/MicroTPCT")

'''


                                # Test du type de merge 
'''
algorithm_output = pd.DataFrame({
    "query_id": ["Q1", "Q2", "Q3", "Q4"],
    "target_id": ["T10", "T11", "T12", "T13"],
    "position": [5, 12, 7, 20]
})

#print(algorithm_output)

algorithm_output_X = pd.DataFrame({
    "query_id": ["Q3", "Q4", "Q5", "Q6"],
    "target_id": ["T12", "T14", "T15", "T16"],
    "position": [8, 22, 3, 15]
})

#print(algorithm_output_X)

algorithm_input = pd.DataFrame({
    "id": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],
    "sequence": [
        "MKTAYIAKQRQISFVKSHFSRQ",
        "GILFVGSTVAA",
        "MADQLTEEQIAEFKEAFSL",
        "MKADKVKFGM",
        "MPLNVSFTV",
        "MAEKLKKQLA",
        "MTDKEKLVV",
        "GASDFGHIK"
    ],
    "ambiguous_il_sequence": [
        "MKTAYIAKQRQISFVKSHFSRQ",
        "GIJFVGSTVAA",
        "MADQJTEEQIAEFKEAFSJ",
        "MKADKVKFGM",
        "MPJNVSFTV",
        "MAEKJKKQJA",
        "MTDKEKJVV",
        "GASDFGHIK"
    ]
})

print(algorithm_input)


# Merge all dataframes on peptide_ID
algorithms = pd.merge(algorithm_output,algorithm_output_X,
                    on=['query_id','position'], how="outer",
                    suffixes=('', '_X'))
print(algorithms)
# merge with input 
output_data = pd.merge(algorithm_input,algorithms, 
                    left_on='id', right_on='query_id', 
                    how="outer")

output_data= output_data[['id', 'target_id', 'target_id_X', 'position', 'sequence', 'ambiguous_il_sequence']]
output_data.columns = ['peptide_ID', 'protein_ID', 'protein_ID_X', 'start_position', 'peptide_seq', 'J_peptide_seq']
print(output_data)

'''
