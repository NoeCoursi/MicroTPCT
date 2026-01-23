"""
Main computational pipeline for MicroTPCT.

This module orchestrates the full workflow:
    readers -> validators -> databases -> matching -> results

This pipeline is interface-agnostic.
"""

from pathlib import Path
from typing import Optional, List

from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.validators import validate_protein_input, validate_peptide_input, validates_wildcards
from microtpct.io.converters import build_database
# from microtpct.core.match import match_ahocorasick
# from microtpct.core.match_engines import MATCHING_ENGINES, list_available_engines
from microtpct.core.results import MatchResult
from microtpct.utils.logging import setup_logger


# Main pipeline entry point

def run_pipeline(
    target_file: str | Path,
    query_file: str | Path,
    target_format: Optional[str] = None,
    query_format: Optional[str] = None,
    target_separator: Optional[str] = None,
    query_separator: Optional[str] = None,
    log_file: Optional[str | Path] = None,

    *,
    allow_wildcard: bool = True,
    wildcards: str | List[str] = "X",
    matching_engine: str = "aho",
):
    """
    Run the complete MicroTPCT pipeline.

    docstring to complete...

    """

    logger = setup_logger(__name__, log_file=log_file)

    logger.info("Starting MicroTPCT pipeline")

    # Read inputs
    logger.info(f"Reading target file: {target_file}")
    target_inputs = list(
        read_file(target_file, role=SequenceRole.PROTEIN, format=target_format) #, sep=target_separator) + colomn
    )

    logger.info(f"Reading query file: {query_file}")
    query_inputs = list(
        read_file(query_file, role=SequenceRole.PEPTIDE, format=query_format)#, sep=query_separator)
    )

    logger.info(f"Loaded {len(target_inputs)} target sequences")
    logger.info(f"Loaded {len(query_inputs)} query peptides")

    # Validate inputs
    if allow_wildcard and not wildcards: # Strange to allow wildcard and get empty wildcard
        logger.warning(
                    "Wildcard matching is enabled (allow_wildcard=True), but no wildcard characters were provided. "
                    "Wildcard matching will be ignored and strict matching will be applied."
                    )

    if wildcards: # allways test wildcards even if not allowed by user to log warning later on
        wildcards = set(wildcards) if isinstance(wildcards, List) else {wildcards}
        validates_wildcards(wildcards)
        if allow_wildcard:
            logger.info(f"Wildcard character(s) {list(wildcards)} valid and enable")

    logger.info("Validating target inputs")
    for obj in target_inputs:
        validate_protein_input(obj, wildcards)
    
    logger.info("Validating query inputs")
    for obj in query_inputs:
        validate_peptide_input(obj)

    logger.info("All inputs are valid")
    


    # # ----------------------------
    # # Step 3 — Build databases
    # # ----------------------------

    # logger.info("Building target database")
    # target_db = build_database(target_inputs, role=SequenceRole.PROTEIN)

    # logger.info("Building query database")
    # query_db = build_database(query_inputs, role=SequenceRole.PEPTIDE)

    # logger.info(
    #     f"TargetDB: {target_db.size} sequences "
    #     f"({target_db.n_unique_accessions()} unique accessions)"
    # )
    # logger.info(
    #     f"QueryDB: {query_db.size} peptides "
    #     f"({query_db.n_unique_accessions()} unique accessions)"
    # )

    # # ----------------------------
    # # Step 4 — Run matching engine
    # # ----------------------------

    # logger.info(f"Running matching engine: {matching_engine}")

    # if matching_engine == "find":
    #     result = run_find(target_db, query_db)

    # else:
    #     raise ValueError(f"Unsupported matching engine: '{matching_engine}'")

    # logger.info(f"Matching completed: {len(result)} total matches")

    # # ----------------------------
    # # Done
    # # ----------------------------

    # logger.info("Pipeline finished successfully")

    # return result


run_pipeline(
    target_file = r"C:\Users\huawei\Desktop\uniprotkb_proteome_UP000000803_2025_11_25.fasta",
    query_file = r"c:\Users\huawei\Desktop\Drosophila Microproteome Openprot 2025-10-09 all conditions_2025-11-24_1613.xlsx",
    allow_wildcard = True,

    wildcards = "X"
)