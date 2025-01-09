import json
import csv
import openpyxl
import os
from datetime import datetime
from openpyxl.styles import Font, PatternFill, Alignment

def flatten_list(items, for_excel=False):
    """Convert a list of items to a separated string
    Args:
        items: List of items to flatten
        for_excel: If True, use newlines, otherwise use semicolons
    """
    if not items:
        return ""
    separator = "\n" if for_excel else "; "
    return separator.join(str(item) for item in items)

def convert_json_to_csv(input_file=None):
    if not input_file:
        print("Error: Input JSON file name is required")
        print("Usage: python json_to_csv.py <input_json_file>")
        return

    try:
        # Read JSON file
        with open(input_file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            job_listings = data.get('job_listings', [])

        # Define CSV headers
        csv_headers = [
            'Title',
            'Company',
            'Location',
            'Timestamp',
            'Job Highlights',
            'Job Highlights Items',
            'Qualifications',
            'Qualifications Items',
            'Benefits',
            'Benefits Items',
            'Responsibilities',
            'Responsibilities Items',
            'Job Description'
        ]
        
        # Define Excel headers (excluding Items columns)
        excel_headers = [
            'Title',
            'Company',
            'Location',
            'Timestamp',
            'Job Highlights',
            'Qualifications',
            'Benefits',
            'Responsibilities',
            'Job Description'
        ]

        # Create csv directory if it doesn't exist
        if not os.path.exists('csv'):
            os.makedirs('csv')
            
        # Create output filename for CSV in csv folder
        base_name = os.path.basename(input_file).rsplit('.', 1)[0]
        output_csv = os.path.join('csv', base_name + '.csv')
        
        # Write to CSV file
        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
            writer.writeheader()

            for job in job_listings:
                writer.writerow({
                    'Title': job.get('title', ''),
                    'Company': job.get('company', ''),
                    'Location': job.get('location', ''),
                    'Timestamp': job.get('timestamp', ''),
                    'Job Highlights': job.get('job_highlights_text', ''),
                    'Job Highlights Items': flatten_list(job.get('job_highlights_items', [])),
                    'Qualifications': job.get('qualifications_text', ''),
                    'Qualifications Items': flatten_list(job.get('qualifications_items', [])),
                    'Benefits': job.get('benefits_text', ''),
                    'Benefits Items': flatten_list(job.get('benefits_items', [])),
                    'Responsibilities': job.get('responsibilities_text', ''),
                    'Responsibilities Items': flatten_list(job.get('responsibilities_items', [])),
                    'Job Description': job.get('job_description', '')
                })

        print(f"Successfully converted job listings to CSV format. Output saved to {output_csv}")

        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Job Listings"

        # Add headers with formatting
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Freeze the top row
        ws.freeze_panes = 'A2'
        
        for col, header in enumerate(excel_headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            # Set alignment for header
            cell.alignment = openpyxl.styles.Alignment(horizontal='left', vertical='top', wrap_text=True)

        # Add data
        for row_idx, job in enumerate(job_listings, 2):
            # Create cells with data and formatting
            cells = [
                (1, job.get('title', '')),
                (2, job.get('company', '')),
                (3, job.get('location', '')),
                (4, job.get('timestamp', '')),
                (5, job.get('job_highlights_text', '')),
                (6, job.get('qualifications_text', '')),
                (7, job.get('benefits_text', '')),
                (8, job.get('responsibilities_text', '')),
                (9, job.get('job_description', ''))
            ]
            
            for col, value in cells:
                cell = ws.cell(row=row_idx, column=col, value=value)
                cell.alignment = openpyxl.styles.Alignment(horizontal='left', vertical='top', wrap_text=True)

        # Adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = openpyxl.utils.get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = min(len(str(cell.value)), 100)  # Cap at 100 characters
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Create xlsx directory if it doesn't exist
        if not os.path.exists('xlsx'):
            os.makedirs('xlsx')
            
        # Create output filename in xlsx folder
        base_name = os.path.basename(input_file).rsplit('.', 1)[0]
        output_excel = os.path.join('xlsx', base_name + '.xlsx')
        
        # Save Excel file
        wb.save(output_excel)
        print(f"Successfully exported to Excel format. Output saved to {output_excel}")
        
    except FileNotFoundError:
        print("Error: job_listings.json file not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in job_listings.json")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        convert_json_to_csv()  # Will print usage message
    else:
        convert_json_to_csv(sys.argv[1])
