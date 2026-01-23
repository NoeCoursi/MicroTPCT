import subprocess
import tempfile
import os
import shutil as sh
from typing import List

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import Match, MatchResult

### bash commands makeblastdb and blastp must be installed and on PATH
# sudo apt update
# sudo apt install ncbi-blast+


def peptides_to_fasta(peptides: List[str], ids: List[str], out_path: str):
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
            # replace J I and L with ONLY L in the sequences before writing to fasta
            pep = pep.replace("J", "L").replace("I", "L")
            qf.write(f">{pid}\n{pep}\n")


def proteins_to_fasta(proteins: List[str], ids: List[str], out_path: str):
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
            # replace J I and L with ONLY L in the sequences before writing to fasta
            seq = seq.replace("J", "L").replace("I", "L")
            pf.write(f">{tid}\n{seq}\n")


def make_blast_db(proteome_file, db_prefix):
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

        # print file path to debug
        raise RuntimeError(
            f"makeblastdb failed (rc={proc.returncode}): {proc.stderr.strip()}\n"
            f"Proteome file path: {proteome_file}\n"
            f"--- start of {proteome_file} (first 5 lines) ---\n{snippet}\n"
            f"--- end of snippet ---"
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
        # skip BLAST comment/header lines
        if line.startswith("#"):
            continue
        qseqid, sseqid, pident, alen, mismatch, gapopen, qlen, sstart, send = line.split()
        #pat_idx = int(qseqid)
        #pep = peptides[pat_idx]
        # Only accept full-length exact matches (pident 100 and alignment length == peptide length and 0 mismatches and 0 gap)
        try:
            if float(pident) != 100.0:
                continue
        except ValueError:
            if int(mismatch) != 0:
                continue
            if int(gapopen) != 0:
                continue
            if int(alen) != int(qlen):
                continue
        
        sstart_i = int(sstart) - 1
        send_i = int(send) - 1
        start0 = min(sstart_i, send_i)
        
        matches.append(Match(query_id=qseqid, target_id=sseqid, position=start0))

    return matches


# Use local BLAST+ (makeblastdb + blastp) to find exact peptide matches in proteins.
def run_blast(target_db: TargetDB, query_db: QueryDB) -> MatchResult:
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

        db_prefix = os.path.join(tmpdir, "prot_db")
        make_blast_db(targets_fa, db_prefix)

        outfmt = "6 qseqid sseqid pident length mismatch gapopen qlen sstart send"
        cmd_blast = [
            "blastp", # blast program
            "-query", queries_fa, # peptide queries
            "-db", db_prefix, # use the created db
            "-task", "blastp-short", # optimized for short sequences
            "-seg", "no", # disable low-complexity filtering to allow small peptides
            "-comp_based_stats", "0", # disable compositional adjustments
            "-soft_masking", "false", # disable soft masking
            "-outfmt", outfmt, # tabular output with selected fields
            "-max_target_seqs", "1000000000", # very high limit to get all valid alignments
            "-max_hsps", "1000000", # high limit to get all valid alignments
            "-word_size", "2", # small word size for short peptides
            "-use_sw_tback" # force use of Smith-Waterman, disable all shortcut heuristics
        ]
                
        proc = subprocess.run(cmd_blast, check=False, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"blastp failed with return code {proc.returncode}: {proc.stderr}")

        blast_out = proc.stdout

        matches = parse_blast_output(blast_out)
        return MatchResult(matches)
    finally:
        sh.rmtree(tmpdir)
