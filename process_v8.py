import pandas as pd

def process_ksa_frequencies():
    # Read the Excel file
    df = pd.read_excel('ksa_frequencies_v8.xlsx')
    
    # Group by KSA and sum frequencies
    df = df.groupby('KSA')['Frequency'].sum().reset_index()
    
    # Sort by frequency in descending order
    df = df.sort_values('Frequency', ascending=False)
    
    # Export to Excel
    output_file = 'ksa_frequencies_v9.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Processed KSA frequencies have been exported to '{output_file}'")
    print(f"Total unique KSAs: {len(df)}")
    print(f"Total occurrences: {df['Frequency'].sum()}")

if __name__ == "__main__":
    process_ksa_frequencies()
