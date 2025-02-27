from collections import Counter
import pandas as pd

def group_and_count_ksa():
    # Read the text file
    with open('ksa_list_from_v5_processed.txt', 'r', encoding='utf-8') as f:
        phrases = [line.strip() for line in f if line.strip()]
    
    # Count occurrences using Counter
    phrase_counts = Counter(phrases)
    
    # Convert to DataFrame
    df = pd.DataFrame.from_records(
        [(phrase, count) for phrase, count in phrase_counts.items()],
        columns=['Phrase', 'Count']
    )
    
    # Sort by count in descending order
    df = df.sort_values('Count', ascending=False)
    
    # Export to CSV
    output_file = 'ksa_grouped_counts.csv'
    df.to_csv(output_file, index=False)
    print(f"Grouped KSAs have been exported to '{output_file}'")
    print(f"Total unique phrases: {len(df)}")
    print(f"Total occurrences: {df['Count'].sum()}")

if __name__ == "__main__":
    group_and_count_ksa()
