from pathlib import Path
from enum import Enum
from typing import Iterator, Optional, Dict, Sequence
from microtpct.io.schema import TargetInput, QueryInput
from microtpct.utils import setup_logger

logger = setup_logger(__name__)

# Sequence roles
class SequenceRole(Enum):
    """
    Class that define role of the readed sequence in a clean way.
    """

    TARGET = "target"
    QUERY = "query"


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
    Produces TargetInput or QueryInput depending on the role.
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
        accession = header.split("|")[1]
        sequence = sequence.strip().upper() # Normalization
        if self.role == SequenceRole.TARGET:
            return TargetInput(accession=accession, sequence=sequence)
        
        elif self.role == SequenceRole.QUERY:
            return QueryInput(accession=accession, sequence=sequence)
        
        else:
            logger.warning(f"Unknown role '{self.role}' for sequence {header}")
            return None


class AbstractPandasReader(BaseReader):
    """
    Abstract base class for pandas-based readers (CSV, TSV, XLSX, etc.).

    Handles:
    - I/O checks
    - pandas import
    - column validation
    - row iteration
    - role-based Input construction

    Should not be directly manualy instancied by user.

    Subclasses must implement:
        _load_dataframe() -> pandas.DataFrame
    """

    # Default Proline headers
    PROLINE_COLUMNS: Dict[str, str] = {
        "accession": "accession",
        "sequence": "sequence",
    }

    def __init__(
        self,
        file_path: str,
        role: SequenceRole,
        columns: Optional[Dict[str, str]] = None,
    ):
        super().__init__(file_path, role)
        self.columns = columns or self.PROLINE_COLUMNS

    # Public API
    def read(self) -> Iterator:
        if not self._check_file_exists():
            return

        try:
            import pandas as pd  # lazy import
        except ImportError:
            logger.error("Pandas is required for tabular/XLSX parsing. Please install pandas.")
            return

        try:
            df = self._load_dataframe()
        except Exception as e:
            logger.error(f"Error reading file ({self.file_path}): {e}")
            return

        if not self._check_required_columns(df.columns):
            return

        for record in df.itertuples(index=False):
            try:
                accession_val = getattr(record, self.columns["accession"])
                sequence_val = getattr(record, self.columns["sequence"])
            except AttributeError as e:
                logger.error(f"Column access error in {self.file_path}: {e}")
                continue

            input_obj = self._build_input(accession_val, sequence_val)
            if input_obj:
                yield input_obj

    # Hooks for subclasses
    def _load_dataframe(self):
        """
        Load the file into a pandas DataFrame.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("_load_dataframe() must be implemented by subclasses.")

    # Internal helpers
    def _check_required_columns(self, available_columns: Sequence[str]) -> bool:
        """Check that all required columns are present in the dataframe."""
        required = set(self.columns.values())
        available = set(available_columns)

        missing = required - available
        if missing:
            logger.error(
                f"Missing required columns in {self.file_path}: {sorted(missing)}. "
                f"Available columns: {sorted(available)}"
            )
            return False

        return True

    def _build_input(
        self, accession: str, sequence: str
    ) -> Optional[object]:
        """
        Build the Input object based on the role.
        Performs light normalization (strip, upper).
        """
        sequence = str(sequence).strip().upper()

        if self.role == SequenceRole.TARGET:
            return TargetInput(accession=accession, sequence=sequence)

        elif self.role == SequenceRole.QUERY:
            return QueryInput(accession=accession, sequence=sequence)

        else:
            logger.warning(f"Unknown role '{self.role}' for sequence {id}")
            return None


# Tabular reader
class TabularReader(AbstractPandasReader):
    """
    Tabular format reader using pandas.read_csv.

    By default, expects Proline-like headers:
        - accession
        - sequence
    """

    def __init__(
        self,
        file_path: str,
        role: SequenceRole,
        sep: str = ",",
        columns: Optional[Dict[str, str]] = None,
    ):
        super().__init__(file_path, role, columns)
        self.sep = sep

    def _load_dataframe(self):
        import pandas as pd
        return pd.read_csv(str(self.file_path), sep=self.sep)


# XLSX reader
class XlsxReader(AbstractPandasReader):
    """
    Excel (.xlsx) format reader using pandas.read_excel.

    By default, expects Proline-like headers:
        - accession
        - sequence
    """

    def __init__(
        self,
        file_path: str,
        role: SequenceRole,
        sheet_name: int | str = 0,
        columns: Optional[Dict[str, str]] = None,
    ):
        super().__init__(file_path, role, columns)
        self.sheet_name = sheet_name

    def _load_dataframe(self):
        import pandas as pd
        return pd.read_excel(str(self.file_path), sheet_name=self.sheet_name)


def read_file(
    file_path: str,
    role: SequenceRole,
    format: Optional[str] = None,
    **kwargs,
) -> Iterator:
    """
    Factory function to return the appropriate reader based on format.

    If format is not specified, it is deduced from the file extension.

    For tabular formats (CSV/TSV), the separator is deduced from the extension
    unless explicitly provided via kwargs.

    Parameters
    ----------
    file_path : str
        Path to the input file.
    role : SequenceRole
        Role of the sequences (TARGET or QUERY).
    format : str, optional
        Input format ("fasta", "csv", "tsv", "xlsx").
        If None, deduced from file extension.
    **kwargs
        Additional keyword arguments passed to the reader constructor
        (e.g., sep, sheet_name, columns).

    Returns
    -------
    Iterator
        Iterator over Input objects.
    """

    file_path_obj = Path(file_path)
    ext = file_path_obj.suffix.lower()

    # Deduce format from extension
    if format is None:
        if ext in (".fasta", ".fa", ".faa"):
            format = "fasta"
        elif ext == ".csv":
            format = "csv"
        elif ext in (".tsv", ".txt"):
            format = "tsv"
        elif ext == ".xlsx":
            format = "xlsx"
        else:
            logger.error(
                f"Cannot deduce format from file extension '{ext}' for file {file_path}"
            )
            return iter([])

    format = format.lower()

    # Instantiate appropriate reader
    if format == "fasta":
        reader = FastaReader(file_path, role)

    elif format in ("csv", "tsv"):
        # Deduce separator from extension unless explicitly provided
        if "sep" not in kwargs:
            if ext == ".csv":
                kwargs["sep"] = ","
            elif ext in (".tsv", ".txt"):
                kwargs["sep"] = "\t"
            else:
                # fallback (should not really happen if format deduction worked)
                kwargs["sep"] = ","
                logger.warning(
                    f"Could not deduce separator from extension '{ext}'. "
                    f"Falling back to ',' for file {file_path}."
                )

        reader = TabularReader(file_path, role, **kwargs)

    elif format == "xlsx":
        reader = XlsxReader(file_path, role, **kwargs)

    else:
        logger.error(f"Unsupported format '{format}' for file {file_path}")
        return iter([])

    return reader.read()