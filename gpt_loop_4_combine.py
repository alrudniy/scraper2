import json
import sys
from openpyxl import load_workbook
import pandas as pd
import sys

def main(excel_file):
    """
    Read Excel file and process job descriptions with delay
    """
    # Read Excel file
    df = pd.read_excel(excel_file)
    # remove rows with missing job description
    df = df[df['KSA3'].notna()]

    # Initialize an empty list to store the combined data
    combined_data = []
    
    # Loop through each row
    for index, row in df.iterrows():
        # Get KSA
        ksa3_data = row['KSA3']
        
        try:
            # Parse the JSON data in 'KSA3' column
            ksa3_list = json.loads(ksa3_data)
            combined_data.extend(ksa3_list)
        except json.JSONDecodeError:
            print(f"Invalid JSON data in row {row[0]}: {ksa3_data}")

    # Generate the output JSON file name
    output_filename = excel_file.replace('.xlsx', '.json')
    # Save the combined data to a JSON file
    with open(output_filename, 'w') as json_file:
        json.dump(combined_data, json_file)

    print(f"Combined data saved to {output_filename}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gpt_loop_4_combine.py <excel_file>")
        sys.exit(1)

    excel_file = sys.argv[1]
    main(excel_file)
