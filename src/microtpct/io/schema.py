"""
Input data schemas for MicroTPCT.

This module defines lightweight data contracts for protein and peptide
inputs. These objects represent normalized inputs BEFORE conversion
to core Sequence objects.

NOTE: May be redundant with core/sequence.py... Should maybe considere
deleting later on.

Validation and biological rules are handled in io/validators.py.
"""

from dataclasses import dataclass, field # dataclasses allows auto-creates __init__, __repr__, etc.


@dataclass(frozen=True) # Frozen to prevent sequence modification (~ read only)
class SequenceInput:
    """
    Generic input biological sequence.

    This class should not be instantiated directly for user inputs.
    """
    id: str
    sequence: str = field(repr=False)  # Avoid printing sequence when object is called


@dataclass(frozen=True) # Frozen to prevent sequence modification (~ read only)
class ProteinInput(SequenceInput):
    """Contract for a protein input."""
    
    accession: str


@dataclass(frozen=True)
class PeptideInput(ProteinInput):
    """Contract for a peptide input."""
    
    pass
