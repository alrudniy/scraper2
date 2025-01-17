import pandas as pd
from pgpt_python.client import PrivateGPTApi
from collections import Counter
import re

def extract_ksas():
    """Extract Knowledge, Skills and Abilities from text using PrivateGPT"""
    prompt = f"""
    From the following job description, extract all mentioned knowledge, skills and abilities (KSAs).
    Return them as a simple comma-separated list.
    
    """
    #Job description: {text}
    
    # Get response
    response = client.contextual_completions.prompt_completion(prompt, use_context=True,include_sources=True,).choices[0]
    
    # Split response into individual KSAs and clean
    ksas = [ksa.strip() for ksa in response.split(',')]
    return ksas

def main():
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001")
    
    # Ingestion of File:
    with open("combined_output_20250116_191158_unduplicated.csv", "rb") as f:
        ingested_file_doc_id = client.ingestion.ingest_file(file=f).data[0].doc_id
    
   
    # Process each job description
    all_ksas = extract_ksas()

    """ try:
        ksas = extract_ksas(jd)
        all_ksas.extend(ksas)
    except Exception as e:
        print(f"Error: {e}") """
    
    # Create frequency table
    ksa_freq = Counter(all_ksas)
    
    # Convert to DataFrame for better display
    freq_df = pd.DataFrame.from_dict(ksa_freq, orient='index', columns=['Frequency'])
    freq_df.index.name = 'KSA'
    freq_df = freq_df.sort_values('Frequency', ascending=False)
    
    # Save results
    freq_df.to_csv('ksa_frequency_table.csv')
    print("KSA frequency analysis complete. Results saved to ksa_frequency_table.csv")

if __name__ == "__main__":
    main()
