import pandas as pd

def combine_ksa_lists():
    # Read the Excel file
    df = pd.read_excel('combined_output_20250116_191158_unduplicated_with_KSA v4.xlsx')
    
    # Initialize empty list to store all KSAs
    all_ksas = []
    
    # Iterate through each cell in KSA Cleaned column
    for ksa_list in df['KSA Cleaned'].dropna():
        # Split the KSA string into individual items and strip whitespace
        ksas = [ksa.strip() for ksa in ksa_list.split(',')]
        all_ksas.extend(ksas)
    
    # Write combined list to text file
    with open('ksa_list_v2.txt', 'w', encoding='utf-8') as f:
        for ksa in all_ksas:
            f.write(f"{ksa}\n")
    
    print(f"Combined KSA list has been exported to 'ksa_list_v2.txt'")
    print(f"Total number of KSAs: {len(all_ksas)}")

if __name__ == "__main__":
    combine_ksa_lists()
