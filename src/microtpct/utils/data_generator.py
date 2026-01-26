import random
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
import json
from pathlib import Path
import pandas as pd

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


def introduce_redundancy(
    proteins: List[ProteinInput],
    redundancy_rate: float,
    mutation_rate: float,
    rng: random.Random,
) -> List[ProteinInput]:
    """
    Replace a fraction of proteins by mutated duplicates of other proteins,
    without changing the total number of proteins.

    Duplicated proteins are renamed as:
        <PARENT_ACCESSION>_DUP_<k>
    where k is the duplication index for this parent protein.
    """

    if redundancy_rate == 0.0:
        return proteins

    n = len(proteins)
    k = int(n * redundancy_rate)

    # Indices of proteins that will be replaced by duplicates
    duplicate_indices = rng.sample(range(n), k)

    new_proteins = list(proteins)

    # Counter of how many times each parent protein has been duplicated
    dup_counter: dict[str, int] = {}

    for idx in duplicate_indices:
        # Choose a different protein as template (parent)
        parent_idx = rng.randrange(n)
        while parent_idx == idx:
            parent_idx = rng.randrange(n)

        parent = proteins[parent_idx]
        parent_acc = parent.accession

        # Update duplication counter for this parent
        dup_counter[parent_acc] = dup_counter.get(parent_acc, 0) + 1
        dup_version = dup_counter[parent_acc]

        # Mutate parent sequence
        seq = list(parent.sequence)

        for j in range(len(seq)):
            if seq[j] != "X" and rng.random() < mutation_rate:
                seq[j] = rng.choice(AA_ALPHABET)

        new_seq = "".join(seq)

        # New accession: PARENT_DUP_k
        new_acc = f"{parent_acc}_DUP_{dup_version}"

        new_proteins[idx] = ProteinInput(
            accession=new_acc,
            sequence=new_seq,
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
    ground_truth: List[Tuple[PeptideInput, int, int]] = []

    for i in range(n_peptides):
        prot_idx = rng.randrange(len(proteins))
        prot = proteins[prot_idx]
        prot_seq = prot.sequence

        pep_len = max(1, int(rng.gauss(mean_length, std_length)))
        pep_len = min(pep_len, len(prot_seq))

        start = rng.randint(0, len(prot_seq) - pep_len)
        pep_seq = prot_seq[start:start + pep_len]

        pep_seq = replace_X(pep_seq, rng)

        peptide = PeptideInput(
            accession=f"PEP_MATCH_{i+1:06d}",
            sequence=pep_seq,
        )

        peptides.append(peptide)
        ground_truth.append((peptide.accession, prot_idx, start))

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


def validate_parameters(
    *,
    # Counts
    n_proteins: int,
    n_peptides: int,

    # Length distributions
    protein_mean_length: float,
    protein_std_length: float,
    peptide_mean_length: float,
    peptide_std_length: float,

    # Rates / proportions
    x_rate: float,
    match_fraction: float,
    quasi_fraction: float,
    redundancy_rate: float,
    mutation_rate: float,
):
    """
    Validate all benchmark generation parameters.

    Ensures numerical validity and consistency of proportions.
    Raises ValueError with explicit messages if invalid.
    """

    # Basic positivity checks

    if n_proteins <= 0:
        raise ValueError("n_proteins must be > 0")

    if n_peptides <= 0:
        raise ValueError("n_peptides must be > 0")

    if protein_mean_length <= 0 or peptide_mean_length <= 0:
        raise ValueError("Mean sequence lengths must be > 0")

    if protein_std_length < 0 or peptide_std_length < 0:
        raise ValueError("Standard deviations must be >= 0")

    # Probability bounds

    probs = {
        "x_rate": x_rate,
        "match_fraction": match_fraction,
        "quasi_fraction": quasi_fraction,
        "redundancy_rate": redundancy_rate,
        "mutation_rate": mutation_rate,
    }

    for name, value in probs.items():
        if not (0.0 <= value <= 1.0):
            raise ValueError(
                f"{name} must be between 0 and 1 (got {value})"
            )

    # Consistency between proportions

    if match_fraction + quasi_fraction > 1.0:
        raise ValueError(
            "match_fraction + quasi_fraction must be <= 1.0 "
            f"(got {match_fraction + quasi_fraction})"
        )

    # Redundancy only makes sense if mutation_rate > 0 (optional strictness)
    if redundancy_rate > 0 and mutation_rate == 0:
        raise ValueError(
            "mutation_rate must be > 0 when redundancy_rate > 0 "
            "(otherwise duplicated proteins are identical)"
        )


# Display config utilities

def summarize_config(
    *,
    n_proteins: int,
    protein_mean_length: float,
    protein_std_length: float,
    x_rate: float,
    n_peptides: int,
    peptide_mean_length: float,
    peptide_std_length: float,
    redundancy_rate: float,
    mutation_rate: float,
    match_fraction: float,
    quasi_fraction: float,
    seed: Optional[int],
) -> Dict[str, Any]:
    """
    Return a reproducibility dictionary describing the benchmark configuration.
    """

    return {
        "timestamp": datetime.now().isoformat(),
        "n_proteins": n_proteins,
        "protein_mean_length": protein_mean_length,
        "protein_std_length": protein_std_length,
        "x_rate": x_rate,
        "n_peptides": n_peptides,
        "peptide_mean_length": peptide_mean_length,
        "peptide_std_length": peptide_std_length,
        "match_fraction": match_fraction,
        "quasi_fraction": quasi_fraction,
        "nomatch_fraction": 1.0 - match_fraction - quasi_fraction,
        "redundancy_rate": redundancy_rate,
        "mutation_rate": mutation_rate,
        "seed": seed,
    }


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

    # Config save
    save_config_path: Optional[str] = None,

    # Database save
    export_target_fasta_path: Optional[str] = None,
    export_query_xlsx_path: Optional[str] = None,
):
    """
    Generate synthetic TargetDB and QueryDB for MicroTPCT benchmarking.
    """

    # Validate all parameters first
    validate_parameters(
        n_proteins=n_proteins,
        n_peptides=n_peptides,
        protein_mean_length=protein_mean_length,
        protein_std_length=protein_std_length,
        peptide_mean_length=peptide_mean_length,
        peptide_std_length=peptide_std_length,
        x_rate=x_rate,
        match_fraction=match_fraction,
        quasi_fraction=quasi_fraction,
        redundancy_rate=redundancy_rate,
        mutation_rate=mutation_rate,
    )

    # Build reproducibility config
    config = summarize_config(
        n_proteins=n_proteins,
        protein_mean_length=protein_mean_length,
        protein_std_length=protein_std_length,
        x_rate=x_rate,
        n_peptides=n_peptides,
        peptide_mean_length=peptide_mean_length,
        peptide_std_length=peptide_std_length,
        redundancy_rate=redundancy_rate,
        mutation_rate=mutation_rate,
        match_fraction=match_fraction,
        quasi_fraction=quasi_fraction,
        seed=seed,
    )

    rng = random.Random(seed)

    # Generate proteome
    proteins = generate_proteome(
        n_proteins=n_proteins,
        mean_length=protein_mean_length,
        std_length=protein_std_length,
        x_rate=x_rate,
        seed=seed,
    )

    proteins = introduce_redundancy(
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

    if export_target_fasta_path:
        export_target_fasta(proteins, export_target_fasta_path)

    if export_query_xlsx_path:
        export_query_xlsx(all_peptides, export_query_xlsx_path)

    # Build TargetDB and QueryDB
    target_db = build_database(proteins, SequenceRole.PROTEIN)
    query_db = build_database(all_peptides, SequenceRole.PEPTIDE)

    gt_matches: List[Match] = []

    for t_id, t_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):
        for q_id, q_seq in zip(query_db.ids, query_db.ambiguous_il_sequences):
            start = t_seq.find(q_seq)
            if start != -1:
                gt_matches.append(Match(
                    query_id=q_id,
                    target_id=t_id,
                    position=start,
                ))

    ground_truth = MatchResult(gt_matches)

    if save_config_path:
        with open(save_config_path, "w") as f:
            json.dump(config, f, indent=2)

    return target_db, query_db, ground_truth, config


def export_target_fasta(
    proteins: List[ProteinInput],
    path: str | Path,
    prefix: str = "mtpct",
):
    """
    Export Target proteome to FASTA.

    Header format:
        >mtpct|ACCESSION
    """
    path = Path(path)

    with open(path, "w") as f:
        for prot in proteins:
            header = f">{prefix}|{prot.accession}"
            f.write(header + "\n")
            f.write(prot.sequence + "\n")


def export_query_xlsx(
    peptides: List[PeptideInput],
    path: str | Path,
):
    """
    Export Query peptides to Excel with columns:
        accession | sequence
    """
    path = Path(path)

    df = pd.DataFrame({
        "accession": [p.accession for p in peptides],
        "sequence": [p.sequence for p in peptides],
    })

    df.to_excel(path, index=False)


if __name__ == "__main__":

    target_db, query_db, ground_truth, _ = generate_benchmark_databases(
        n_proteins = 20,
        protein_mean_length = 20,
        protein_std_length = 3,
        x_rate = 1/100,

        n_peptides = 8,
        peptide_mean_length = 5,
        peptide_std_length = 1,
        match_fraction = 0.5,
        quasi_fraction = 0.2,

        redundancy_rate = 0.5,
        mutation_rate = 0.2,

        seed = 123
    )

    print("=== TARGET DATABASE ===")
    print(target_db.to_dataframe())

    print("=== QUERY DATABASE ===")
    print(query_db.to_dataframe())

    print(ground_truth.matches)
