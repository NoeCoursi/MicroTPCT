# Exemple d'utilisation :

# from dataclasses import dataclass, field
# from typing import List

# @dataclass
# class Peptide:
#     id: str
#     seq: str
#     length: int = field(init=False)

#     def __post_init__(self):
#         self.length = len(self.seq)

#     def is_valid(self) -> bool:
#         """Check if sequence contains only standard amino acids."""
#         valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
#         return set(self.seq.upper()) <= valid_aa


# @dataclass
# class Protein:
#     id: str
#     seq: str
#     peptides: List[Peptide] = field(default_factory=list)
#     length: int = field(init=False)

#     def __post_init__(self):
#         self.length = len(self.seq)

#     def extract_peptides(self, min_len: int = 7, max_len: int = 30) -> List[Peptide]:
#         """Return list of Peptides from this protein sequence."""
#         self.peptides = [
#             Peptide(id=f"{self.id}_{i}", seq=self.seq[i:i+length])
#             for i in range(len(self.seq))
#             for length in range(min_len, max_len+1)
#             if i+length <= len(self.seq)
#         ]
#         return self.peptides
