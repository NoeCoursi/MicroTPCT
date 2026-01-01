# Exemple d'utilisation :

# from dataclasses import dataclass

# @dataclass
# class Peptide:
#     id: str
#     seq: str
#     length: int = None

#     def __post_init__(self):
#         if self.length is None:
#             self.length = len(self.seq)

# @dataclass
# class Protein:
#     id: str
#     seq: str
#     peptides: list[Peptide] = None

# @dataclass
# class Result:
#     peptide_id: str
#     proteotypic_score: float
#     uniqueness: float