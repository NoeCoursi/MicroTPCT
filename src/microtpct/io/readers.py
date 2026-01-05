from pathlib import Path
from enum import Enum
from typing import Iterator, Optional
from microtpct.io.schema import ProteinInput, PeptideInput
from microtpct.utils import setup_logger

logger = setup_logger(__name__)

# Sequence roles
class SequenceRole(Enum):
    """
    Class that define role of the readed sequence in a clean way.
    """

    PROTEIN = "protein"
    PEPTIDE = "peptide"


# Base reader
class BaseReader:
    """
    Base class for all readers.
    Defines the minimal interface: read() -> Iterator[Input]
    """

    def __init__(self, file_path: str, role: SequenceRole):
        self.file_path = Path(file_path)
        self.role = role
    
    def _check_file_exists(self) -> bool:
        if not self.file_path.exists():
            logger.error(f"File not found: {self.file_path}")
            return False
        return True

    def read(self) -> Iterator:
        """
        Generator yielding Input objects.
        Must be implemented by each concrete reader.
        """
        raise NotImplementedError("read() must be implemented by the concrete reader.")


# FASTA reader
class FastaReader(BaseReader):
    """
    FASTA reader using Biopython SeqIO.
    Produces ProteinInput or PeptideInput depending on the role.
    """

    def read(self) -> Iterator:
        if not self._check_file_exists():
            return
        
        try:
            from Bio import SeqIO # Only if needed (optimization)
        except ImportError:
            logger.error("Biopython is required for FASTA parsing. Please install biopython.")
            return

        try:
            for record in SeqIO.parse(str(self.file_path), "fasta"):
                input_obj = self._build_input(record.id, str(record.seq))
                if input_obj:
                    yield input_obj
        except Exception as e:
            logger.error(f"Error reading FASTA ({self.file_path}): {e}")

    def _build_input(self, header: str, sequence: str) -> Optional[object]:
        """
        Build the Input object based on the role.
        Performs light normalization (strip, upper).
        """
        sequence = sequence.strip().upper() # Normalization
        if self.role == SequenceRole.PROTEIN:
            return ProteinInput(id=header, sequence=sequence)
        
        elif self.role == SequenceRole.PEPTIDE:
            return PeptideInput(id=header, sequence=sequence)
        
        else:
            logger.warning(f"Unknown role '{self.role}' for sequence {header}")
            return None


# Reader factory
def read_file(file_path: str, role: SequenceRole, format: Optional[str] = None) -> Iterator:
    """
    Factory function to return the appropriate reader based on format.
    If format is not specified, try to deduce it from file extension.
    Usage: read_file("file.fasta", format="fasta", role=SequenceRole.PROTEIN)
    """

    file_path_obj = Path(file_path) # Convert into Path object to get the suffix.

    # Format guessing from extension
    if not format:
        ext = file_path_obj.suffix.lower()
        if ext in (".fasta", ".fa"):
            format = "fasta"
        else:
            logger.error(f"Cannot deduce format from file extension '{ext}' for file {file_path}")
            return iter([])  # empty iterator

    format = format.lower()
    if format == "fasta":
        reader = FastaReader(file_path, role)
    else:
        logger.error(f"Unsupported format '{format}' for file {file_path}")
        return iter([])  # empty iterator

    return reader.read()