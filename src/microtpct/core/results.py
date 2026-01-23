"""
Matching result data structures for MicroTPCT.

This module defines lightweight containers to store and analyze
peptide-to-protein matching results produced by the matching engines.
"""

from dataclasses import dataclass
import pandas as pd
from typing import Dict, List, Iterable, Set

# Match object
@dataclass(frozen=True)
class Match:
    """
    Single peptide-to-protein match.

    Attributes
    ----------
    query_id : str
        Internal pipeline ID of the peptide (e.g. Q000123).
    target_id : str
        Internal pipeline ID of the protein (e.g. T000045).
    position : int
        Start position of the match in the target sequence (0-based).
    """

    query_id: str
    target_id: str
    position: int


# Container for all matches
class MatchResult:
    """
    Container for all matching results.

    Stores a flat list of Match objects and provides convenient
    accessors for downstream analysis (grouping, counting, filtering).

    This object is independent of the matching algorithm used.
    """

    def __init__(self, matches: Iterable[Match]):
        self._matches: List[Match] = list(matches)

        # Lazy-built indexes (created on demand)
        self._by_query: Dict[str, List[Match]] | None = None
        self._by_target: Dict[str, List[Match]] | None = None


    # Basic accessors

    @property
    def matches(self) -> List[Match]:
        """Return the full list of matches."""
        return self._matches

    def __len__(self) -> int:
        """Total number of matches."""
        return len(self._matches)



    # Help to extract results at the end 

    def to_dataframe(self) -> pd.DataFrame:
        """
        Return the matching results as a pandas DataFrame.
        One row per peptide-to-protein match.
        """
        return pd.DataFrame(
            {"query_id": [m.query_id for m in self._matches],
                "target_id": [m.target_id for m in self._matches],
                "position": [m.position for m in self._matches]} )


    # Indexing helpers
    def by_query(self) -> Dict[str, List[Match]]:
        """
        Group matches by query (peptide) ID.

        Returns
        -------
        dict
            Mapping:
                query_id -> list of Match
        """
        if self._by_query is None:
            index: Dict[str, List[Match]] = {}
            for m in self._matches:
                index.setdefault(m.query_id, []).append(m)
            self._by_query = index

        return self._by_query

    def by_target(self) -> Dict[str, List[Match]]:
        """
        Group matches by target (protein) ID.

        Returns
        -------
        dict
            Mapping:
                target_id -> list of Match
        """
        if self._by_target is None:
            index: Dict[str, List[Match]] = {}
            for m in self._matches:
                index.setdefault(m.target_id, []).append(m)
            self._by_target = index

        return self._by_target

    # Analysis helpers
    def matches_for_query(self, query_id: str) -> List[Match]:
        """Return all matches for a given peptide."""
        return self.by_query().get(query_id, [])

    def matches_for_target(self, target_id: str) -> List[Match]:
        """Return all matches for a given protein."""
        return self.by_target().get(target_id, [])

    def n_matches_for_query(self, query_id: str) -> int:
        """Number of matches for a given peptide."""
        return len(self.matches_for_query(query_id))

    def unique_targets_for_query(self, query_id: str) -> Set[str]:
        """Set of unique target IDs matched by a peptide."""
        return {m.target_id for m in self.matches_for_query(query_id)}

    def n_unique_targets_for_query(self, query_id: str) -> int:
        """
        Number of distinct proteins matched by a peptide.

        This is a key quantity for proteotypicity.
        """
        return len(self.unique_targets_for_query(query_id))

    def peptides_with_no_match(self, all_query_ids: Iterable[str]) -> List[str]:
        """
        Return peptides that did not match any target.

        Parameters
        ----------
        all_query_ids : iterable of str
            All peptide IDs present in the QueryDB.

        Returns
        -------
        list of str
            Peptide IDs with zero matches.
        """
        matched = set(self.by_query().keys())
        return [qid for qid in all_query_ids if qid not in matched]

    # Global statistics
    def n_unique_queries(self) -> int:
        """Number of peptides that matched at least one protein."""
        return len(self.by_query())

    def n_unique_targets(self) -> int:
        """Number of proteins hit by at least one peptide."""
        return len(self.by_target())
