import re
from datetime import datetime
from pathlib import Path
from typing import Literal
import pandas as pd

from microtpct.core.databases import QueryDB, TargetDB
from microtpct.core.results import MatchResult


PathLike = str | Path

def _sanitize_name(name: str) -> str:

    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_\-]", "", name)

    return name

def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")



def build_matching_result_table(query_db: QueryDB, result_strict: MatchResult, result_wildcard: MatchResult | None = None):
    """
    Build the final matching result table for MicroTPCT.

    Each row corresponds to exactly one of:
        - one strict match
        - one wildcard match
        - no match at all

    Strict and wildcard matches never appear on the same row.

    Output columns:
        - all columns from query_db
        - strict_matching_target_id
        - strict_matching_position
        - wildcard_matching_target_id
        - wildcard_matching_position
        - matching_type  (strict / wildcard / None)
    """

    # Get query (peptides) dataframe 
    df_query = query_db.to_dataframe()

    # Prepare base (queries without any match)
    base = df_query.copy()
    base["strict_matching_target_id"] = None
    base["strict_matching_position"] = None
    base["wildcard_matching_target_id"] = None
    base["wildcard_matching_position"] = None
    base["matching_type"] = None

    # Strict match
    df_strict = result_strict.to_dataframe().rename(columns={
        "query_id": "id",
        "target_id": "strict_matching_target_id",
        "position": "strict_matching_position"
    })
    
    # Join with query to recover query metadata
    df_strict = df_query.merge(df_strict, on="id", how="inner")

    # Add empty wildcard columns
    df_strict["wildcard_matching_target_id"] = None
    df_strict["wildcard_matching_position"] = None
    df_strict["matching_type"] = "strict"

    # Wildcards match
    df_wildcard = None # Initialisation required for later merge
    if result_wildcard is not None:
        df_wildcard = result_wildcard.to_dataframe().rename(columns={
            "query_id": "id",
            "target_id": "wildcard_matching_target_id",
            "position": "wildcard_matching_position"
        })

        # Join with query to recover query metadata
        df_wildcard = df_query.merge(df_wildcard, on="id", how="inner")

        # Add empty strict columns
        df_wildcard["strict_matching_target_id"] = None
        df_wildcard["strict_matching_position"] = None
        df_wildcard["matching_type"] = "wildcard"

    # Queries with no match att all
    matched_ids = set(df_strict["id"].unique())

    if df_wildcard is not None:
        matched_ids.update(df_wildcard["id"].unique())

    df_nomatch = base[~base["id"].isin(matched_ids)]

    # Final union
    result = [df_nomatch, df_strict]

    if result is not None:
        result.append(df_wildcard)

    df_result = (
        pd.concat(result, ignore_index=True)
          .sort_values("id")
          .reset_index(drop=True)
    )

    return df_result



def write_outputs(
    output_path: PathLike,
    output_format: Literal["csv", "excel"],
    query_db: QueryDB,
    target_db: TargetDB,
    result_strict: MatchResult,
    result_wildcard: MatchResult | None = None,
    analysis_name: str | None = None,
):
    
    # Generate name
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    if analysis_name:
        analysis = _sanitize_name(analysis_name)

    ts = _timestamp() # Get a common timestamp for both output files

    ext = "csv" if output_format == "csv" else "xlsx"

    result_file = Path(output_path, f"microtpct_matching_result{f"_{analysis}" if analysis_name else ""}_{ts}.{ext}")
    stats_file  = Path(output_path, f"microtpct_statistics{f"_{analysis}" if analysis_name else ""}_{ts}.{ext}")
    
    df_result = build_matching_result_table(query_db, result_strict, result_wildcard)

    print(df_result)






def write_outputs_to_csv(algorithm_output, algorithm_output_X , algorithm_input, file_path=None, output_file="microTPCT.csv", output_metrics="metrics.csv"):

                                                # Compute Metrics 
    # Need to compute metrics first before converting algorithm output to dataframe instead of object from class MatchResult

    # Indexing helpers defined in class MatchResult used here: 
    # by_query(self) Group matches by query (peptide) ID
    # by_target(self) Group matches by target (protein) ID
    
    # Analysis helpers defined in class MatchResult used here:
    # matches_for_query
    # n_matches_for_query
    # peptides_with_no_match
    # n_unique_queries
    # n_unique_targets
    
    # Compute metrics with the above helpers
    total_peptides = algorithm_input.size
    matched_peptides = algorithm_output.n_unique_queries()
    unmatched_peptides = len(algorithm_output.peptides_with_no_match(algorithm_input.ids))
    unique_proteins_matched = algorithm_output.n_unique_targets()
    avg_proteins_per_peptide = ((total_peptides - unmatched_peptides) / matched_peptides) if matched_peptides > 0 else 0


                                        # Create micropeptides CSV file            

    # algorithm_output contains query_id = peptide_ID, target_id = protein_ID, position = start_position     
    # Convert output to dataframe
    algorithm_output = algorithm_output.to_dataframe()
    # Algorithm output for protein sequence containing X
    algorithm_output_X = algorithm_output_X.to_dataframe()
    # Rename column of protein's ID for it to be different than result without Xs
    algorithm_output_X.columns = ['query_id', 'target_id_X', 'position']

    # It's still missing peptide_seq and J_peptide_seq, so we fetch those in input files QueryDB
    # QueryDB contains : id = peptide_ID, sequence= peptide_seq, ambiguous_il_sequence = J_peptide_seq 
    algorithm_input= algorithm_input.to_dataframe()[['id', 'sequence', 'ambiguous_il_sequence']]

    # Merge all dataframes on peptide_ID
    algorithms = pd.merge(algorithm_output,algorithm_output_X,
                      on=['query_id','position'], how="outer",
                      suffixes=('', '_X'))
    # merge with input 
    output_data = pd.merge(algorithm_input,algorithms, 
                       left_on='id', right_on='query_id', 
                       how="outer")
    output_data= output_data[['id', 'target_id', 'target_id_X', 'position', 'sequence', 'ambiguous_il_sequence']]
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
    (output_data).to_csv(output_path, index=False)
    




    # Create a DataFrame to hold the metrics
    metrics_df = pd.DataFrame({
        'Total_Peptides': [total_peptides],
        'Matched_Peptides': [matched_peptides],
        'Unmatched_Peptides': [unmatched_peptides],
        'Unique_Proteins_Matched': [unique_proteins_matched],
        'Avg_Proteins_Per_Peptide': [avg_proteins_per_peptide]
    })

    # Creates output path for file 
    metrics_name=month_day_hour_minute+"_"+output_metrics
    metrics_path = output_dir/metrics_name

    # Write metrics to CSV
    metrics_df.to_csv(metrics_path, index=False)


    return None





