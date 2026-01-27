"""
Validation utilities for MicroTPCT input schemas.

This module validates SequenceInput, TargetInput and QueryInput
objects before they are converted into core biological sequences.

It enforces data completeness, formatting rules and basic
biological constraints.
"""

from typing import Optional, List

from microtpct.io.schema import SequenceInput, TargetInput, QueryInput
from microtpct.utils import setup_logger

# Biological constants 

AMINO_ACIDS = set("GPAVLIMCFYWHKRQNEDST") | set("OU") # Commons amino acids + rares


logger = setup_logger(__name__)


# Base validation

def validate_sequence_input(seq: SequenceInput) -> None:

    if not seq.sequence:
        raise ValueError("SequenceInput.sequence cannot be empty.")

    if not isinstance(seq.sequence, str):
        raise TypeError("SequenceInput.sequence must be a string.")


# Target validation

def validate_target_input(prot: TargetInput, wildcards: Optional[set] = None) -> bool:
    if type(prot) is not TargetInput:
        raise TypeError(
            f"validate_target_input() expects TargetInput, got {type(prot).__name__}"
        )

    validate_sequence_input(prot)

    if not prot.accession:
        raise ValueError("TargetInput.accession cannot be empty.")

    if not isinstance(prot.accession, str):
        raise TypeError("TargetInput.accession must be a string.")

    # Returns True if wildcard detected, False otherwise
    return _validate_amino_acid_sequence(
        prot.sequence,
        obj_id=prot.accession,
        wildcards=wildcards,
    )


def validate_query_input(pep: QueryInput) -> None:
    if type(pep) is not QueryInput:
        raise TypeError(
            f"validate_query_input() expects QueryInput, got {type(pep).__name__}"
        )

    validate_sequence_input(pep)

    if not pep.accession:
        raise ValueError("QueryInput.accession cannot be empty.")

    if not isinstance(pep.accession, str):
        raise TypeError("QueryInput.accession must be a string.")

    # Querys never allow wildcards → strict validation
    _validate_amino_acid_sequence(
        pep.sequence,
        obj_id=f"{pep.accession} (sequence: {pep.sequence})"
    )


def _validate_amino_acid_sequence(
    sequence: str,
    obj_id: str | None = None,
    wildcards: Optional[set] = None,
) -> bool:

    if wildcards is None:
        wildcards = set()

    invalid = set(sequence.upper()) - AMINO_ACIDS

    if invalid:
        # All invalid characters are allowed wildcards
        if invalid.issubset(wildcards):
            return True

        id_info = f" for object '{obj_id}'" if obj_id else ""
        logger.error(
            f"Invalid amino acids found{id_info}: {', '.join(sorted(invalid))}"
        )
        raise ValueError(
            f"Invalid amino acids found{id_info}: {', '.join(sorted(invalid))}"
        )

    # No wildcard, sequence is clean
    return False


def validates_wildcards(wildcards: set):
    overlapping = wildcards & AMINO_ACIDS

    if overlapping:
        logger.error(
            f"Invalid wildcard(s) found: {sorted(overlapping)} overlap with standard amino acids."
        )
        raise ValueError(
            f"Invalid wildcard(s) found: {sorted(overlapping)} overlap with standard amino acids."
        )
