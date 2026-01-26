from microtpct.utils.data_generator import generate_benchmark_databases
from microtpct.core.match import get_engine

engine_name = "find"

config = {"negative_only": dict(
        n_proteins=5000,
        protein_mean_length=500,
        protein_std_length=50,
        x_rate=0.0,
        n_peptides=5000,
        peptide_mean_length=30,
        peptide_std_length=2,
        match_fraction=0.5,
        quasi_fraction=0.0,
        redundancy_rate=0.0,
        mutation_rate=0.0,
        seed=4,
    )}

target_db, query_db, config = generate_benchmark_databases(**config["negative_only"])
algo_func = get_engine(engine_name)

print(target_db.to_dataframe())
print(query_db.to_dataframe())

result = algo_func(target_db, query_db)

print(result.to_dataframe())