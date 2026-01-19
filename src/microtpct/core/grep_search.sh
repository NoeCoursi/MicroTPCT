#!/usr/bin/env bash

query_file_fasta="$1"
target_file_fasta="$2"

echo "------------------------------------------------------"
echo "------------------------------------------------------"
echo "MATCHED"
echo "------------------------------------------------------"
echo "------------------------------------------------------"


/usr/bin/time -v grep -F -o -f "$query_file_fasta" "$target_file_fasta" | LC_ALL=C sort | uniq -c




echo "------------------------------------------------------"
echo "------------------------------------------------------"
echo "NON MATCHED"
echo "------------------------------------------------------"
echo "------------------------------------------------------"

/usr/bin/time -v grep -F -o -f "$query_file_fasta" "$target_file_fasta" | sort -u | grep -F -o -v -f "$query_file_fasta"
