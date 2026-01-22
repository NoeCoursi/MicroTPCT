from unittest import result
from Bio import SeqIO
import subprocess
import tempfile
import os
import shutil as sh

### bash commands makeblastdb and blastp must be installed and on PATH
# sudo apt update
# sudo apt install ncbi-blast+

## to do : replace input (proteins and peptides) with apropriate classes
# ne pas autoriser les gap -> gapopen dans le outfmt : ... length mismatch gapopen ...
# vérifier que l’alignement couvre 100% du peptide : outfmt = "6 qseqid sseqid pident length mismatch gapopen qlen sstart send"


# Use local BLAST+ (makeblastdb + blastp) to find exact peptide matches in proteins.
def run_blast(peptides, proteome_file):
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
        cmd_make = ["makeblastdb", "-in", proteome_file, "-dbtype", "prot", "-out", db_prefix]
        result = subprocess.run(cmd_make, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Run blastp (short-task) with tabular output including sstart/send, percent identity and alignment length
        # Use correct outfmt tokens: sseqid, length, sstart/send
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
            raise RuntimeError(f"blastp failed with return code {proc.returncode}")

        blast_out = proc.stdout

        # Parse blast output lines
        for line in blast_out.splitlines():
            if not line:
                continue
            # skip BLAST comment/header lines
            if line.startswith("#"):
                continue

            qseqid, sseqid, pident, alen, mismatch, gapopen, qlen, sstart, send = line.split()
            pat_idx = int(qseqid)
            pep = peptides[pat_idx]
            # Only accept full-length exact matches (pident 100 and alignment length == peptide length and 0 mismatches and 0 gap)
            if float(pident) != 100.0:
                continue
            if int(mismatch) != 0:
                continue
            if int(alen) != len(pep):
                continue
            if int(gapopen) != 0:
                continue
            if int(alen) != int(qlen):
                continue


            sstart_i = int(sstart) - 1
            send_i = int(send) - 1
            start0 = min(sstart_i, send_i)
            results.setdefault(pep, []).append((sseqid, start0))

        return results
    finally:
        sh.rmtree(tmpdir)



### test:
# Load peptides: text file with one peptide sequence per line
peptides = []
peptides_file = "/home/ambroiz/Bureau/BIOCOMP/DEFI_BIOINFO/peptides.txt"

with open(peptides_file) as f:
    for line in f:
        peptides.append(line.strip()) 


proteome_file = "/home/ambroiz/Bureau/BIOCOMP/DEFI_BIOINFO/uniprotkb_proteome_UP000000803_2025_11_25.fasta"

print("\n=== Local BLAST ===")
print(run_blast(peptides, proteome_file))

