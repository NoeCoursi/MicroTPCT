"""
Functions to benchmark
Put this script in the benchmark folder

Global architecture:
fn(peptides, proteome) -> results
    peptides = list[str]
    proteome = list[(protein_id, sequence)]

"""
# Necessary packages
import subprocess
import tempfile
import os
import shutil as sh
import pandas as pd
from pathlib import Path
from multiprocessing import Pool, cpu_count

import ahocorasick
from ahocorasick_rs import AhoCorasick
import pybmoore
from Bio import SeqIO
from io import StringIO


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


# Boyer-Moore
SEPARATOR = "#"
BIG_TEXT = None
POS_TO_TARGET = None

# --- fonctions nécessaires pour le Boyer-Moore parallèle ---
def build_big_text(target_fasta):
    big_chunks = []
    pos_map = []
    current_pos = 0
    for rec in SeqIO.parse(target_fasta, "fasta"):
        seq = str(rec.seq)
        big_chunks.append(seq)
        pos_map.append((current_pos, current_pos + len(seq), rec.id))
        current_pos += len(seq)
        big_chunks.append(SEPARATOR)
        current_pos += len(SEPARATOR)
    return "".join(big_chunks), pos_map

def init_worker(big_text, pos_map):
    global BIG_TEXT, POS_TO_TARGET
    BIG_TEXT = big_text
    POS_TO_TARGET = pos_map

def locate_target(global_pos):
    for start, end, tid in POS_TO_TARGET:
        if start <= global_pos < end:
            return tid, global_pos - start
    return None, None

def process_query(query):
    qrec_id, qseq = query
    hits = []
    matches = pybmoore.search(qseq, BIG_TEXT)
    for start, _ in matches:
        tid, local_pos = locate_target(start)
        if tid is not None:
            hits.append((tid, local_pos))
    return qrec_id, hits

# --- fonction à benchmarker ---
def run_boyermoore_parallel_mem(queries, target_fasta):
    """
    queries : list[(query_id, query_sequence)]
    target_fasta : str (path to fasta)

    Returns:
        dict: query_id -> list[(target_id, local_pos)]
    """
    big_text, pos_map = build_big_text(target_fasta)

    with Pool(
        processes=cpu_count(),
        initializer=init_worker,
        initargs=(big_text, pos_map),
    ) as pool:
        results = pool.map(process_query, queries)

    return dict(results)

# Grawk 
def run_grawk_mem2(peptides, proteome):
    """
    peptides : list[str]
    proteome : list[(protein_id, sequence)]
    """

    import subprocess
    import tempfile
    from pathlib import Path

    # 1️⃣ écrire peptides -> FASTA temporaire
    with tempfile.NamedTemporaryFile(mode="w", suffix=".fa", delete=False) as qf:
        for i, pep in enumerate(peptides):
            qf.write(f">{i}\n{pep}\n")
        query_path = qf.name

    # 2️⃣ écrire proteome -> FASTA temporaire
    with tempfile.NamedTemporaryFile(mode="w", suffix=".fa", delete=False) as tf:
        for pid, seq in proteome:
            tf.write(f">{pid}\n{seq}\n")
        target_path = tf.name

    try:
        # 3️⃣ appel du script grawk
        result = subprocess.run(
            ["bash", "grawk_match.sh", query_path, target_path],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        # 4️⃣ parser stdout → dictionnaire
        results = {}

        for line in result.stdout.splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split(";")
            if len(parts) != 3:
                continue

            peptide, protein, pos = parts
            if not pos.isdigit():
                continue

            results.setdefault(peptide, []).append((protein, int(pos)))

        return results

    finally:
        Path(query_path).unlink(missing_ok=True)
        Path(target_path).unlink(missing_ok=True)



#UNUSED GRAWK function kept for reference
def run_grawk_mem(peptides, proteome):  #UNUSED
    """
    peptides : list[str]
    proteome : list[(protein_id, sequence)]

    Returns:
        dict : peptide -> liste de protein_ids
    """
    core_path = Path(__file__).resolve().parent  # dossier du script

    # Créer un dossier temporaire pour les fichiers FASTA
    with tempfile.TemporaryDirectory() as tmpdir:
        # Fichier peptides temporaire
        query_fasta = Path(tmpdir) / "peptides.fa"
        with open(query_fasta, "w") as f:
            for i, pep in enumerate(peptides):
                f.write(f">{i}\n{pep}\n")

        # Fichier proteome temporaire
        target_fasta = Path(tmpdir) / "proteome.fa"
        with open(target_fasta, "w") as f:
            for pid, seq in proteome:
                f.write(f">{pid}\n{seq}\n")

        # Appel du script bash
        result = subprocess.run(
            [f"{core_path}/grawk_match.sh", query_path, target_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"grawk_match.sh failed:\n{result.stderr}")

        # Lire le CSV renvoyé
        df = pd.read_csv(StringIO(result.stdout), sep=';')

        # Convertir en dict : peptide -> liste de protein_ids
        grawk_dict = {}
        for _, row in df.iterrows():
            pep = row['peptide']      # adapter si nom colonne différent
            prot = row['protein_id']  # adapter si nom colonne différent
            grawk_dict.setdefault(pep, []).append(prot)

        return grawk_dict

# Alternative: Use WSL to run bash scripts on Windows
def run_grawk_mem_wsl(peptides, proteome): #UNUSED
    """
    Run grawk_match.sh using WSL on Windows
    
    _______________________________________

    peptides : list[str]
    proteome : list[(protein_id, sequence)]

    Returns:
        dict : peptide -> liste de protein_ids
    """   
    # Create temp FASTA files
    query_fasta = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.fasta')
    target_fasta = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.fasta')
    
    for pep in peptides:
        query_fasta.write(f">{pep}\n{pep}\n")
    
    for pid, seq in proteome:
        target_fasta.write(f">{pid}\n{seq}\n")
    
    query_fasta.close()
    target_fasta.close()
    
    core_path = r"c:\Users\Hp\Desktop\biocomp_repository\MicroTPCT\benchmark"  # Adjust to your path
    
    # Run via WSL
    result = subprocess.run(
        ["wsl", "bash", f"{core_path}/grawk_match.sh", query_fasta.name, target_fasta.name],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"grawk_match.sh failed:\n{result.stderr}")
    
    return result.stdout
