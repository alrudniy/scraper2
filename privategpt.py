import pandas as pd
from pgpt import PGPT
from collections import Counter
import re

def extract_ksas(text):
    """Extract Knowledge, Skills and Abilities from text using PrivateGPT"""
    prompt = f"""
    From the following job description, extract all mentioned knowledge, skills and abilities (KSAs).
    Return them as a simple comma-separated list.
    Job description: {text}
    """
    
    # Initialize PGPT client
    pgpt = PGPT()
    
    # Get response
    response = pgpt.chat(prompt)
    
    # Split response into individual KSAs and clean
    ksas = [ksa.strip() for ksa in response.split(',')]
    return ksas

def main():
    # Read the CSV file
    df = pd.read_csv('combined_output_20250116_191158_unduplicated job descriptions only.csv')
    
    # Extract job descriptions
    job_descriptions = df['job_description'].tolist()
    
    # Process each job description
    all_ksas = []
    for jd in job_descriptions:
        try:
            ksas = extract_ksas(jd)
            all_ksas.extend(ksas)
        except Exception as e:
            print(f"Error processing job description: {e}")
    
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
