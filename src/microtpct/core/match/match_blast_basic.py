import subprocess
import tempfile
import os
import shutil as sh
from typing import List, Tuple, Literal, Dict
from pathlib import Path

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult

### bash commands makeblastdb and blastp must be installed and on PATH
# sudo apt update
# sudo apt install ncbi-blast+


def peptides_to_fasta(peptides: List[str], ids: List[str], out_path: str) -> None:
    """Write peptide sequences to FASTA using provided IDs as headers.

    Args:
        peptides: list of peptide sequences
        ids: list of corresponding peptide IDs (must have same length)
        out_path: path to output FASTA file
    """
    if len(peptides) != len(ids):
        raise ValueError("peptides and ids must have the same length")

    with open(out_path, "w") as qf:
        for pid, pep in zip(ids, peptides):
            #replace J I and L with ONLY L in the sequences before writing to fasta
            pep = pep.replace("J", "L").replace("I", "L")
            qf.write(f">{pid}\n{pep}\n")


def proteins_to_fasta(proteins: List[str], ids: List[str], out_path: str) -> None:
    """Write protein sequences to FASTA using provided IDs as headers.

    Args:
        proteins: list of protein sequences
        ids: list of corresponding protein IDs
        out_path: path to output FASTA file
    """
    if len(proteins) != len(ids):
        raise ValueError("proteins and ids must have the same length")

    with open(out_path, "w") as pf:
        for tid, seq in zip(ids, proteins):
            #replace J I and L with ONLY L in the sequences before writing to fasta
            seq = seq.replace("J", "L").replace("I", "L")
            pf.write(f">{tid}\n{seq}\n")


def make_blast_db(proteome_file: str | Path, db_prefix: str) -> str:
    """Create a BLAST protein database from `proteome_file` with given prefix.
    Raises RuntimeError on failure with `makeblastdb` stderr attached.
    """
    if not os.path.exists(proteome_file):
        raise RuntimeError(f"proteome file not found: {proteome_file}")
    if os.path.getsize(proteome_file) == 0:
        raise RuntimeError(f"proteome file is empty: {proteome_file}")

    cmd_make = ["makeblastdb", "-in", proteome_file, "-dbtype", "prot", "-out", db_prefix]
    proc = subprocess.run(cmd_make, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        # Try to include a short snippet of the proteome file to help debugging
        try:
            with open(proteome_file, "r") as fh:
                snippet = "".join(fh.readlines()[:5])
        except Exception as e:
            snippet = f"<could not read proteome file: {e}>"
        raise RuntimeError(
            f"makeblastdb failed (rc={proc.returncode}): {proc.stderr.strip()}\n"
        )

    return db_prefix


def parse_blast_output(blast_out: str) -> List[Match]:
    """Parse BLAST tabular output and return a list of `Match` objects.

    Only accept exact full-length matches (100% identity, 0 mismatches,
    alignment length == peptide length).
    """
    matches: List[Match] = []
    for line in blast_out.splitlines():
        if not line:
            continue
        qseqid, sseqid, pident, alen, mismatch, sstart, send = line.split()
        try:
            if float(pident) != 100.0:
                continue
        except ValueError:
            continue
        if int(mismatch) != 0:
            continue
        # alignment length check will be done by comparing to BLAST reported length
        if int(alen) < 1:
            continue

        sstart_i = int(sstart) - 1
        send_i = int(send) - 1
        start0 = min(sstart_i, send_i)

        matches.append(Match(query_id=qseqid, target_id=sseqid, position=start0))

    return matches


# Use local BLAST+ (makeblastdb + blastp) to find exact peptide matches in proteins.
def run_blast_basic(target_db: TargetDB, query_db: QueryDB) -> MatchResult:
    """Run local BLAST (makeblastdb + blastp) using `target_db` and `query_db`.

    The function writes temporary FASTA files for targets and queries, builds
    a BLAST protein database from the targets, runs `blastp` and returns a
    `MatchResult` with exact full-length matches.
    """
    # Ensure BLAST+ binaries are available
    if sh.which("makeblastdb") is None or sh.which("blastp") is None:
        raise RuntimeError("makeblastdb and blastp must be installed and on PATH")

    tmpdir = tempfile.mkdtemp(prefix="blast_tmp_")
    try:
        targets_fa = os.path.join(tmpdir, "proteome.fasta")
        proteins_to_fasta(target_db.ambiguous_il_sequences, target_db.ids, targets_fa)

        queries_fa = os.path.join(tmpdir, "peptides.fasta")
        peptides_to_fasta(query_db.ambiguous_il_sequences, query_db.ids, queries_fa)

        # Debug: print quick stats and first lines of the generated FASTA files
        for path in (targets_fa, queries_fa):
            try:
                exists = os.path.exists(path)
                size = os.path.getsize(path) if exists else -1
                with open(path, "r") as fh:
                    sample = "".join(fh.readlines()[:5])
            except Exception as e:
                exists = False
                size = -1
                sample = f"<could not read file: {e}>"

        db_prefix = os.path.join(tmpdir, "prot_db")
        make_blast_db(targets_fa, db_prefix)

        outfmt = "6 qseqid sseqid pident length mismatch sstart send"
        cmd_blast = [
            "blastp",
            "-query", queries_fa,
            "-db", db_prefix,
            "-task", "blastp-short",
            "-outfmt", outfmt,
            "-max_target_seqs", "100000",
        ]

        proc = subprocess.run(cmd_blast, check=False, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"blastp failed with return code {proc.returncode}: {proc.stderr}")

        blast_out = proc.stdout

        matches = parse_blast_output(blast_out)
        return MatchResult(matches)
    finally:
        sh.rmtree(tmpdir)

