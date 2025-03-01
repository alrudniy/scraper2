from collections import Counter
import pandas as pd

def get_ksa_frequencies():
    # Read the text file
    with open('ksa_list_from_v5_processed.txt', 'r', encoding='utf-8') as f:
        phrases = [line.strip() for line in f if line.strip()]
    
    # Count occurrences using Counter
    phrase_counts = Counter(phrases)
    
    # Convert to DataFrame
    df = pd.DataFrame.from_records(
        [(phrase, count) for phrase, count in phrase_counts.items()],
        columns=['KSA', 'Frequency']
    )
    
    # Sort by frequency in descending order
    df = df.sort_values('Frequency', ascending=False)
    
    # Export to Excel
    output_file = 'ksa_frequencies_v6.xlsx'
    df.to_excel(output_file, index=False)
    print(f"KSA frequencies have been exported to '{output_file}'")
    print(f"Total unique KSAs: {len(df)}")
    print(f"Total occurrences: {df['Frequency'].sum()}")

if __name__ == "__main__":
    get_ksa_frequencies()
