import json
import csv
import openpyxl
from datetime import datetime
from openpyxl.styles import Font, PatternFill

def flatten_list(items):
    """Convert a list of items to a semicolon-separated string"""
    if not items:
        return ""
    return "; ".join(str(item) for item in items)

def convert_json_to_csv():
    try:
        # Read JSON file
        with open('job_listings.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            job_listings = data.get('job_listings', [])

        # Define CSV headers
        headers = [
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

        # Write to CSV file
        with open('job_listings.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
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

        print(f"Successfully converted job listings to CSV format. Output saved to job_listings.csv")

        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Job Listings"

        # Add headers with formatting
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill

        # Add data
        for row_idx, job in enumerate(job_listings, 2):
            ws.cell(row=row_idx, column=1, value=job.get('title', ''))
            ws.cell(row=row_idx, column=2, value=job.get('company', ''))
            ws.cell(row=row_idx, column=3, value=job.get('location', ''))
            ws.cell(row=row_idx, column=4, value=job.get('timestamp', ''))
            ws.cell(row=row_idx, column=5, value=job.get('job_highlights_text', ''))
            ws.cell(row=row_idx, column=6, value=flatten_list(job.get('job_highlights_items', [])))
            ws.cell(row=row_idx, column=7, value=job.get('qualifications_text', ''))
            ws.cell(row=row_idx, column=8, value=flatten_list(job.get('qualifications_items', [])))
            ws.cell(row=row_idx, column=9, value=job.get('benefits_text', ''))
            ws.cell(row=row_idx, column=10, value=flatten_list(job.get('benefits_items', [])))
            ws.cell(row=row_idx, column=11, value=job.get('responsibilities_text', ''))
            ws.cell(row=row_idx, column=12, value=flatten_list(job.get('responsibilities_items', [])))
            ws.cell(row=row_idx, column=13, value=job.get('job_description', ''))

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

        # Save Excel file
        wb.save('job_listings.xlsx')
        print("Successfully exported to Excel format. Output saved to job_listings.xlsx")
        
    except FileNotFoundError:
        print("Error: job_listings.json file not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in job_listings.json")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    convert_json_to_csv()
