import pandas as pd

def combine_ksa_lists():
    # Read the Excel file
    df = pd.read_excel('KSAs only.xlsx')
    
    # Initialize empty list to store all KSAs
    all_ksas = []
    
    # Iterate through each cell in KSA column
    for ksa_list in df['KSA'].dropna():
        # Split the KSA string into individual items and strip whitespace
        ksas = [ksa.strip() for ksa in ksa_list.split(',')]
        all_ksas.extend(ksas)
    
    # Write combined list to text file
    with open('ksa_list.txt', 'w', encoding='utf-8') as f:
        for ksa in all_ksas:
            f.write(f"{ksa}\n")
    
    print(f"Combined KSA list has been exported to 'ksa_list.txt'")
    print(f"Total number of KSAs: {len(all_ksas)}")

if __name__ == "__main__":
    combine_ksa_lists()
