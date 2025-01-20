import pandas as pd
from collections import Counter

def build_ksa_frequencies():
    # Read the CSV file
    df = pd.read_csv("combined_output_20250116_191158_unduplicated_with_KSA v2 with degree.xlsx - Sheet1.csv")
    
    # Get all KSAs and convert to lowercase
    all_ksas = []
    for ksa_list in df['KSA'].dropna():
        # Split the KSA string into individual items and convert to lowercase
        ksas = [ksa.strip().lower() for ksa in ksa_list.split(',')]
        all_ksas.extend(ksas)
    
    # Calculate frequencies using Counter
    ksa_frequencies = Counter(all_ksas)
    
    # Convert to DataFrame and sort by frequency
    freq_df = pd.DataFrame.from_dict(ksa_frequencies, orient='index', columns=['Frequency'])
    freq_df.index.name = 'KSA'
    freq_df = freq_df.sort_values('Frequency', ascending=False)
    
    # Export to Excel
    freq_df.to_excel('KSA frequencies.xlsx')
    print(f"Frequency table has been exported to 'KSA frequencies.xlsx'")

if __name__ == "__main__":
    build_ksa_frequencies()
