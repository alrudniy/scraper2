import pandas as pd
import time

def process_job_descriptions(filename):
    """
    Read Excel file and process job descriptions with delay
    """
    # Read Excel file
    df = pd.read_excel(filename)
    
    # Loop through each row
    for index, row in df.iterrows():
        # Get job description
        job_desc = row['Job Description']
        
        # Print to console
        print(f"\nJob Description #{index + 1}:")
        print("-" * 50)
        print(job_desc)
        print("-" * 50)
        
        # Wait 2 seconds
        time.sleep(2)

def main():
    input_file = 'combined_output_20250116_191158_unduplicated.xlsx'
    process_job_descriptions(input_file)

if __name__ == "__main__":
    main()
