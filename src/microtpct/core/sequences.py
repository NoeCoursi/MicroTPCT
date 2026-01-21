"""
Core biological sequence models for MicroTPCT.

These classes define the canonical data structures manipulated
by the MicroTPCT pipeline. They are independent of input formats
and user interfaces.
"""

from dataclasses import dataclass, field # dataclasses allows auto-creates __init__, __repr__, etc.


# Base sequence

@dataclass(frozen=True) # Frozen to prevent sequence modification (~ read only)
class Sequence:
    """
    Generic biological sequence.

    This class should not be instantiated directly for user inputs.
    """
    id: str
    sequence: str = field(repr=False) # Avoid printing sequence when object is called

    def __post_init__(self):
        if not self.id:
            raise ValueError("Sequence id cannot be empty.")
        
        if not self.sequence:
            raise ValueError("Sequence cannot be empty.")


# Protein / peptide

@dataclass(frozen=True)
class ProteinSequence(Sequence):
    """
    Protein sequence.
    """
    accession: str

    def __post_init__(self):
        super().__post_init__()

        if not self.accession:
            raise ValueError("Protein accession cannot be empty.")
    
    @property # Compute sequence length
    def length(self) -> int: 
        return len(self.sequence)


@dataclass(frozen=True)
class PeptideSequence(ProteinSequence):
    """
    Peptide sequence.
    """
    pass
