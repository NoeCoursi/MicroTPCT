"""
Sequence registries for MicroTPCT.

This file provides simple in-memory databases for ProteinSequence and
PeptideSequence objects. It allows grouping, indexing, and querying
sequences by accession or other criteria.

NOTE: This is a temporary solution for convenience and pipeline testing.
For very large datasets, consider switching to a pandas.DataFrame or
another storage engine for efficiency and scalability.
"""

from collections import defaultdict
from typing import List, TypeVar, Generic

from .sequences import *

# Generic type for database items
T = TypeVar("T", bound=Sequence)

class SequenceDatabase(Generic[T]):
    """
    Generic in-memory database for Sequence-derived objects.
    Provides basic storage and querying functionality.
    """

    def __init__(self):
        self._sequences: List[T] = []
        self._by_accession = defaultdict(list)

    def add(self, seq: T):
        """Add a sequence to the database."""
        self._sequences.append(seq)
        if hasattr(seq, "accession"):
            self._by_accession[seq.accession].append(seq)

    def all(self) -> List[T]:
        """Return all sequences."""
        return list(self._sequences)

    def get_by_accession(self, accession: str) -> List[T]:
        """Return all sequences with the given accession."""
        return self._by_accession.get(accession, [])

    def filter_by_length(self, min_len: int = None, max_len: int = None) -> List[T]:
        """
        Return sequences whose length is within the given bounds.
        If min_len or max_len is None, it is ignored.
        """
        result = self._sequences
        if min_len is not None:
            result = [s for s in result if len(s.sequence) >= min_len]
        if max_len is not None:
            result = [s for s in result if len(s.sequence) <= max_len]
        return result

    def count(self) -> int:
        """Return total number of sequences."""
        return len(self._sequences)


class ProteinDatabase(SequenceDatabase[ProteinSequence]):
    """Database specialized for ProteinSequence objects."""
    pass


class PeptideDatabase(SequenceDatabase[PeptideSequence]):
    """Database specialized for PeptideSequence objects."""
    
    def get_unique_accessions(self) -> List[str]:
        """Return a list of all unique protein accessions in this database."""
        return list(self._by_accession.keys())

    def get_by_motif(self, motif: str) -> List[PeptideSequence]:
        """
        Return all peptides containing the given amino acid motif.
        Simple substring search.
        """
        return [p for p in self._sequences if motif in p.sequence]
