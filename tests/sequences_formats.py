from microtpct.core.sequences import ProteinSequence, PeptideSequence

# Creates protein
prot = ProteinSequence(
    id="protA",
    accession="P12345",
    sequence="MKTAYIAKQRQISFVKSHFSRQ"
)

print(prot)
print("Length:", prot.length)

# Creates peptide which is part of previously define protein (same accession)
pep = PeptideSequence(
    id="pepA_1",
    accession="P12345",
    sequence="KSHFSR"
)

print(pep)
print("Length:", pep.length)

# Creates peptide whitout accession
pep2 = PeptideSequence(
    id="pepA_2",
    accession="",
    sequence="TAYIAKQ"
)