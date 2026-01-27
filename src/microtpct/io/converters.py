"""
Conversion utilities for MicroTPCT.

This module converts validated input schemas into
clean core biological sequence databases objects.
"""
from typing import Iterable
from microtpct.core.databases import TargetDB, QueryDB
from microtpct.io.schema import TargetInput, QueryInput
from microtpct.io.readers import SequenceRole


def il_to_j(sequence: str) -> str:
    """Replace I and L by J in a protein/peptide sequence."""
    return sequence.replace("I", "J").replace("L", "J")


def generate_ids(prefix: str, n: int) -> list[str]:
    """
    Generate internal pipeline IDs.
    """
    width = max(6, len(str(n)))
    return [f"{prefix}{i+1:0{width}d}" for i in range(n)]

def build_database(
    inputs: Iterable[TargetInput | QueryInput],
    role: SequenceRole,
) -> TargetDB | QueryDB:
    """
    Convert validated SequenceInput objects into a SequenceDB.

    Returns
    -------
    TargetDB or QueryDB
    """

    sequences = []
    ambiguous = []
    accessions = []

    for obj in inputs:
        sequences.append(obj.sequence)
        ambiguous.append(il_to_j(obj.sequence))
        accessions.append(obj.accession)

    n = len(sequences)

    # Choose DB type and ID prefix
    if role == SequenceRole.TARGET:
        ids = generate_ids("T", n)
        return TargetDB(
            ids=ids,
            sequences=sequences,
            ambiguous_il_sequences=ambiguous,
            accessions=accessions,
        )

    elif role == SequenceRole.QUERY:
        ids = generate_ids("Q", n)
        return QueryDB(
            ids=ids,
            sequences=sequences,
            ambiguous_il_sequences=ambiguous,
            accessions=accessions,
        )

    else:
        raise ValueError(f"Unsupported SequenceRole: {role}")
