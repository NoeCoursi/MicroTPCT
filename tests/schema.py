from microtpct.io.schema import ProteinInput, PeptideInput

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
    sequence="KSHFSR"
)

print(pep)