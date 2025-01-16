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
    width_22_cols = ['B', 'C', 'D', 'E']  # Title, Company, Location, Timestamp
    ws.column_dimensions['A'].width = 14  # Keyword column
    width_50_cols = ['F', 'G', 'H', 'I', 'J']  # Job Highlights, Qualifications, Benefits, Responsibilities, Job Description
    width_10_cols = ['K', 'L', 'M', 'N', 'O', 'P']  # Boolean columns
    width_20_cols = ['Q', 'R', 'S', 'T', 'U']  # Evidence columns

    for col in width_22_cols:
        ws.column_dimensions[col].width = 22
    for col in width_50_cols:
        ws.column_dimensions[col].width = 50
    for col in width_10_cols:
        ws.column_dimensions[col].width = 10
    for col in width_20_cols:
        ws.column_dimensions[col].width = 20

    # Save the workbook with formatting
    writer.book.save(output_file)
    print(f"Combined data saved to {output_file}")

if __name__ == "__main__":
    combine_excel_files()
