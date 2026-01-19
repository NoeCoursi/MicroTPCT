#!/usr/bin/env bash

query_file_fasta="$1"
target_file_fasta="$2"

/usr/bin/time -v awk '
BEGIN {
    # Read the query FASTA
    while ((getline < ARGV[1]) > 0) {
        if ($0 ~ /^>/) {
            peptide_header = $0       # store the header
        } else {
            peptides[$0] = peptide_header  # map sequence -> header
        }
    }
    ARGV[1] = ""  # clear so next ARGV files are processed normally
}

# Process target FASTA
/^>/ {target_header = $0; next}  # store current target header
{
    for (seq in peptides)
        if (index($0, seq))  # if peptide seq is found in target
            print seq "\t" peptides[seq] "\t" target_header
}
' "$query_file_fasta" "$target_file_fasta" | sort

