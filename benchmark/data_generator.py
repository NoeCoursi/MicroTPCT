import random
from typing import List, Optional, Tuple

from microtpct.io.schema import ProteinInput, PeptideInput
from microtpct.io.converters import build_database
from microtpct.io.readers import SequenceRole
from microtpct.core.results import Match, MatchResult


# Alphabet utilities
AA_ALPHABET = "GPAVLIMCFYWHKRQNEDST"  # standard without X


def random_sequence(length: int, rng: random.Random) -> str:
    return "".join(rng.choices(AA_ALPHABET, k=length))


def inject_X(sequence: str, x_rate: float, rng: random.Random) -> str:
    """
    Randomly replace amino acids by X with probability x_rate.
    """
    seq = list(sequence)
    for i in range(len(seq)):
        if rng.random() < x_rate:
            seq[i] = "X"
    return "".join(seq)


def replace_X(sequence: str, rng: random.Random) -> str:
    """
    Replace all X by random amino acids (used for peptides).
    """
    return "".join(
        rng.choice(AA_ALPHABET) if aa == "X" else aa
        for aa in sequence
    )


# Proteome generation

def generate_proteome(
    n_proteins: int,
    mean_length: float,
    std_length: float,
    x_rate: float,
    seed: Optional[int] = None,
) -> List[ProteinInput]:

    rng = random.Random(seed)
    proteins: List[ProteinInput] = []

    for i in range(n_proteins):
        length = max(1, int(rng.gauss(mean_length, std_length)))
        seq = random_sequence(length, rng)
        seq = inject_X(seq, x_rate, rng)

        proteins.append(
            ProteinInput(
                accession=f"P{i+1:06d}",
                sequence=seq,
            )
        )

    return proteins


def duplicate_proteins_with_mutations(
    proteins: List[ProteinInput],
    redundancy_rate: float,
    mutation_rate: float,
    rng: random.Random,
) -> List[ProteinInput]:
    """
    Duplicate a fraction of proteins and introduce point mutations.
    """

    new_proteins = list(proteins)
    n_dup = int(len(proteins) * redundancy_rate)

    for i in range(n_dup):
        original = rng.choice(proteins)
        seq = list(original.sequence)

        # introduce mutations
        for j in range(len(seq)):
            if seq[j] != "X" and rng.random() < mutation_rate:
                seq[j] = rng.choice(AA_ALPHABET)

        new_seq = "".join(seq)

        new_proteins.append(
            ProteinInput(
                accession=f"{original.accession}_DUP{i+1}",
                sequence=new_seq,
            )
        )

    return new_proteins

# Peptide generation (match)

def extract_matching_peptides(
    proteins: List[ProteinInput],
    n_peptides: int,
    mean_length: float,
    std_length: float,
    rng: random.Random,
) -> Tuple[List[PeptideInput], List[Tuple[int, int, int]]]:
    """
    Returns peptides + raw ground-truth tuples:
    (peptide_index, protein_index, position)
    """

    peptides: List[PeptideInput] = []
    ground_truth: List[Tuple[int, int, int]] = []

    for i in range(n_peptides):
        prot_idx = rng.randrange(len(proteins))
        prot = proteins[prot_idx]
        prot_seq = prot.sequence

        pep_len = max(1, int(rng.gauss(mean_length, std_length)))
        pep_len = min(pep_len, len(prot_seq))

        start = rng.randint(0, len(prot_seq) - pep_len)
        pep = prot_seq[start:start + pep_len]

        pep = replace_X(pep, rng)

        peptides.append(
            PeptideInput(
                accession=f"PEP_MATCH_{i+1:06d}",
                sequence=pep,
            )
        )

        # ground truth (indices for now)
        ground_truth.append((i, prot_idx, start))

    return peptides, ground_truth


# Peptide generation (quasi-match)

def mutate_peptide_once(peptide: str, rng: random.Random) -> str:
    pos = rng.randrange(len(peptide))
    new_aa = rng.choice([aa for aa in AA_ALPHABET if aa != peptide[pos]])
    return peptide[:pos] + new_aa + peptide[pos+1:]


def generate_quasi_matching_peptides(
    proteins: List[ProteinInput],
    n_peptides: int,
    mean_length: float,
    std_length: float,
    rng: random.Random,
) -> List[PeptideInput]:

    peptides: List[PeptideInput] = []

    for i in range(n_peptides):
        prot = rng.choice(proteins)
        seq = prot.sequence

        pep_len = max(1, int(rng.gauss(mean_length, std_length)))
        pep_len = min(pep_len, len(seq))

        start = rng.randint(0, len(seq) - pep_len)
        pep = seq[start:start + pep_len]

        pep = replace_X(pep, rng)
        pep = mutate_peptide_once(pep, rng)   # one mismatch

        peptides.append(
            PeptideInput(
                accession=f"PEP_QUASI_{i+1:06d}",
                sequence=pep,
            )
        )

    return peptides



# Peptide generation (non match)

def generate_non_matching_peptides(
    proteome_sequences: List[str],
    n_peptides: int,
    mean_length: float,
    std_length: float,
    rng: random.Random,
    max_trials: int = 1000,
) -> List[PeptideInput]:

    peptides: List[PeptideInput] = []

    for i in range(n_peptides):
        for _ in range(max_trials):
            pep_len = max(1, int(rng.gauss(mean_length, std_length)))
            pep = random_sequence(pep_len, rng)

            # Ensure peptide does not appear in any protein
            if not any(pep in prot for prot in proteome_sequences):
                peptides.append(
                    PeptideInput(
                        accession=f"PEP_RANDOM_{i+1:06d}",
                        sequence=pep,
                    )
                )
                break
        else:
            raise RuntimeError("Failed to generate non-matching peptide after many trials")

    return peptides



# Main public API

def generate_benchmark_databases(
    # Proteome params
    n_proteins: int,
    protein_mean_length: float,
    protein_std_length: float,
    x_rate: float,

    # Peptide params
    n_peptides: int,
    peptide_mean_length: float,
    peptide_std_length: float,

    # Proteome default set params
    redundancy_rate: float = 0.0,
    mutation_rate: float = 0.0,

    # Peptide default set params
    match_fraction: float = 0.5,
    quasi_fraction: float = 0.0,

    # Random control
    seed: Optional[int] = None,
):
    """
    Generate synthetic TargetDB and QueryDB for MicroTPCT benchmarking.
    """

    rng = random.Random(seed)

    # Generate proteome
    proteins = generate_proteome(
        n_proteins=n_proteins,
        mean_length=protein_mean_length,
        std_length=protein_std_length,
        x_rate=x_rate,
        seed=seed,
    )

    proteins = duplicate_proteins_with_mutations(
        proteins=proteins,
        redundancy_rate=redundancy_rate,
        mutation_rate=mutation_rate,
        rng=rng,
    )

    # Split peptides
    n_match = int(n_peptides * match_fraction)
    n_quasi = int(n_peptides * quasi_fraction)
    n_nomatch = n_peptides - n_match - n_quasi

    # Generate matching peptides
    match_peptides, raw_ground_truth = extract_matching_peptides(
        proteins=proteins,
        n_peptides=n_match,
        mean_length=peptide_mean_length,
        std_length=peptide_std_length,
        rng=rng,
    )

    # Generate non-matching peptides
    proteome_sequences = [p.sequence for p in proteins]

    # Quasi-match peptides
    quasi_peptides = generate_quasi_matching_peptides(
        proteins = proteins,
        n_peptides = n_quasi,
        mean_length = peptide_mean_length,
        std_length = peptide_std_length,
        rng = rng,
    )

    nomatch_peptides = generate_non_matching_peptides(
        proteome_sequences=proteome_sequences,
        n_peptides=n_nomatch,
        mean_length=peptide_mean_length,
        std_length=peptide_std_length,
        rng=rng,
    )

    all_peptides = match_peptides + quasi_peptides + nomatch_peptides
    rng.shuffle(all_peptides)

    # Build TargetDB and QueryDB using your pipeline
    target_db = build_database(proteins, SequenceRole.PROTEIN)
    query_db = build_database(all_peptides, SequenceRole.PEPTIDE)


    # Build ground truth matching result
    matches: List[Match] = []

    for pep_idx, prot_idx, pos in raw_ground_truth:
        query_id = query_db.ids[pep_idx]
        target_id = target_db.ids[prot_idx]

        matches.append(
            Match(
                query_id=query_id,
                target_id=target_id,
                position=pos,
            )
        )

    ground_truth = MatchResult(matches)

    return target_db, query_db, ground_truth


if __name__ == "__main__":

    target_db, query_db, ground_truth = generate_benchmark_databases(
        n_proteins = 20,
        protein_mean_length = 20,
        protein_std_length = 3,
        x_rate = 1/100,

        n_peptides = 5,
        peptide_mean_length = 5,
        peptide_std_length = 1,
        match_fraction = 0.5,

        seed = 123,
    )

    print("=== TARGET DATABASE ===")
    print(target_db.to_dataframe())

    print("=== QUERY DATABASE ===")
    print(query_db.to_dataframe())

    print(ground_truth.matches)
