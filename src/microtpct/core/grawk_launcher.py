#!/usr/bin/env python3

import subprocess
import pandas as pd 

from pathlib import Path
from io import StringIO

root_path = Path(__file__).resolve().parent.parent.parent.parent
core_path = Path(__file__).resolve().parent

query_path = str(root_path) + "/raw_data" + "/query_sequence.fa"
target_path = str(root_path) + "/raw_data" + "/uniprotkb_proteome_UP000000803_2025_11_25.fasta"


print("\nWorking on path : \n")
print(f"root_path : {root_path}")
print(f"core_path : {core_path}")
print(f"query_path : {query_path}")
print(f"target_path : {target_path}")



result = subprocess.run(
    [f"{core_path}/grawk_match.sh", query_path, target_path],
    capture_output=True,
    text=True)

grawk_results_DataFrame = pd.read_csv(StringIO(result.stdout), sep=';')

print("\ngrawk_results_DataFrame : \n")
print(grawk_results_DataFrame)


