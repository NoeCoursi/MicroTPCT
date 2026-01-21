#!/bin/bash

set -eu

regex=FALSE

while getopts "r" opt; do
    case "$opt" in
        r)
            regex=TRUE
            ;;
        *)
            echo "Usage: $0 fasta1 fasta2 [-r]" >&2
            exit 1
            ;;
    esac
done

shift $((OPTIND - 1))

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 fasta1 fasta2 [-r]" >&2
    exit 1
fi

FASTA1="$1"
FASTA2="$2"

TMP_FASTA2=$(mktemp)
trap 'rm -f "$TMP_FASTA2"' EXIT

usage(){
    echo "Usage: $0 [QUERY_FASTA] [TARGET_FASTA] -R"
    echo "  -R              : Regex search, allows X mismatch"
    exit 1
}


regex_core() 
{ 
  sed "s/;/_/g" "$FASTA2" |
  LC_ALL=C awk '
    /^>/ {
      if (seq) {
        gsub(/X/, ".", seq)   # remplacer X par . dans la séquence uniquement
        print header "\t" seq
      }
      header = substr($0, 2)
      seq = ""
      next
    }
    { seq = seq $0 }
    END {
      if (seq) {
        gsub(/X/, ".", seq)
        print header "\t" seq
      }
    }
  ' > "$TMP_FASTA2"
  



  echo "query_header;target_header;position"

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
  while IFS=$'\t' read -r h1 seq1; do #grep single seq to full target fasta

      grep -E "$seq1" "$TMP_FASTA2" |
      awk -F'\t' -v q="$h1" -v s="$seq1" '
        {
          pos=match($2, s)-1
          if(pos>=0) print q";"$1";"pos
        } END { if(NR==0) print q";;" }'
  done
}

text_core() 
{ 
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

  echo "query_header;target_header;position"

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
  while IFS=$'\t' read -r h1 seq1; do #grep single seq to full target fasta

      grep -F "$seq1" "$TMP_FASTA2" |
      awk -F'\t' -v q="$h1" -v s="$seq1" '
        {
          pos=index($2, s)-1
          if(pos>=0) print q";"$1";"pos
        } END { if(NR==0) print q";;"}'
  done
}


# Not finished, in dev, non functional
regex_core_inverted() 
{ 
  sed -e "s/[\t;:,. ]/_/g" -e '/^>/! s/X/./g' "$FASTA2" |
  seqkit seq -w 0 | awk '/^>/{printf "%s ", $0; next} {print}' > "$TMP_FASTA2"


  sed -e "s/[\t;:,. ]/_/g" -e '/^>/! s/X/./g' "$FASTA1" |
  seqkit seq -w 0 | awk '/^>/{printf "%s ", $0; next} {print}' |
  while IFS=$' ' read -r h1 seq1; do
      echo "$h1"
      grep -E "$seq2" "$FASTA1" | head

      awk -F'\t' -v q="$h2" -v s="$seq2" '
        {
          pos=match($2, s)-1
          if(pos>=0) print q";"$1";"pos
        } END { if(NR==0) print q";;" }'
  done
}



if [[ "$regex" == "TRUE" ]]; then
    regex_core
else
    text_core
fi