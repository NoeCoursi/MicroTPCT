# MicroTPCT

***Microproteotypicity of Peptides – Computational Toolkit***

A computational toolkit designed to assess the proteotypicity of candidate microprotein peptides and resolve ambiguities in extended proteome analyses.

## Description

MicroTPCT is a bioinformatics toolkit designed to identify and evaluate candidate microproteins by matching peptides from alternative proteomes against canonical proteomes using multiple matching strategies. This software enables to process wildcards in the target file. This README provides an overview of the modules and their functionalities within the MicroTPCT project.

MicroTPCT is a framework that addresses the classical short-pattern / long-text matching problem supporting exact and wildcard-based matching with a unified result model.

The framework is primarily developed for peptide-to-protein matching in microproteomics, with an appropriate management of biological sequences, bioinformatics file reading and explicit support for ambiguous amino-acid symbols.

## Context

### Microproteins and alternative proteomes

Historically, an ORF was defined as a sequence starting with a START codon, ending with a STOP codon and having at least 100 codons. Shorter ORFs were usually ignored. However, since the 2010s, it has become apparent that small proteins, could also have important biological functions, for example in the regulation of key cellular processes, cell signaling or stress response. Their study is therefore particularly promising to better understand the functioning of cells and certain diseases.

Today, a new paradigm is emerging for the annotation of ORFs. In our work, we consider that an ORF can have a minimum size of 30 codons. The ORFs of 30 to 100 codons are called small-ORFs (smORFs), and the proteins from these smORFs are referred to here as microproteins. The set of microproteins is named alternative proteome.

### Microproteomics workflows and limitations

Due to the novelty of the field, there is not yet a standardized analysis strategy for the study of microproteins in proteomics. Similarly, no dedicated bioinformatics tool currently allows for specifically processing this type of data in large volumes.

A possible strategy for proteomic studies based on mass spectrometry is to perform a double analysis of the spectra, as opposed to a single analysis in the typical case. In a first step, the spectra of the injected peptides are matched to a database of canonical proteins, such as Uniprot, using tryptic search engines such as Mascot. In a second step, the spectra of unmatched peptides, i.e., those that do not belong to canonical proteins, are matched against a database of alternative proteins, including microproteins. The peptides found in the second step are peptides that potentially belong to microproteins. This two-step search workflow allows for control of the matching FDR.

### False positives in two-step search strategies

However, this method alone is not sufficient in the case of alternative in-vitro digestion of canonical peptides, rendering them semi-trypsic. These peptides, which are not matched in the first stage of the workflow, may, by chance, have a sequence identical to a trypsic microprotein peptide. In this case, the workflow identifies the peptides as belonging to a microprotein, even though the biological sample contained the canonical protein, creating a false positive.

MicroTPCT was developed precisely for the purpose of correcting these false positives by performing a robust and optimized text search of a list of peptides against a reference proteome. MicroTPCT allows users to systematically verify whether candidate peptides uniquely map to microproteins or also occur in canonical proteomes. From a computational perspective, this corresponds to large-scale matching of short peptide sequences against long protein sequences under controlled matching constraints.

## Installation

### Requirements (Python version, dependencies, OS)

Python version 3.12 or older is recommended

### Install from source

1. Clone the repository : 

```
git clone https://github.com/NoeCoursi/MicroTPCT.git
```

2. Create and activate a dedicated Python virtual environment (recommended) :
- Linux and macOS

```
python -m venv venv
source venv/bin/activate
```

- Windows

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install Python dependencies : 

```
pip install -r requirements.txt
```

4. Install MicroTPCT

```
cd MicroTPCT
pip install .

# editable mode for developpers
# pip install -e .

```

### Install GUI

If you don't want to install Python or use the command line, you can download the ready-to-use graphical version:

** Download here :**

https://github.com/NoeCoursi/MicroTPCT/releases

#### Windows

- Download `MicroTPCT.exe`
- Double-click on it to launch the application.

#### macOS

- Download `MicroTPCT.app`
- Clic droit → **Ouvrir** (la première fois, macOS peut bloquer les apps non signées)

#### Linux

**Debian/Ubuntu `.deb` package**

- Download the latest `MicroTPCT.deb`
- Install it with:

```bash
sudo apt install ./MicroTPCT.deb
```

Launch MicroTPCT from the Applications menu or by typing `MicroTPCT` in the terminal.

**AppImage (Universal)**

- Download  `MicroTPCT.AppImage`

```bash
chmod +x MicroTPCT.AppImage
./MicroTPCT.AppImage
```

Double-click the AppImage luncher. Make sure it’s executable.

**Portable `.tar.gz`**

- Download `MicroTPCT-linux.tar.gz` from the Releases page
- Extract the archive and run the `MicroTPCT` binary:

```bash
tar -xzf MicroTPCT-linux.tar.gz
./MicroTPCT
```

## Quick Start

MicroTPCT can be used either as a Python package or through its command-line interface (CLI).

### CLI

Basic syntax

```bash
microTPCT [options] QUERY_input TARGET_input
```

- **QUERY_input**: file containing peptides
- **TARGET_input**: file containing the canonical proteome used as reference

Wildcard handling

`--allow_wildcard`

Enable complementary regex searches for undetermined amino acids in the target file

A wildcard character **must** be specified when using this option.

Example : 

```
microTPCT --allow_wildcard X QUERY_input TARGET_input
```

For further details refer to document USAGE.txt in the docs folder. 

### GUI

MicroTPCT provides an optional **graphical user interface (GUI)** built with **Tkinter**, allowing users to run the peptide matching pipeline without using the command line.

Lauching the GUI

```python
python -m microtpct.interfaces.gui
```

## Pipeline

MicroTPCT implements the following workflow:

1. Read protein and peptide input files
2. Validate sequence integrity and detect ambiguous residues
3. Build optimized internal databases
4. Perform efficient strict exact matching
5. Perform optional wildcard-aware matching
6. Merge results and export summary tables

## Validation and Benchmarks

We benchmarked several exact peptide-to-proteome matching algorithms implemented in MicroTPCT.

We evaluate execution time, CPU usage, peak memory consumption, and correctness in order to guide default algorithm selection and user-level configuration.

The following algorithms are compared:

- Naive Python baseline (`str.find`) (reference method)
- Boyer–Moore
- Aho–Corasick (pure Python implementation)
- Aho–Corasick (Rust backend)
- System-level `grep + awk` launcher
- BLAST (included as a qualitative reference, not as a competitive exact matcher)

If you wish to compare performances of the different algorithms on your data we recommend you to go through the match_engine_benchmark jupyter notebook. 

Our benchmarking highlighted that :

- The naive str.find implementation provides a reliable but slow baseline.
- Multi-pattern algorithms (Aho–Corasick) scale better with increasing numbers of queries.
- System-level tools (grep/awk) offer competitive performance with minimal memory overhead.
- BLAST, while robust, is computationally overkill for exact peptide matching.

These results justify the default configuration of MicroTPCT and provide users
with practical guidance for selecting an appropriate matching engine.

## Authors and Affiliations

From INP ENSAT — Agrotoulouse : 
Basile Bergeron
https://www.linkedin.com/in/basile-bergeron-4665aa259/

Meredith Biteau
https://www.linkedin.com/in/meredithbf/

Ambre Bordas	
https://www.linkedin.com/in/ambre-bordas-52b287254/

Noé Coursimaux	
https://www.linkedin.com/in/noe-coursimaux/

Ambroise Loeb	
https://www.linkedin.com/in/ambroiseloeb/

