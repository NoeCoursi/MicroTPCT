"""
Validation utilities for MicroTPCT input schemas.

This module validates SequenceInput, ProteinInput and PeptideInput
objects before they are converted into core biological sequences.

It enforces data completeness, formatting rules and basic
biological constraints.
"""

from typing import Optional, List

from microtpct.io.schema import SequenceInput, ProteinInput, PeptideInput
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


# Protein validation

def validate_protein_input(prot: ProteinInput, wildcards: Optional[set] = None) -> bool:
    if type(prot) is not ProteinInput:
        raise TypeError(
            f"validate_protein_input() expects ProteinInput, got {type(prot).__name__}"
        )

    validate_sequence_input(prot)

    if not prot.accession:
        raise ValueError("ProteinInput.accession cannot be empty.")

    if not isinstance(prot.accession, str):
        raise TypeError("ProteinInput.accession must be a string.")

    # Returns True if wildcard detected, False otherwise
    return _validate_amino_acid_sequence(
        prot.sequence,
        obj_id=prot.accession,
        wildcards=wildcards,
    )


def validate_peptide_input(pep: PeptideInput) -> None:
    if type(pep) is not PeptideInput:
        raise TypeError(
            f"validate_peptide_input() expects PeptideInput, got {type(pep).__name__}"
        )

    validate_sequence_input(pep)

    if not pep.accession:
        raise ValueError("PeptideInput.accession cannot be empty.")

    if not isinstance(pep.accession, str):
        raise TypeError("PeptideInput.accession must be a string.")

    # Peptides never allow wildcards → strict validation
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
