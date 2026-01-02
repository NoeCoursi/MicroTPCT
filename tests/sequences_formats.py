from microtpct.core.sequences import ProteinSequence, PeptideSequence
from microtpct.core.registry import PeptideDatabase

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

pep2 = PeptideSequence(
    id="pepA_2",
    accession="P12345",
    sequence="TAYIAKQ"
)

pep3 = PeptideSequence(
    id="pepB_1",
    accession="P54321",
    sequence="TAYIA"
)


# Testing registry

db = PeptideDatabase()

db.add(pep)
db.add(pep2)
db.add(pep3)

# All peptides
print(db.all())

# Peptides by accession
print(db.get_by_accession("P12345"))

# Unique accessions
print(db.get_unique_accessions())

# Peptides containing motif "KSH"
print(db.get_by_motif("YIA"))
