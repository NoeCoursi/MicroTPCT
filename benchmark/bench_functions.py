"""
Functions to benchmark
Put this script in the benchmark folder
"""
# Necessary packages
import ahocorasick
from ahocorasick_rs import AhoCorasick
import subprocess
import tempfile
import os
import shutil as sh


# Functions to benchmark
## Aho-Corasick
def run_ahocorasick_mem(peptides, proteome):
    """
    peptides : list[str]
    proteome : list[(protein_id, sequence)]
    """
    # Build automaton
    A = ahocorasick.Automaton()
    for i, pep in enumerate(peptides):
        A.add_word(pep, (i, pep))
    A.make_automaton()
    # Prepare results dict: peptide -> list of (protein_id, position)
    results = {pep: [] for pep in peptides}

    # Scan proteome and record matches
    for protein_id, seq in proteome:
        seq = str(seq)
        for end_idx, (i, pep) in A.iter(seq):
            start = end_idx - len(pep) + 1
            results.setdefault(pep, []).append((protein_id, start))
    return results


## Aho-Corasick RS
def run_ahocorasick_rs_mem(peptides, proteome):
    """
    peptides : list[str]
    proteome : list[(protein_id, sequence)]
    """
    ac = AhoCorasick(peptides)

    results = {pep: [] for pep in peptides}

    for protein_id, seq in proteome:
        matches = ac.find_matches_as_indexes(seq, overlapping=True)
        for pat_idx, start, end in matches:
            pep = peptides[pat_idx]
            results[pep].append((protein_id, start))

    return results

## Naive matching with str.find
def run_find_mem(peptides, proteome):
    """
    peptides : list[str]
    proteome : list[(protein_id, sequence)]
    """
    # Prepare results dict: peptide -> list of (protein_id, position)
    results = {pep: [] for pep in peptides}

    for protein_id, seq in proteome:
        seq = str(seq)
        for pep in peptides:
            start = 0
            while True:
                start = seq.find(pep, start)
                if start == -1:
                    break
                results.setdefault(pep, []).append((protein_id, start))
                start += 1

    return results

# Naive matching with str.find
def run_in_mem(peptides, proteome):
    """
    peptides : list[str]
    proteome : list[(protein_id, sequence)]
    """
    # Prepare results dict: peptide -> list of protein_ids where peptide occurs
    results = {pep: [] for pep in peptides}

    for protein_id, seq in proteome:
        seq = str(seq)
        for pep in peptides:
            if pep in seq:
                results.setdefault(pep, []).append(protein_id)
                
    return results


# BLAST was benchmarked separately as an external, disk-based tool.
# Its execution time reflects a full pipeline including database construction and I/O, and is therefore not directly comparable to in-memory string matching algorithms

## BLAST
def run_blast_mem(peptides, proteome_fasta_path):
    """
    peptides : list[str]
    proteome_fasta_path : str (FASTA file)
    """
    # Ensure BLAST+ binaries are available
    if sh.which("makeblastdb") is None or sh.which("blastp") is None:
        raise RuntimeError("makeblastdb and blastp must be installed and on PATH")

    # Prepare results dict: peptide -> list of (protein_id, position)
    results = {pep: [] for pep in peptides}

    # Create temporary workspace
    tmpdir = tempfile.mkdtemp(prefix="blast_tmp_")
    try:
        # Write peptide queries to a FASTA file; use numeric qids to map back
        queries_fa = os.path.join(tmpdir, "peptides.fa")
        with open(queries_fa, "w") as qf:
            for i, pep in enumerate(peptides):
                qf.write(f">{i}\n{pep}\n")
        #with open(queries_fa, "r") as qf: # debug
        #    print("Contenu de peptides.fa :", qf.read())   

        # Make blast db from proteome_file
        db_prefix = os.path.join(tmpdir, "prot_db")
        cmd_make = ["makeblastdb", "-in", proteome_fasta_path, "-dbtype", "prot", "-out", db_prefix]
        result = subprocess.run(cmd_make, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      
        # Run blastp (short-task) with tabular output including sstart/send, percent identity and alignment length
        outfmt = "6 qseqid sseqid pident length mismatch sstart send"
        cmd_blast = [
            "blastp",
            "-query", queries_fa,
            "-db", db_prefix,
            "-task", "blastp-short",
            "-outfmt", outfmt,
            "-max_target_seqs", "100000",
            # On enlève -perc_identity 100
        ]
        proc = subprocess.run(cmd_blast, check=False, capture_output=True, text=True)
        #print("blastp stdout:", proc.stdout) #debug
        #print("blastp stderr:", proc.stderr) #debug
        if proc.returncode != 0:
            raise RuntimeError(f"blastp failed with return code {proc.returncode}")

        blast_out = proc.stdout

        # Parse blast output lines
        for line in blast_out.splitlines():
            if not line:
                continue
            qseqid, sseqid, pident, alen, mismatch, sstart, send = line.split()
            pat_idx = int(qseqid)
            pep = peptides[pat_idx]
            # Only accept full-length exact matches (pident 100 and alignment length == peptide length and 0 mismatches)
            if float(pident) != 100.0:
                continue
            if int(mismatch) != 0:
                continue
            if int(alen) != len(pep):
                continue

            sstart_i = int(sstart) - 1
            send_i = int(send) - 1
            start0 = min(sstart_i, send_i)
            results.setdefault(pep, []).append((sseqid, start0))

        return results
    finally:
        sh.rmtree(tmpdir)
