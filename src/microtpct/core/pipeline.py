"""
Main computational pipeline for MicroTPCT.

This module orchestrates the full workflow:
    readers -> validators -> databases -> matching -> results

This pipeline is interface-agnostic.
"""

from pathlib import Path
from typing import List, Literal

from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.validators import validate_protein_input, validate_peptide_input, validates_wildcards
from microtpct.io.converters import build_database
from microtpct.core.databases import TargetDB


from microtpct.core.match import MATCHING_ENGINES, run_find, run_ahocorasick
from microtpct.core.match.wildcards_matcher import run_wildcard_match

from microtpct.io.writers import write_outputs
from microtpct.utils.logging import setup_logger


PathLike = str | Path

# Main pipeline entry point

def run_pipeline(
    target_file: PathLike,
    query_file: PathLike,

    *,
    target_format: str | None = None,
    query_format: str | None = None,
    target_separator: str | None = None,
    query_separator: str | None = None,

    output_path: PathLike | None = None,
    output_format: Literal["excel", "csv"] = "csv",

    analysis_name: str | None = None,
    log_file: PathLike | None = None,

    allow_wildcard: bool = True,
    wildcards: str | List[str] = "X",
    matching_engine: str = "aho",
):
    """
    Run the complete MicroTPCT pipeline.

    docstring to complete...

    """

    logger = setup_logger(__name__, log_file=log_file)

    logger.info(f"Starting MicroTPCT pipeline {f"for analysis: {analysis_name}" if analysis_name else ""}")

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
    effective_allow_wildcard = allow_wildcard # The real allow_wildcard
    if allow_wildcard and not wildcards: # Strange to allow wildcard and get empty wildcard
        logger.warning(
                    "Wildcard matching is enabled (allow_wildcard=True), but no wildcard characters were provided. "
                    "Wildcard matching will be ignored and strict matching will be applied."
                    )
        effective_allow_wildcard = False


    if wildcards: # allways test wildcards even if not allowed by user to log warning later on
        wildcards = set(wildcards) if isinstance(wildcards, list) else {wildcards}

        validates_wildcards(wildcards)

        if effective_allow_wildcard:
            logger.info(f"Wildcard character(s) {list(wildcards)} valid and enable")


    logger.info("Validating target inputs")

    # Validate protein input and return True if object contain wildcards
    n_with_wildcards = 0

    for obj in target_inputs:
        wildcards_detected = validate_protein_input(obj, wildcards)

        if wildcards_detected:
            n_with_wildcards += 1

        if effective_allow_wildcard:
            object.__setattr__(obj, "contain_wildcards", wildcards_detected)


    # Inform user about detected wildcards according to matching mode
    if n_with_wildcards > 0:

        if not effective_allow_wildcard:
            # Strict matching requested
            logger.warning(
                f"Strict matching requested (allow_wildcard=False), but {n_with_wildcards} target sequence(s) "
                f"contain wildcard character(s) ({list(wildcards)}), which may represent ambiguous amino acids. "
                "Strict matching will be applied. Use allow_wildcard=True to enable wildcard matching."
            )

        else:
            # Wildcard matching enabled
            logger.info(
                f"{n_with_wildcards} target sequence(s) contain wildcard character(s) ({list(wildcards)}). "
                "These sequences will be processed using wildcard-enabled matching as requested."
            )
    

    logger.info("Validating query inputs")
    for obj in query_inputs:
        validate_peptide_input(obj)

    logger.info("All inputs are valid")
    

    # Build databases

    logger.info("Building target database")
    target_db = build_database(target_inputs, role=SequenceRole.PROTEIN)

    if effective_allow_wildcard: # Add special attribute and method if wildcard search enable
        _inject_wildcard_metadata(target_db, target_inputs)

    logger.info("Building query database")
    query_db = build_database(query_inputs, role=SequenceRole.PEPTIDE)

    logger.info(
        f"TargetDB: {target_db.size} sequences "
        f"({target_db.n_unique_accessions()} unique accessions)"
    )
    logger.info(
        f"QueryDB: {query_db.size} peptides "
        f"({query_db.n_unique_accessions()} unique accessions)"
    )


    # Run matching engine

    # Strict matching (ignore wildcard)
    try:
        matching_func = MATCHING_ENGINES[matching_engine]
    except KeyError:
        raise ValueError(f"Unsupported matching engine: '{matching_engine}'")

    # Execute the engine
    logger.info(f"Running matching engine: {matching_engine} {"+ wildcards match" if effective_allow_wildcard else ""}")
    result_strict_matching = matching_func(target_db, query_db)

    total_n_matches = result_strict_matching.__len__() # Store number of matches

    # Wildcard matching
    if effective_allow_wildcard:
        result_wildcard_matching = run_wildcard_match(target_db.get_wildcard_targets(), # Only sequence that contain wildcards
                                                       query_db,
                                                       wildcards)
        
        total_n_matches += result_wildcard_matching.__len__()
    
    logger.info(f"Matching completed: {total_n_matches} total matches")

    # Generate output 
    if not output_path:
        output_path = Path(query_file).parent

    logger.info(f"Saving results")

    result_file, stats_file = write_outputs(
        output_path = output_path,
        output_format = output_format,
        analysis_name = analysis_name,
        query_db = query_db,
        target_db = target_db,
        result_strict = result_strict_matching,
        result_wildcard = result_wildcard_matching if effective_allow_wildcard else None,
    )
    
    logger.info(f"Results written to: {result_file}")

    # Done
    logger.info("Pipeline finished successfully")


def _inject_wildcard_metadata(target_db, target_inputs):
    contains_wildcard = [
        getattr(obj, "contain_wildcards")
        for obj in target_inputs
    ]

    object.__setattr__(target_db, "contains_wildcards", contains_wildcard)

    from types import MethodType

    def _get_wildcard_targets(self):
        indices = [i for i, has_wc in enumerate(self.contains_wildcards) if has_wc]

        return TargetDB(
            ids=[self.ids[i] for i in indices],
            sequences=[self.sequences[i] for i in indices],
            ambiguous_il_sequences=[self.ambiguous_il_sequences[i] for i in indices],
            accessions=[self.accessions[i] for i in indices],
        )

    target_db.get_wildcard_targets = MethodType(_get_wildcard_targets, target_db)



run_pipeline(
    target_file = r"C:\Users\huawei\Desktop\uniprotkb_proteome_UP000000803_2025_11_25.fasta",
    query_file = r"c:\Users\huawei\Desktop\Drosophila Microproteome Openprot 2025-10-09 all conditions_2025-11-24_1613.xlsx",
    allow_wildcard = True,
    matching_engine = "find",
    # analysis_name = "Test of MicroTPCT",
    # log_file="logs/test_pipeline.log",

    wildcards = "X"
)
