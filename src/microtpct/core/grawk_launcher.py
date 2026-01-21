#!/usr/bin/env python3

import subprocess, sys
import pandas as pd 

from pathlib import Path
from io import StringIO


regex = False


# Parsing
root_path = Path(__file__).resolve().parent.parent.parent.parent
core_path = Path(__file__).resolve().parent

if len(sys.argv) == 3 :
    query_path, target_path =  sys.argv[1], sys.argv[2]
else :
    #print(" No files has been given => dafault file :\n")
    query_path = str(root_path) + "/raw_data" + "/query_sequence.fa"
    target_path = str(root_path) + "/raw_data" + "/uniprotkb_proteome_UP000000803_2025_11_25.fasta"


print("\nWorking on path : \n")
print(f"root_path : {root_path}")
print(f"core_path : {core_path}")
print(f"query_path : {query_path}")
print(f"target_path : {target_path}")

# Run the grawk_match.sh script through python3
command_regex = [f"{core_path}/grawk_match.sh", "-r", query_path, target_path]
command_text  = [f"{core_path}/grawk_match.sh", query_path, target_path]


# Run script
if regex == True:
    command = command_regex
    print(f"\nRunning on REGEX")
else : 
    command = command_text
    print(f"\nRunning on TEXT search")


result = subprocess.run(
    command_regex,
    capture_output=True,
    text=True)


grawk_results_DataFrame = pd.read_csv(StringIO(result.stdout), sep=';')
print(grawk_results_DataFrame)
