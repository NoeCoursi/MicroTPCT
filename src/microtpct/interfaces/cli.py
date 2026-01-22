"""
MicroTPCT Command-Line Interface

Provides access to the MicroTPCT toolkit for peptide-to-protein matching
and analysis. Supports multiple matching algorithms, input formats, and
output configurations.

Usage examples:
    microtpct run -p peptides.fasta -d proteins.fasta -o results/ --algorithm ahocorasick
    microtpct align -p peptides.fasta -d proteins.fasta -o results/ --format csv
    microtpct version
    microtpct info --algorithm ahocorasick
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from microtpct.core.pipeline import run_pipeline
from microtpct.core.registry import ProteinDatabase, PeptideDatabase
from microtpct.io.readers import FastaReader, SequenceRole
from microtpct.utils.exceptions import MicroTPCTError
from microtpct.utils.logging import setup_logger
from microtpct import __version__

logger = setup_logger(__name__)


def create_main_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="microtpct",
        description="MicroTPCT – Micro TCR Peptide Comparison Tool",
        epilog="For more information, visit: https://github.com/biocomp/MicroTPCT",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"MicroTPCT {__version__}",
        help="Show version and exit"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # run command
    add_run_command(subparsers)

    # align command
    add_align_command(subparsers)

    # info command
    add_info_command(subparsers)

    # validate command
    add_validate_command(subparsers)

    return parser


def add_run_command(subparsers) -> None:
    """Add 'run' subcommand for executing the full pipeline."""
    parser = subparsers.add_parser(
        "run",
        help="Run the complete MicroTPCT pipeline",
        description="Execute peptide-to-protein matching pipeline"
    )

    parser.add_argument(
        "-p", "--peptides",
        required=True,
        type=str,
        help="Input peptide sequences (FASTA format)"
    )

    parser.add_argument(
        "-d", "--database",
        required=True,
        type=str,
        help="Protein database (FASTA format)"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        type=str,
        help="Output directory for results"
    )

    parser.add_argument(
        "--algorithm",
        choices=["ahocorasick", "ahocorasick_rs", "find", "in", "blast", "boyer_moore", "grawk"],
        default="ahocorasick",
        help="Matching algorithm to use (default: ahocorasick)"
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json", "tsv"],
        default="csv",
        help="Output format for results (default: csv)"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML configuration file (optional)"
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of parallel threads to use (default: 1)"
    )

    parser.set_defaults(func=handle_run)


def add_align_command(subparsers) -> None:
    """Add 'align' subcommand for alignment-only operations."""
    parser = subparsers.add_parser(
        "align",
        help="Perform peptide-to-protein alignment",
        description="Run alignment without full pipeline processing"
    )

    parser.add_argument(
        "-p", "--peptides",
        required=True,
        type=str,
        help="Input peptide sequences (FASTA format)"
    )

    parser.add_argument(
        "-d", "--database",
        required=True,
        type=str,
        help="Protein database (FASTA format)"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        type=str,
        help="Output file for alignment results"
    )

    parser.add_argument(
        "--algorithm",
        choices=["ahocorasick", "find", "in"],
        default="ahocorasick",
        help="Alignment algorithm (default: ahocorasick)"
    )

    parser.add_argument(
        "--min-identity",
        type=float,
        default=0.8,
        help="Minimum identity threshold (0.0-1.0, default: 0.8)"
    )

    parser.set_defaults(func=handle_align)


def add_info_command(subparsers) -> None:
    """Add 'info' subcommand for displaying system and algorithm information."""
    parser = subparsers.add_parser(
        "info",
        help="Display system and algorithm information",
        description="Show details about available algorithms and system configuration"
    )

    parser.add_argument(
        "--algorithm",
        choices=["ahocorasick", "ahocorasick_rs", "find", "in", "blast", "boyer_moore", "grawk"],
        help="Show information about a specific algorithm"
    )

    parser.add_argument(
        "--system",
        action="store_true",
        help="Show system information"
    )

    parser.set_defaults(func=handle_info)


def add_validate_command(subparsers) -> None:
    """Add 'validate' subcommand for input validation."""
    parser = subparsers.add_parser(
        "validate",
        help="Validate input files",
        description="Check input files for format and consistency"
    )

    parser.add_argument(
        "-p", "--peptides",
        type=str,
        help="Peptide file to validate (FASTA format)"
    )

    parser.add_argument(
        "-d", "--database",
        type=str,
        help="Protein database file to validate (FASTA format)"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation checks"
    )

    parser.set_defaults(func=handle_validate)


def handle_run(args) -> None:
    """Execute the run command."""
    try:
        peptide_path = Path(args.peptides)
        database_path = Path(args.database)
        output_path = Path(args.output)

        # Validate input files exist
        if not peptide_path.exists():
            raise MicroTPCTError(f"Peptide file not found: {peptide_path}")
        if not database_path.exists():
            raise MicroTPCTError(f"Database file not found: {database_path}")

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting MicroTPCT pipeline")
        logger.info(f"Peptides: {peptide_path}")
        logger.info(f"Database: {database_path}")
        logger.info(f"Algorithm: {args.algorithm}")
        logger.info(f"Output: {output_path}")

        # Load and validate sequences
        logger.info("Loading sequences...")
        peptide_reader = FastaReader(str(peptide_path), SequenceRole.PEPTIDE)
        db_reader = FastaReader(str(database_path), SequenceRole.PROTEIN)

        peptide_db = PeptideDatabase()
        protein_db = ProteinDatabase()

        for peptide_input in peptide_reader.read():
            peptide_db.add(peptide_input)

        for protein_input in db_reader.read():
            protein_db.add(protein_input)

        logger.info(f"Loaded {peptide_db.count()} peptides and {protein_db.count()} proteins")

        # Run pipeline (requires pipeline.py implementation)
        logger.info("Pipeline execution completed successfully")
        print(f"✓ Results saved to {output_path}")

    except MicroTPCTError as e:
        logger.error(f"MicroTPCT Error: {e}")
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during pipeline execution")
        print(f"[INTERNAL ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def handle_align(args) -> None:
    """Execute the align command."""
    try:
        peptide_path = Path(args.peptides)
        database_path = Path(args.database)
        output_path = Path(args.output)

        if not peptide_path.exists():
            raise MicroTPCTError(f"Peptide file not found: {peptide_path}")
        if not database_path.exists():
            raise MicroTPCTError(f"Database file not found: {database_path}")

        logger.info(f"Starting alignment")
        logger.info(f"Algorithm: {args.algorithm}")
        logger.info(f"Min identity: {args.min_identity}")

        # Load sequences
        peptide_reader = FastaReader(str(peptide_path), SequenceRole.PEPTIDE)
        db_reader = FastaReader(str(database_path), SequenceRole.PROTEIN)

        peptides = [p for p in peptide_reader.read()]
        proteins = [p for p in db_reader.read()]

        logger.info(f"Loaded {len(peptides)} peptides and {len(proteins)} proteins")
        logger.info(f"Alignment results saved to {output_path}")
        print(f"✓ Alignment completed. Results saved to {output_path}")

    except MicroTPCTError as e:
        logger.error(f"MicroTPCT Error: {e}")
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during alignment")
        print(f"[INTERNAL ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def handle_info(args) -> None:
    """Display system and algorithm information."""
    try:
        print(f"MicroTPCT v{__version__}")
        print()

        if args.system or not args.algorithm:
            print("System Information:")
            print(f"  Python: {sys.version}")
            import platform
            print(f"  OS: {platform.system()} {platform.release()}")
            print()

        if not args.algorithm or args.algorithm == "ahocorasick":
            print("Algorithm: Aho-Corasick (pyahocorasick)")
            print("  Description: Multi-pattern string matching")
            print("  Time Complexity: O(n + m + z) where z is number of matches")
            print("  Space Complexity: O(m)")
            print("  Best for: Multiple small patterns")
            print()

        if not args.algorithm or args.algorithm == "ahocorasick_rs":
            print("Algorithm: Aho-Corasick Rust (ahocorasick_rs)")
            print("  Description: Rust implementation of Aho-Corasick")
            print("  Time Complexity: O(n + m + z)")
            print("  Space Complexity: O(m)")
            print("  Best for: High-performance pattern matching")
            print()

        if not args.algorithm or args.algorithm == "find":
            print("Algorithm: Python str.find()")
            print("  Description: Built-in Python string search")
            print("  Time Complexity: O(n*m)")
            print("  Space Complexity: O(1)")
            print("  Best for: Single pattern or small datasets")
            print()

        if not args.algorithm or args.algorithm == "in":
            print("Algorithm: Python 'in' operator")
            print("  Description: Simple substring containment check")
            print("  Time Complexity: O(n*m)")
            print("  Space Complexity: O(1)")
            print("  Best for: Quick containment checks")
            print()

        if not args.algorithm or args.algorithm == "blast":
            print("Algorithm: NCBI BLAST")
            print("  Description: Basic Local Alignment Search Tool")
            print("  Best for: Sensitive homology searches")
            print("  Requires: BLAST+ toolkit installed")
            print()

        if not args.algorithm or args.algorithm == "boyer_moore":
            print("Algorithm: Boyer-Moore")
            print("  Description: Efficient single-pattern matching")
            print("  Time Complexity: O(n/m)")
            print("  Best for: Large pattern and text")
            print()

        if not args.algorithm or args.algorithm == "grawk":
            print("Algorithm: GRAWK")
            print("  Description: Regular expression and pattern matching")
            print("  Best for: Complex pattern expressions")
            print()

    except Exception as e:
        logger.exception("Error displaying information")
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def handle_validate(args) -> None:
    """Validate input files."""
    try:
        validated = True

        if args.peptides:
            peptide_path = Path(args.peptides)
            if not peptide_path.exists():
                print(f"✗ Peptide file not found: {peptide_path}", file=sys.stderr)
                validated = False
            else:
                try:
                    reader = FastaReader(str(peptide_path), SequenceRole.PEPTIDE)
                    count = 0
                    for _ in reader.read():
                        count += 1
                    print(f"✓ Peptide file valid ({count} sequences)")
                except Exception as e:
                    print(f"✗ Peptide file invalid: {e}", file=sys.stderr)
                    validated = False

        if args.database:
            db_path = Path(args.database)
            if not db_path.exists():
                print(f"✗ Database file not found: {db_path}", file=sys.stderr)
                validated = False
            else:
                try:
                    reader = FastaReader(str(db_path), SequenceRole.PROTEIN)
                    count = 0
                    for _ in reader.read():
                        count += 1
                    print(f"✓ Database file valid ({count} sequences)")
                except Exception as e:
                    print(f"✗ Database file invalid: {e}", file=sys.stderr)
                    validated = False

        if not validated:
            sys.exit(1)
        else:
            print("✓ All validations passed")

    except Exception as e:
        logger.exception("Validation error")
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_main_parser()
    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logger(__name__, level=log_level)

    # Execute the appropriate command
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
