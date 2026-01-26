from microtpct.utils.data_generator import generate_benchmark_databases

_, _, _, _ = generate_benchmark_databases(
    n_proteins = 2000,
    protein_mean_length = 700,
    protein_std_length = 100,
    x_rate = 0.005,

    n_peptides = 200,
    peptide_mean_length = 30,
    peptide_std_length = 5,
    match_fraction = 0.5,
    quasi_fraction = 0.05,

    redundancy_rate = 0.01,
    mutation_rate = 0.05,

    seed = 42,

    export_target_fasta_path = "proteome.fasta",
    export_query_xlsx_path  = "peptides.xlsx",
)