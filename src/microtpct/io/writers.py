# Description : 
# This module contains functions to write the predicted true micropeptides to a CSV file
# 

# The output mipep.csv file contains the following columns:
# peptide_ID: the ID of the peptide that was created at the start
# peptide_seq: the peptidic sequence of the micropeptide

# The output matched_peptides.csv file contains the following columns:
# peptide_ID: the ID of the peptide that was created at the start
# peptide_seq: the peptidic sequence of the micropeptide
# protein_ID : the ID of the protein in which the peptide was found
# start_position : the starting position of the peptide in the protein sequence it matched with

# ? idée : similar_peptides: number of similar peptides found in the proteome (longuer ones with complete overlap)

import csv
import pandas as pd


# algorithm_output is the output from the algorithm/alignment module
    # définir l'algorithme_output, mais surement il sera 
    # créé à un moment dans le script pipeline en appelant 
    # les fonctions créées dans alignemnt/algorithme 


# put it as a dataframe 
algorithm_output = pd.DataFrame(algorithm_output)
# write the micropeptides to a CSV file
(algorithm_output[['peptide_ID', 'peptide_seq']]).to_csv(mipep.csv)
# write the peptides that matched proteins to a CSV file
(algorithm_output[['peptide_ID', 'peptide_seq',
                   'protein_ID','start_position']]).to_csv(matched_peptides.csv)

