#!/usr/bin/env python3
"""
Benchmark multiple sequence alignment packages on a simple workload.
Requires: biopython, parasail, edlib
    pip install biopython parasail edlib

In VScode :
Install Windows C++ Build Tools (for edlib) : https://visualstudio.microsoft.com/visual-cpp-build-tools/
Download Build Tools for Visual Studio
In the installer, select: Desktop development with C++
Reboot terminal
Run : pip install edlib    

https://biopython.org/docs/dev/Tutorial/chapter_pairwise.html 
Pairwise sequence alignment is the process of aligning two sequences to each other by optimizing the similarity
score between them. The Bio.Align module contains the PairwiseAligner class for global and local alignments 
using the Needleman-Wunsch, Smith-Waterman, Gotoh (three-state), and Waterman-Smith-Beyer global and local 
pairwise alignment algorithms, and the Fast Optimal Global Alignment Algorithm (FOGSAA), with numerous options
 to change the alignment parameters. We refer to Durbin et al. [Durbin1998] for in-depth information on 
 sequence alignment algorithms.

parasail is a SIMD C (C99) library containing implementations of the Smith-Waterman (local), Needleman-Wunsch 
(global), and various semi-global pairwise sequence alignment algorithms. Here, semi-global means insertions 
before the start or after the end of either the query or target sequence are optionally not penalized. 
parasail implements most known algorithms for vectorized pairwise sequence alignment, including diagonal 
[Wozniak, 1997], blocked [Rognes and Seeberg, 2000], striped [Farrar, 2007], and prefix scan [Daily, 2015]. 
Therefore, parasail is a reference implementation for these algorithms in addition to providing an 
implementation of the best-performing algorithm(s) to date on today's most advanced CPUs.    

Edlib is a lightweight C/C++ library and tool suite for fast exact sequence alignment (edit distance/Levenshtein), 
supporting global, infix, and prefix alignments, with optional alignment paths and start/end locations, 
and provides a CLI aligner and language bindings including edlibAlign and EdlibAlignResult objects    
"""

import time
import statistics
import numpy
import Bio
from Bio import Align
#import parasail
import edlib

SEQ_A = "GATTACAGATTACAGATTACA" * 5
SEQ_B = "GACTATAAGACTATAAGACTATAA" * 5
REPEATS = 50


def bench(label, fn):
    durations = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - t0)
    print(f"{label:25} mean={statistics.mean(durations):.6f}s "
          f"min={min(durations):.6f}s max={max(durations):.6f}s")


aligner = Align.PairwiseAligner()

def bio_global():
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -2
    aligner.extend_gap_score = -1
    list(aligner.align(SEQ_A, SEQ_B))


def bio_local():
    aligner.mode = "local"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -2
    aligner.extend_gap_score = -1
    list(aligner.align(SEQ_A, SEQ_B))


#def parasail_sw():
    #parasail.sw_trace(SEQ_A, SEQ_B, 2, 1, parasail.nuc44)


#def parasail_nw():
    #parasail.nw_trace(SEQ_A, SEQ_B, 2, 1, parasail.nuc44)


def edlib_lev():
    edlib.align(SEQ_A, SEQ_B, mode="NW", task="path")


if __name__ == "__main__":
    print(f"Benchmarking {REPEATS} iterations per method")
    bench("Biopython globalxx", bio_global)
    bench("Biopython localxx", bio_local)
    #bench("Parasail SW", parasail_sw)
    #bench("Parasail NW", parasail_nw)
    bench("Edlib NW", edlib_lev)


