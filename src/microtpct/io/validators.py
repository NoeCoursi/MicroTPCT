"""
Validation utilities for MicroTPCT input schemas.

This module validates SequenceInput, ProteinInput and PeptideInput
objects before they are converted into core biological sequences.

It enforces data completeness, formatting rules and basic
biological constraints.
"""

from microtpct.io.schema import *

# Biological constants 

AMINO_ACIDS = set("GPAVLIMCFYWHKRQNEDST")


# Base validation

def validate_sequence_input(seq: SequenceInput) -> None:
    """
    Validate a generic biological sequence input.
    """
    if not seq.id:
        raise ValueError("SequenceInput.id cannot be empty.")

    if not seq.sequence:
        raise ValueError("SequenceInput.sequence cannot be empty.")

    if not isinstance(seq.sequence, str):
        raise TypeError("SequenceInput.sequence must be a string.")


# Protein validation

def validate_protein_input(prot: ProteinInput) -> None:
    """
    Validate a protein input sequence.
    """
    if type(prot) is not ProteinInput:
        raise TypeError(
            f"validate_protein_input() expects a ProteinInput, got {type(prot).__name__}"
        )

    validate_sequence_input(prot)

    if not prot.accession:
        raise ValueError("ProteinInput.accession cannot be empty.")

    if not isinstance(prot.accession, str):
        raise TypeError("ProteinInput.accession must be a string.")

    validate_amino_acid_sequence(prot.sequence)


# Peptide validation

def validate_peptide_input(pep: PeptideInput) -> None:
    """
    Validate a peptide input sequence.
    """
    if type(pep) is not ProteinInput:
        raise TypeError(
            f"validate_peptide_input() expects a PeptideInput, got {type(pep).__name__}"
        )

    validate_protein_input(pep)


# Internal helpers

def validate_amino_acid_sequence(sequence: str) -> None:
    """
    Ensure sequence contains only valid amino acids.
    """
    invalid = set(sequence.upper()) - AMINO_ACIDS
    if invalid:
        raise ValueError(
            f"Invalid amino acids found: {', '.join(sorted(invalid))}"
        )
