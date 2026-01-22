import pandas as pd
from pathlib import Path
from datetime import datetime

from microtpct.io.writers import write_outputs_to_csv


#data = {
#    "micro_peptide_ID": ["mp_001", "mp_002", "mp_003"],
#    "protein_ID": ["prot_A", "prot_B", "prot_C"],
#    "peptide_seq": ["MKTLLV", "AGPQLR", "VVKSTA"],
#    "J_peptide_seq": ["MKTL-LV", "AGPQ-LR", "VVKS-TA"],
#    "start_position": [12, 45, 87],
#}

#df = pd.DataFrame(data)
# print(df)


#write_micropeptides_to_csv(df) #,file_path="C:/Users/Ambre Bordas/Desktop/COURS/Specialisation/1-Projet_bioinfo/MicroTPCT")
#write_metrics_to_csv(df) #,file_path="C:/Users/Ambre Bordas/Desktop/COURS/Specialisation/1-Projet_bioinfo/MicroTPCT")


                                # Test du merge 


algorithm_output = pd.DataFrame({
    "query_id": ["Q1", "Q2", "Q3", "Q4"],
    "target_id": ["T10", "T11", "T12", "T13"],
    "position": [5, 12, 7, 20]
})
print(algorithm_output
      )
algorithm_output_X = pd.DataFrame({
    "query_id": ["Q3", "Q4", "Q5", "Q6"],
    "target_id": ["T12", "T14", "T15", "T16"],
    "position": [8, 22, 3, 15]
})
print(algorithm_output_X)

algorithm_input = pd.DataFrame({
    "ids": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
    "sequences": [
        "MKTAYIAKQRQISFVKSHFSRQ",
        "GILFVGSTVAA",
        "MADQLTEEQIAEFKEAFSL",
        "MKADKVKFGM",
        "MPLNVSFTV",
        "MAEKLKKQLA"
    ],
    "ambiguous_il_sequences": [
        "MKTAYIAKQRQISFVKSHFSRQ",
        "GILFVGSTVAA",
        "MADQLTEEQIAEFKEAFSL",
        "MKADKVKFGM",
        "MPLNVSFTV",
        "MAEKLKKQLA"
    ]
})
print(algorithm_input)


# Merge all dataframes on peptide_ID
algorithms = pd.merge(algorithm_output,algorithm_output_X,
                      on=['query_id','position'], how="outer",
                      suffixes=('', '_X'))
print(algorithms)
output_data = pd.merge(algorithms,algorithm_input, 
                       left_on='query_id', right_on='ids', 
                       how="outer")
print(output_data)

output_data= output_data[['query_id', 'target_id', 'target_id_X', 'position', 'sequences', 'ambiguous_il_sequences']]
print(output_data)
output_data.columns = ['peptide_ID', 'protein_ID', 'protein_ID_X', 'start_position', 'peptide_seq', 'J_peptide_seq']
print(output_data)
    
