import pandas as pd
from pathlib import Path
from datetime import datetime

from microtpct.io.writers import write_micropeptides_to_csv
from microtpct.io.writers import write_metrics_to_csv


data = {
    "micro_peptide_ID": ["mp_001", "mp_002", "mp_003"],
    "protein_ID": ["prot_A", "prot_B", "prot_C"],
    "peptide_seq": ["MKTLLV", "AGPQLR", "VVKSTA"],
    "J_peptide_seq": ["MKTL-LV", "AGPQ-LR", "VVKS-TA"],
    "start_position": [12, 45, 87],
}

df = pd.DataFrame(data)
# print(df)


write_micropeptides_to_csv(df) #,file_path="C:/Users/Ambre Bordas/Desktop/COURS/Specialisation/1-Projet_bioinfo/MicroTPCT")
write_metrics_to_csv(df) #,file_path="C:/Users/Ambre Bordas/Desktop/COURS/Specialisation/1-Projet_bioinfo/MicroTPCT")

