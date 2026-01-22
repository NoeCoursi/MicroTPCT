"""
MicroTPCT CLI Usage Guide

This document provides comprehensive examples and usage patterns for the MicroTPCT
command-line interface.
"""

# ============================================================================
# INSTALLATION
# ============================================================================

"""
Install from development environment:
    cd /path/to/MicroTPCT
    pip install -e .

This registers the 'microtpct' command globally.
"""

# ============================================================================
# BASIC COMMANDS
# ============================================================================

"""
1. HELP
   Get help for the tool:
   $ microtpct --help
   $ microtpct run --help
   $ microtpct align --help

2. VERSION
   Show version:
   $ microtpct --version

3. INFO
   Show algorithm information:
   $ microtpct info
   $ microtpct info --algorithm ahocorasick
   $ microtpct info --system
"""

# ============================================================================
# RUN COMMAND (Full Pipeline)
# ============================================================================

"""
Execute the complete MicroTPCT pipeline for peptide-to-protein matching.

Basic usage:
    microtpct run -p peptides.fasta -d proteins.fasta -o results/

With options:
    microtpct run \
        -p peptides.fasta \
        -d proteins.fasta \
        -o results/ \
        --algorithm ahocorasick \
        --format csv \
        --threads 4

Options:
    -p, --peptides TEXT      Input peptide sequences (FASTA format) [required]
    -d, --database TEXT      Protein database (FASTA format) [required]
    -o, --output TEXT        Output directory for results [required]
    --algorithm TEXT         Matching algorithm [default: ahocorasick]
                             Options: ahocorasick, ahocorasick_rs, find, in, 
                                     blast, boyer_moore, grawk
    --format TEXT            Output format [default: csv]
                             Options: csv, json, tsv
    --config TEXT            Path to YAML configuration file (optional)
    --threads INT            Number of parallel threads [default: 1]

Examples:
    # Using Aho-Corasick algorithm
    $ microtpct run -p peptides.fasta -d proteins.fasta -o results/
    
    # Using Rust implementation with 8 threads
    $ microtpct run -p peptides.fasta -d proteins.fasta -o results/ \
        --algorithm ahocorasick_rs --threads 8
    
    # Output as JSON
    $ microtpct run -p peptides.fasta -d proteins.fasta -o results/ \
        --format json
"""

# ============================================================================
# ALIGN COMMAND (Alignment Only)
# ============================================================================

"""
Perform peptide-to-protein alignment without full pipeline processing.

Basic usage:
    microtpct align -p peptides.fasta -d proteins.fasta -o output.csv

With options:
    microtpct align \
        -p peptides.fasta \
        -d proteins.fasta \
        -o output.csv \
        --algorithm find \
        --min-identity 0.85

Options:
    -p, --peptides TEXT      Input peptide sequences (FASTA) [required]
    -d, --database TEXT      Protein database (FASTA) [required]
    -o, --output TEXT        Output file for alignment results [required]
    --algorithm TEXT         Alignment algorithm [default: ahocorasick]
                             Options: ahocorasick, find, in
    --min-identity FLOAT     Minimum identity threshold (0.0-1.0) [default: 0.8]

Examples:
    $ microtpct align -p peptides.fasta -d proteins.fasta -o alignments.csv
    
    $ microtpct align -p peptides.fasta -d proteins.fasta -o alignments.csv \
        --algorithm find --min-identity 0.9
"""

# ============================================================================
# VALIDATE COMMAND (Input Validation)
# ============================================================================

"""
Validate input FASTA files for format and consistency.

Basic usage:
    microtpct validate -p peptides.fasta -d proteins.fasta

Options:
    -p, --peptides TEXT      Peptide file to validate (FASTA format)
    -d, --database TEXT      Protein database file to validate (FASTA format)
    --strict                 Enable strict validation checks

Examples:
    # Validate both files
    $ microtpct validate -p peptides.fasta -d proteins.fasta
    
    # Validate peptides only
    $ microtpct validate -p peptides.fasta
    
    # Strict validation
    $ microtpct validate -p peptides.fasta -d proteins.fasta --strict
"""

# ============================================================================
# INFO COMMAND (Display Information)
# ============================================================================

"""
Display system and algorithm information.

Basic usage:
    microtpct info

With options:
    microtpct info --algorithm ahocorasick
    microtpct info --system

Options:
    --algorithm TEXT         Show information about specific algorithm
                             Options: ahocorasick, ahocorasick_rs, find, in,
                                     blast, boyer_moore, grawk
    --system                 Show system information

Examples:
    # Show all algorithm information
    $ microtpct info
    
    # Show specific algorithm
    $ microtpct info --algorithm blast
    
    # Show system information
    $ microtpct info --system
"""

# ============================================================================
# VERBOSE MODE
# ============================================================================

"""
Enable verbose logging for debugging:

    microtpct --verbose run -p peptides.fasta -d proteins.fasta -o results/

Verbose output includes:
    - Debug-level logging information
    - Detailed operation traces
    - Performance metrics
    - Intermediate results
"""

# ============================================================================
# ALGORITHM COMPARISON
# ============================================================================

"""
Algorithm Characteristics:

1. Aho-Corasick (pyahocorasick) - DEFAULT
   Speed: Very Fast
   Memory: Medium
   Best for: Multiple patterns, standard matching
   
2. Aho-Corasick Rust (ahocorasick_rs)
   Speed: Fastest
   Memory: Low
   Best for: High-performance, large datasets
   
3. Python str.find()
   Speed: Medium
   Memory: Very Low
   Best for: Simple, quick testing
   
4. Python 'in' operator
   Speed: Medium
   Memory: Very Low
   Best for: Containment checks
   
5. NCBI BLAST
   Speed: Variable (slow)
   Memory: High
   Best for: Sensitive homology searches
   Requires: BLAST+ installed
   
6. Boyer-Moore
   Speed: Fast
   Memory: Low
   Best for: Single pattern, large text
   
7. GRAWK
   Speed: Fast
   Memory: Medium
   Best for: Complex pattern expressions
"""

# ============================================================================
# INPUT FILE FORMATS
# ============================================================================

"""
FASTA Format Example:

>protein_id
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQ
VKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHS

>peptide_id
MKFLKFSLLTAVLLSVVFAFSSCGDDDDTGFA
"""

# ============================================================================
# OUTPUT FORMATS
# ============================================================================

"""
CSV Output Format:
    query_id,target_id,position,identity
    Q001,T001,45,0.95
    Q001,T002,12,0.89
    Q002,T001,78,0.92

JSON Output Format:
    {
      "metadata": {
        "timestamp": "2024-01-22T10:30:00",
        "algorithm": "ahocorasick",
        "total_matches": 150
      },
      "matches": [
        {"query_id": "Q001", "target_id": "T001", "position": 45, "identity": 0.95}
      ]
    }

TSV Output Format (similar to CSV but tab-separated):
    query_id    target_id    position    identity
    Q001    T001    45    0.95
    Q001    T002    12    0.89
"""

# ============================================================================
# ADVANCED EXAMPLES
# ============================================================================

"""
Example 1: Benchmark different algorithms
    
    # Run with each algorithm and compare
    for algo in ahocorasick find in; do
        microtpct run -p peptides.fasta -d proteins.fasta \
            -o results_$algo --algorithm $algo
    done

Example 2: Process large datasets with multiple threads
    
    microtpct run -p large_peptides.fasta -d large_proteins.fasta \
        -o results/ --algorithm ahocorasick_rs --threads 16

Example 3: Pipeline with configuration file
    
    # Create config.yaml with custom settings
    microtpct run -p peptides.fasta -d proteins.fasta \
        -o results/ --config config.yaml

Example 4: Validate before processing
    
    microtpct validate -p peptides.fasta -d proteins.fasta
    if [ $? -eq 0 ]; then
        microtpct run -p peptides.fasta -d proteins.fasta -o results/
    fi

Example 5: Quick test with small dataset
    
    # Validate first
    microtpct validate -p test_peptides.fasta -d test_proteins.fasta
    
    # Run alignment
    microtpct align -p test_peptides.fasta -d test_proteins.fasta \
        -o test_results.csv
    
    # Check info
    microtpct info --algorithm ahocorasick
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Common Issues:

1. "Command not found: microtpct"
   Solution: Install package with: pip install -e .

2. "File not found: peptides.fasta"
   Solution: Check file path and ensure file exists

3. "Invalid FASTA format"
   Solution: Validate with: microtpct validate -p peptides.fasta

4. "Algorithm not available"
   Solution: Check installed dependencies, see: microtpct info

5. "Memory error with large dataset"
   Solution: Use ahocorasick_rs algorithm or split data

6. "BLAST not found"
   Solution: Install NCBI BLAST+: sudo apt-get install ncbi-blast+

Tips for Better Performance:
    - Use ahocorasick_rs for speed
    - Use --threads for parallel processing
    - Validate input files first
    - Use verbose mode for debugging
    - Monitor memory usage with large datasets
"""

# ============================================================================
# EXIT CODES
# ============================================================================

"""
Exit Codes:
    0   - Success
    1   - Error (invalid input, file not found, etc.)
    2   - Usage error (missing required arguments)
"""
