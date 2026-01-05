"""
Conversion utilities for MicroTPCT.

This module converts validated input schemas into
clean core biological sequence objects.
"""

from microtpct.io.schema import ProteinInput, PeptideInput
from microtpct.core.sequences import ProteinSequence, PeptideSequence


def protein_input_to_core(prot: ProteinInput) -> ProteinSequence:
    """
    Convert a validated ProteinInput into a core ProteinSequence.
    """
    if type(prot) is not ProteinInput:
        raise TypeError(
            f"protein_input_to_core() expects ProteinInput, got {type(prot).__name__}"
        )

    return ProteinSequence(
        id=prot.id.strip(),
        accession=prot.accession.strip(),
        sequence=prot.sequence.upper().strip(),
    )


def peptide_input_to_core(pep: PeptideInput) -> PeptideSequence:
    """
    Convert a validated PeptideInput into a core PeptideSequence.
    """
    if type(pep) is not PeptideInput:
        raise TypeError(
            f"peptide_input_to_core() expects PeptideInput, got {type(pep).__name__}"
        )

    return PeptideSequence(
        id=pep.id.strip(),
        accession=pep.accession.strip(),
        sequence=pep.sequence.upper().strip(),
    )
