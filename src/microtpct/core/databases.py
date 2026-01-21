"""
Sequence registries for MicroTPCT.

This file provides simple in-memory databases for ProteinSequence and
PeptideSequence objects. It allows grouping, indexing, and querying
sequences by accession or other criteria.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SequenceDB:
    """
    Generic sequence database for algorithmic processing.

    Should not be manualy instancied by user.

    Attributes
    ----------
    sequences : list of str
        Biological sequences used by matching algorithms.
    accessions : list of str or None
        Optional external identifiers (accessions, peptide IDs, etc.).
        The internal algorithmic ID is always the index in the list.
    size : int
        Number of sequences in the database.
    """

    sequences: List[str]
    ambiguous_il_sequence: List[str]
    accessions: List[str]

    def __post_init__(self):
        if len(self.sequences) != len(self.accessions):
            raise ValueError(
                "sequences and accessions must have the same length "
                f"(got {len(self.sequences)} and {len(self.accessions)})"
            )

    @property
    def size(self) -> int:
        """Return the number of sequences in the database."""
        return len(self.sequences)


class TargetDB(SequenceDB):
    """
    Target protein database.

    Contains protein sequences used as matching targets.
    """
    pass


class QueryDB(SequenceDB):
    """
    Query peptide database.

    Contains peptide sequences used as matching patterns.
    """
    pass
