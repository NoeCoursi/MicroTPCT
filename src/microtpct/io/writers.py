# FOR GUI MINIMAL TESTING
# In your io/writers.py or wherever results are saved
import pandas as pd

def save_match_results(match_results, output_path):
    """Convert MatchResult objects to DataFrame and save as Excel"""
    # Convert MatchResult objects to dictionaries
    results_data = []
    for result in match_results:
        results_data.append(vars(result))  # Convert object to dict
    
    df = pd.DataFrame(results_data)
    df.to_excel(output_path, index=False)