from typing import Iterable
from microtpct.io.schema import ProteinInput
from microtpct.io.readers import SequenceRole

def run_flagwc(
        inputs: ProteinInput,
        wildcards: set,
        role: SequenceRole = SequenceRole.PROTEIN,
        ):
    """
    Convert validated SequenceInput objects into SequenceInput with wildcard flag.
    Take ProteinInput as input and flag them completing 'wildcard_positions' field

    Inputs
    - inputs: Iterable of ProteinInput objects
    - wildcards: str or list of wildcard characters to check for
    - role: SequenceRole.PROTEIN or SequenceRole.PEPTIDE

    Return the sames ProteinInput objects with 'wildcard_positions' field completed
    """
    flagged_sequences = []
    for obj in inputs:
        if role == SequenceRole.PROTEIN:
            if type(obj) is not ProteinInput:
                raise TypeError(
                    f"run_flagwc() expects ProteinInput, got {type(obj).__name__}"
                )
        else:
            raise ValueError(f"Unknown SequenceRole: {role}")
        # If wildcards is a list, transform it into a set for faster lookup
        wildcard_set = wildcards
        positions = [i for i, aa in enumerate(obj.sequence) if aa in wildcard_set]
        # Create a new ProteinInput with updated wildcard_positions
        flagged_obj = ProteinInput(
            accession=obj.accession,
            sequence=obj.sequence,
            wildcard_positions=positions
        )
        flagged_sequences.append(flagged_obj)
    return flagged_sequences
