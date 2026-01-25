from microtpct.core.pipeline import run_pipeline

run_pipeline(
    target_file = r"C:\Users\huawei\Desktop\uniprotkb_proteome_UP000000803_2025_11_25.fasta",
    query_file = r"c:\Users\huawei\Desktop\Drosophila Microproteome Openprot 2025-10-09 all conditions_2025-11-24_1613.xlsx",
    allow_wildcard = True,
    matching_engine = "find",
    analysis_name = "Test of MicroTPCT",
    # log_file="logs/test_pipeline.log",

    # wildcards = ["X", "?"]
)