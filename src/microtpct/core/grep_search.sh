#!/bin/bash

set -eu

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 fasta1 fasta2" >&2
    exit 1
fi

FASTA1=$1
FASTA2=$2


TMP_FASTA2=$(mktemp)
trap 'rm -f "$TMP_FASTA2"' EXIT

LC_ALL=C awk '
  /^>/ {
    if (seq) print header "\t" seq
    header=substr($0,2)
    seq=""
    next
  }
  { seq=seq $0 }
  END { if (seq) print header "\t" seq }
' "$FASTA2" > "$TMP_FASTA2"

echo "query_header,target_header,position"


LC_ALL=C awk '
  /^>/ {
    if (seq) print header "\t" seq
    header=substr($0,2)
    seq=""
    next
  }
  { seq=seq $0 }
  END { if (seq) print header "\t" seq }
' "$FASTA1" |
while IFS=$'\t' read -r h1 seq1; do

    grep -F "$seq1" "$TMP_FASTA2" |
    awk -F'\t' -v q="$h1" -v s="$seq1" '
      {
        pos=index($2, s)-1
        if(pos>=0) print q","$1","pos
      } END { if(NR==0) print q",," }'

done
