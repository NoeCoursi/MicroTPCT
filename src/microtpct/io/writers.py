# Description : 
# This module contains functions to write the predicted true micropeptides to a CSV file
# 

# The output mipep.csv file contains the following columns:
# peptide_ID: the ID of the peptide that was created at the start
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
    # it's an object from class MatchResult


def write_outputs_to_csv(algorithm_output, algorithm_output_X , algorithm_input, file_path=None, output_file="microTPCT.csv", output_metrics="metrics.csv"):

                                        # Create micropeptides CSV file            

    # algorithm_output contains query_id = peptide_ID, target_id = protein_ID, position = start_position     
    # Convert output to dataframe
    algorithm_output = algorithm_output.to_dataframe()
    # Algorithm output for protein sequence containing X
    algorithm_output_X = algorithm_output_X.to_dataframe()
    # Rename column of protein's ID for it to be different than result without Xs
    algorithm_output_X.columns = ['query_id', 'target_id_X', 'position']

    # It's still missing peptide_seq and J_peptide_seq, so we fetch those in input files QueryDB
    # QueryDB contains : ids = peptide_ID, sequences= peptide_seq, ambiguous_il_sequences = J_peptide_seq 
    algorithm_input= algorithm_input.to_dataframe()[['ids', 'sequences', 'ambiguous_il_sequences']]

    # Merge all dataframes on peptide_ID
    algorithms = pd.merge(algorithm_output,algorithm_output_X,
                      on=['query_id','position'], how="outer",
                      suffixes=('', '_X'))
    # merge with input 
    output_data = pd.merge(algorithms,algorithm_input, 
                       left_on='query_id', right_on='ids', 
                       how="outer")
    output_data= output_data[['query_id', 'target_id', 'target_id_X', 'position', 'sequences', 'ambiguous_il_sequences']]
    output_data.columns = ['peptide_ID', 'protein_ID', 'protein_ID_X', 'start_position', 'peptide_seq', 'J_peptide_seq']



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
    (output_data[['peptide_ID', 'protein_ID',
                       'peptide_seq','J_peptide_seq',
                       'start_position']]).to_csv(output_path, index=False)
    

    
                        # Compute Metrics 

    # Total number of peptides
    # Computed by counting unique micropeptide's IDs 
    #total_peptides = len(algorithm_output['peptide_ID'])
    # Number of peptides matched to proteins
    #matched_peptides = len(algorithm_output['protein_ID'].dropna())

    # Creates a DataFrame for metrics
    #metrics_df = pd.DataFrame({
    #    "total_peptides": [total_peptides],
    #    "matched_peptides": [matched_peptides]
    #})
    

    # Creates output path for file 
    metrics_name=month_day_hour_minute+"_"+output_metrics
    metrics_path = output_dir/metrics_name

    # Write metrics to CSV
    metrics_df.to_csv(metrics_path, index=False)


    return None





