"""
Sequence registries for MicroTPCT.

This file provides simple in-memory databases for ProteinSequence and
PeptideSequence objects. It allows grouping, indexing, and querying
sequences by accession or other criteria.
"""

from dataclasses import dataclass
from typing import List
import pandas as pd


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

    ids: List[str] # pipeline IDs (Q000001, T000001, …)
    sequences: List[str] # original sequences
    ambiguous_il_sequences: List[str] # # I/L replaced by J
    accessions: List[str]

    def __post_init__(self):
        if not (len(self.ids) == len(self.accessions) == len(self.ambiguous_il_sequences) == len(self.sequences)):
            raise ValueError("All fields must have the same length")

    @property
    def size(self) -> int:
        return len(self.sequences)

    def unique_accessions(self) -> set[str]:
        "Return a set of all uniques accessions in database."
        return {acc for acc in self.accessions if acc is not None}

    def n_unique_accessions(self) -> int:
        "Return number of uniques accessions."
        return len(self.unique_accessions())
    
    def to_dataframe(self):
        """
        Return the database as a pandas DataFrame.
        """
        return pd.DataFrame({
            "id": self.ids,
            "accession": self.accessions,
            "sequence": self.sequences,
            "ambiguous_il_sequence": self.ambiguous_il_sequences,
        })


class TargetDB(SequenceDB):
    """
    Target protein database.

    Contains protein sequences used as matching targets.
    """

    def n_targets_with_wildcards(self) -> int:
        if not hasattr(self, "contains_wildcards"):
            return 0
        return sum(self.contains_wildcards)

    def fraction_targets_with_wildcards(self) -> float:
        if self.size == 0:
            return 0.0
        return self.n_targets_with_wildcards() / self.size

    # Modify to_dataframe methode in order to incorporate eventual contain_windcards attribute in output
    def to_dataframe(self):
        # Start with parent DataFrame
        df = super().to_dataframe()

        # Inject contain_wildcard if it exists
        if hasattr(self, "contains_wildcards"):
            df["contain_wildcard"] = self.contains_wildcards

        return df


class QueryDB(SequenceDB):
    """
    Query peptide database.

    Contains peptide sequences used as matching patterns.
    """
    pass