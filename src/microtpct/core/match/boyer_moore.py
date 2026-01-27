import sys
import pybmoore  # type: ignore
import pandas as pd

from multiprocessing import Pool, cpu_count
from Bio import SeqIO  # type: ignore

from microtpct.core.databases import TargetDB, QueryDB
from microtpct.core.results import MatchResult

BIG_TEXT = None
POS_TO_TARGET = None
SEPARATOR = "#" # Separator inserted between concatenated sequences


def concatenate_prot(target_db: TargetDB) -> tuple:
    """
    Concatenate all target sequences into a single text string.
    Build a mapping from global position to (target_id, offset).

    Args:
        target_fasta (str): Path to the target FASTA file.

    Returns:
        tuple:
            - big_text (str): concatenated sequences separated by SEPARATOR
            - pos_map (list of tuples): [(start, end, target_id), ...]
    """
    big_chunks = []
    pos_map = []
    current_pos = 0

    for prot_id, prot_seq in zip(target_db.ids, target_db.ambiguous_il_sequences):
        seq = str(prot_seq)
        big_chunks.append(seq)

        pos_map.append((current_pos, current_pos + len(seq), prot_id))

        # Update the global position
        current_pos += len(seq)
        big_chunks.append(SEPARATOR)
        current_pos += len(SEPARATOR)

    return "".join(big_chunks), pos_map

def init_worker(big_text: str, pos_map: int) -> None:
    """
    Initialize global variables for multiprocessing workers.

    Args:
        big_text (str): concatenated sequences
        pos_map (list): mapping from global position to (target_id, offset)
    """
    global BIG_TEXT, POS_TO_TARGET
    BIG_TEXT = big_text
    POS_TO_TARGET = pos_map

def locate_target(global_pos) -> tuple:
    """
    Convert a global position in the concatenated text
    to (target_id, local position within the target sequence).

    Args:
        global_pos (int): global position in BIG_TEXT

    Returns:
        tuple: (target_id, local_pos) or (None, None) if not found
    """
        
    for start, end, tid in POS_TO_TARGET:
        if start <= global_pos < end:
            return tid, global_pos - start
    return None, None

def process_query(query: list) -> tuple:
    """
    Search for occurrences of a query sequence in the concatenated text.

    Args:
        query (list): [query_id, sequence]

    Returns:
        tuple: (query_id, list of hits)
            hits: [(target_id, local_position), ...]
    """
    qrec_id, qseq = query
    hits = []

    matches = pybmoore.search(qseq, BIG_TEXT)

    if matches:
        for start, _ in matches:
            tid, local_pos = locate_target(start)
            if tid is not None:
                hits.append((tid, local_pos))

    return qrec_id, hits


def run_boyer_moore(target_db: TargetDB, query_db: QueryDB) -> MatchResult:

    # Build concatenated text and position mapping
    big_text, pos_map = concatenate_prot(target_db)
    queries = [(t_id, str(t_seq)) for t_id, t_seq in zip(query_db.ids, query_db.ambiguous_il_sequences)]


    # Perform parallel search using multiprocessing
    with Pool(
        processes=cpu_count(),
        initializer=init_worker,
        initargs=(big_text, pos_map),
    ) as pool:
        all_results = pool.map(process_query, queries)
    print(all_results)

    return

