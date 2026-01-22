from microtpct.io.schema import ProteinInput, PeptideInput
from microtpct.io.validators import *

# Creates protein
prot = ProteinInput(
    id="protA",
    accession="P12345",
    sequence="MKTAYIAKQRQISFVKSHFSRQ"
)

print(prot)
print(prot.sequence)

pep = PeptideInput(
    id="pepA_1",
    accession="P12345",
    sequence="KSHBSZ"
)

print(pep)
validate_protein_input(prot)
validate_peptide_input(pep)