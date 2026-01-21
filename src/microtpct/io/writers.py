# Description : 
# This module contains functions to write the predicted true micropeptides to a CSV file
# 

# The output mipep.csv file contains the following columns:
# micro_peptide_ID: the ID of the peptide that was created at the start
# protein_ID: the ID of the canonical protein's peptide to which it matched
# peptide_seq: the peptidic sequence of the micropeptide
# J_peptide_seq: the peptidic sequence of the micropeptide with Isoleucine instead of Leucine
# start_position : the starting position of the peptide in the protein sequence it matched with

import csv
import pandas as pd
from pathlib import Path
import microtpct
from datetime import datetime

# algorithm_output is the output from the algorithm/alignment module
    # définir l'algorithme_output, mais surement il sera 
    # créé à un moment dans le script pipeline en appelant 
    # les fonctions créées dans alignemnt/algorithme 



def write_micropeptides_to_csv(algorithm_output, file_path=None, output_file="microTPCT.csv"):
    # put it as a dataframe 
    algorithm_output = pd.DataFrame(algorithm_output)

    # If no file_path is given, use current directory
    if not file_path:
        file_path = Path.cwd()
        print(f"No file_path provided, saving file in current directory: {file_path}")

    # Get the directory of the files used as input 
    file_dir = Path(file_path).resolve().parent

    # Check if outputs folder exists, if not creates it 
    output_dir = file_dir / "outputs"
    if output_dir.exists():
        print("outputs folder already exists")
    else:
        output_dir.mkdir(parents=True)
        print("creating outputs folder")

    # Format: month_day_hour:minute_name-of-file
    month_day_hour_minute = datetime.now().strftime("%m_%d_%Hh%M")
    # creates output path for file 
    file_name=month_day_hour_minute+"_"+output_file
    output_path = output_dir/file_name 

    # write the micropeptides to a CSV file "microTPCT.csv"
    (algorithm_output[['micro_peptide_ID', 'protein_ID',
                       'peptide_seq','J_peptide_seq',
                       'start_position']]).to_csv(output_path, index=False)
    return None




# compute metrics and write them to a CSV file
def write_metrics_to_csv(algorithm_output, file_path=None, output_file="metrics.csv"):
    # Total number of peptides
    # Computed by counting unique micropeptide's IDs 
    total_peptides = len(algorithm_output['micro_peptide_ID'])
    # Number of peptides matched to proteins
    matched_peptides = len(algorithm_output['protein_ID'].dropna())

    # Creates a DataFrame for metrics
    metrics_df = pd.DataFrame({
        "total_peptides": [total_peptides],
        "matched_peptides": [matched_peptides]
    })
    
    # If no file_path is given, use current directory
    if not file_path:
        file_path = Path.cwd()
        print(f"No file_path provided, saving file in current directory: {file_path}")

    # Get the directory of the files used as input 
    file_dir = Path(file_path).resolve().parent
    output_dir = file_dir / "outputs"

    # Does not test if outputs folder exists because it was done in the previous function
    
    # Format: month_day_hour:minute
    month_day_hour_minute = datetime.now().strftime("%m_%d_%Hh%M")
    # creates output path for file 
    file_name=month_day_hour_minute+"_"+output_file
    output_path = output_dir/file_name 

    # Write metrics to CSV
    metrics_df.to_csv(output_path, index=False)
    
    return None 
