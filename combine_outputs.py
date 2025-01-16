import pandas as pd
import os
import glob
from datetime import datetime

def extract_keyword(filename):
    # Get base filename without path and extension
    base = os.path.splitext(os.path.basename(filename))[0]
    # Get first part before timestamp (everything before last 2 segments)
    keyword_parts = base.rsplit('_', 2)[0]
    # Replace remaining underscores with spaces
    return keyword_parts.replace('_', ' ')

def combine_excel_files():
    # Get all xlsx files in the xlsx directory
    excel_files = glob.glob('xlsx/*.xlsx')
    
    if not excel_files:
        print("No Excel files found in xlsx directory")
        return
    
    # List to store individual dataframes
    dfs = []
    
    for file in excel_files:
        # Read Excel file
        df = pd.read_excel(file)
        # Extract keyword from filename
        keyword = extract_keyword(file)
        # Add keyword column
        df.insert(0, 'Keyword', keyword)
        # Append to list
        dfs.append(df)
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Save combined data with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'combined_output_{timestamp}.xlsx'
    combined_df.to_excel(output_file, index=False)
    print(f"Combined data saved to {output_file}")

if __name__ == "__main__":
    combine_excel_files()
