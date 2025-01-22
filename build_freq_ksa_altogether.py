import pandas as pd
import sys
import os

def combine_ksa_lists(input_file, output_file):
    # Read the input file based on extension
    file_ext = os.path.splitext(input_file)[1].lower()
    if file_ext == '.xlsx':
        df = pd.read_excel(input_file)
    elif file_ext == '.csv':
        df = pd.read_csv(input_file)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Use .xlsx or .csv")
    
    # Initialize empty list to store all KSAs
    all_ksas = []
    
    # Iterate through each cell in KSA column
    for ksa_list in df['KSA'].dropna():
        # Split the KSA string into individual items and strip whitespace
        ksas = [ksa.strip() for ksa in ksa_list.split(',')]
        all_ksas.extend(ksas)
    
    # Write combined list to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for ksa in all_ksas:
            f.write(f"{ksa}\n")
    
    print(f"Combined KSA list has been exported to '{output_file}'")
    print(f"Total number of KSAs: {len(all_ksas)}")

def print_usage():
    print("Usage: python build_freq_ksa_altogether.py <input_file> <output_file>")
    print("Input file must be .xlsx or .csv")
    print("Output file should be .txt")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        combine_ksa_lists(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        print_usage()
        sys.exit(1)
