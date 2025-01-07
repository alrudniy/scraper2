import json
import csv
from datetime import datetime

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
        
    except FileNotFoundError:
        print("Error: job_listings.json file not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in job_listings.json")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    convert_json_to_csv()
