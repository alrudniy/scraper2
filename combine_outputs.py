import pandas as pd
import os
import glob
from datetime import datetime
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

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
    
    # Remove Benefits and Responsibilities columns
    combined_df = combined_df.drop(['Benefits', 'Responsibilities'], axis=1)
    
    # Sort the dataframe
    combined_df = combined_df.sort_values(['Title', 'Company', 'Keyword'])
    
    # Add Duplicate Flag column
    combined_df['Duplicate Flag'] = ''
    
    # Mark duplicates
    duplicate_mask = combined_df.duplicated(subset=['Title', 'Company'], keep='first')
    combined_df.loc[duplicate_mask, 'Duplicate Flag'] = 'Y'
    # Mark first occurrence of duplicates
    first_duplicate_mask = combined_df.duplicated(subset=['Title', 'Company'], keep='last')
    combined_df.loc[first_duplicate_mask & ~duplicate_mask, 'Duplicate Flag'] = '1'
    
    # Reorder columns to put Duplicate Flag after Keyword
    cols = combined_df.columns.tolist()
    cols.remove('Duplicate Flag')
    cols.insert(1, 'Duplicate Flag')
    combined_df = combined_df[cols]
    
    # Save combined data with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'combined_output_{timestamp}.xlsx'
    combined_df.to_excel(output_file, index=False)

    # Apply Excel formatting
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
        ws = writer.book.active

    # Freeze top row and left column
    ws.freeze_panes = 'B2'

    # Center align headers
    for cell in ws[1]:
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # Set alignment for all cells except headers
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Set row heights (starting from row 2)
    for row in range(2, ws.max_row + 1):
        ws.row_dimensions[row].height = 200

    # Set column widths
    width_22_cols = ['C', 'D', 'E', 'F']  # Title, Company, Location, Timestamp
    ws.column_dimensions['A'].width = 14  # Keyword column
    ws.column_dimensions['B'].width = 10  # Duplicate Flag column
    width_50_cols = ['G', 'H', 'I']  # Job Highlights, Qualifications, Job Description
    width_10_cols = ['J', 'K', 'L', 'M', 'N', 'O']  # Boolean columns
    width_20_cols = ['P', 'Q', 'R', 'S', 'T']  # Evidence columns

    for col in width_22_cols:
        ws.column_dimensions[col].width = 22
    for col in width_50_cols:
        ws.column_dimensions[col].width = 50
    for col in width_10_cols:
        ws.column_dimensions[col].width = 10
    for col in width_20_cols:
        ws.column_dimensions[col].width = 20

    # Add autofilter and apply filter to hide rows with 'Y' in Duplicate Flag
    ws.auto_filter.ref = ws.dimensions
    ws.auto_filter.add_filter_column(1, ["1", ""])  # Column B (index 1) for Duplicate Flag

    # Save the workbook with formatting
    writer.book.save(output_file)
    print(f"Combined data saved to {output_file}")

if __name__ == "__main__":
    combine_excel_files()
