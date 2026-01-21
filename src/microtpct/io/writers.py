# Description : 
# This module contains functions to write the predicted true micropeptides to a CSV file
# 

# The output mipep.csv file contains the following columns:
# micro_peptide_ID: the ID of the peptide that was created at the start
# peptide_ID: the ID of the canonical protein's peptide to which it matched
# peptide_seq: the peptidic sequence of the micropeptide
# J_peptide_seq: the peptidic sequence of the micropeptide with Isoleucine instead of Leucine
# protein_ID : the ID of the canonicalprotein
# start_position : the starting position of the peptide in the protein sequence it matched with

import csv
import pandas as pd


# algorithm_output is the output from the algorithm/alignment module
    # définir l'algorithme_output, mais surement il sera 
    # créé à un moment dans le script pipeline en appelant 
    # les fonctions créées dans alignemnt/algorithme 


def write_micropeptides_to_csv(algorithm_output, output_file="microTPCT.csv"):
    # put it as a dataframe 
    algorithm_output = pd.DataFrame(algorithm_output)
    # write the micropeptides to a CSV file "microTPCT.csv"
    (algorithm_output[['micro_peptide_ID', 'peptide_ID',
                       'peptide_seq','J_peptide_seq',
                       'protein_ID', 'start_position']]).to_csv(output_file)
    return None

