"""
Main computational pipeline for MicroTPCT.

This module orchestrates the full workflow:
    readers -> validators -> databases -> matching -> results

This pipeline is interface-agnostic.
"""

from asyncio.log import logger
from pathlib import Path
from typing import Literal, List, Dict

from microtpct.io.readers import read_file, SequenceRole
from microtpct.io.validators import validate_target_input, validate_query_input, validates_wildcards
from microtpct.io.converters import build_database
from microtpct.core.databases import TargetDB


from microtpct.core.match import get_engine
from microtpct.core.match.wildcards_matcher import run_wildcard_match

from microtpct.io.writers import write_outputs
from microtpct.utils.logger import setup_logger


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
    target_columns: Dict[str, str] | None = None,
    query_columns: Dict[str, str] | None = None,

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

    logger.info(
    f"Starting MicroTPCT pipeline"
    f"{' for analysis: ' + analysis_name if analysis_name else ''}"
)

    # Read inputs
    logger.info(f"Reading target file: {target_file}")
    target_inputs = list(
        read_file(target_file, 
                  role=SequenceRole.TARGET, 
                  format=target_format, 
                  sep = target_separator,
                  columns = target_columns
                  )
    )

    logger.info(f"Reading query file: {query_file}")
    query_inputs = list(
        read_file(query_file, 
                  role=SequenceRole.QUERY, 
                  format=query_format, 
                  sep = query_separator,
                  columns = query_columns
                  )
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

    # Validate target input and return True if object contain wildcards
    n_with_wildcards = 0

    for obj in target_inputs:
        wildcards_detected = validate_target_input(obj, wildcards)

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
        validate_query_input(obj)

    logger.info("All inputs are valid")
    

    # Build databases

    logger.info("Building target database")
    target_db = build_database(target_inputs, role=SequenceRole.TARGET)

    if effective_allow_wildcard: # Add special attribute and method if wildcard search enable
        _inject_wildcard_metadata(target_db, target_inputs)

    logger.info("Building query database")
    query_db = build_database(query_inputs, role=SequenceRole.QUERY)

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
        matching_func = get_engine(matching_engine)
    except ValueError as e:
        logger.error(str(e))
        raise

    # Execute the engine
    suffix = " + wildcard match" if effective_allow_wildcard else ""
    logger.info(f"Running matching engine: {matching_engine}{suffix}")
    
    result_strict_matching = matching_func(target_db, query_db)

    total_n_matches = result_strict_matching.__len__() # Store number of matches

    # Wildcard matching
    if effective_allow_wildcard and n_with_wildcards > 0:
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
        n_target_with_wildcards = n_with_wildcards,
        matching_engine = matching_engine,
        allow_wildcard = effective_allow_wildcard,
        wildcards = wildcards if wildcards else None,
    )
    
    logger.info(f"Results written to: {result_file}")
    logger.info(f"Statistics written to: {stats_file}")

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