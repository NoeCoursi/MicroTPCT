#!/usr/bin/env bash

query_file_fasta="$1"
target_file_fasta="$2"


/usr/bin/time -v awk '
BEGIN {
    while ((getline < ARGV[1]) > 0)
        if ($0 !~ /^>/) peptides[$0]=1
    ARGV[1]=""
}
/^>/ {header=$0; next}
{
    for (p in peptides)
        if (index($0,p)) print p "\t" header
}
' "$query_file_fasta" "$target_file_fasta" | sort 
