#!/usr/bin/env python3

import sys
from multiprocessing import Pool, cpu_count
from Bio import SeqIO  # type: ignore
import pybmoore  # type: ignore

BIG_TEXT = None
POS_TO_TARGET = None
SEPARATOR = "#"


def build_big_text(target_fasta):
    """
    Concatène toutes les targets dans un seul texte
    et construit un mapping position -> (target_id, offset)
    """
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
    """Convertit une position globale en (target_id, local_pos)"""
    for start, end, tid in POS_TO_TARGET:
        if start <= global_pos < end:
            return tid, global_pos - start
    return None, None


def process_query(query):
    qrec_id, qseq = query
    hits = []

    matches = pybmoore.search(qseq, BIG_TEXT)

    if matches:
        for start, _ in matches:
            tid, local_pos = locate_target(start)
            if tid is not None:
                hits.append((tid, local_pos))

    return qrec_id, hits

def main(query_fasta, target_fasta):
    big_text, pos_map = build_big_text(target_fasta)
    queries = [(rec.id, str(rec.seq)) for rec in SeqIO.parse(query_fasta, "fasta")]

    with Pool(
        processes=cpu_count(),
        initializer=init_worker,
        initargs=(big_text, pos_map),
    ) as pool:
        all_results = pool.map(process_query, queries)

    print(dict(all_results))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} query.fasta target.fasta", file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
