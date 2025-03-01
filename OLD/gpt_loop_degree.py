import pandas as pd
import sys
from pgpt_python.client import PrivateGPTApi

def process_job_descriptions(filename, client):
    """
    Read Excel file and clean KSA
    """
    # Read Excel file
    df = pd.read_excel(filename)
    
    # Add new columns
    df['Degree'] = ''
    df['doc_id'] = ''
    
    # Loop through each row
    for index, row in df.iterrows():
        # Get 
        job_desc = row['Job Description']
        
        # Print to console
        print(f"\nJob Description #{index + 1}:")
        print("-" * 50)
        print(job_desc)

        
        # Ingestion of Text:
        ingested_text_doc_id = (
            client.ingestion.ingest_text(file_name=str(index + 1), text=job_desc)
            .data[0]
            .doc_id
        )
        print("Ingested text doc id: ", ingested_text_doc_id)
        

        
        # Contextual Completion:
        result = client.contextual_completions.prompt_completion(
            prompt="""Extract required degrees. Output must be just degrees, no additional comments.
            """,
            
            use_context=True,
            context_filter={"docs_ids": [ingested_text_doc_id]},
            include_sources=True,
        ).choices[0]

        print("\n>Contextual completion:")
        print(result.message.content)
        print(f" # Source: {result.sources[0].document.doc_metadata['file_name']}")
        
        # Save to DataFrame
        df.at[index, 'Degree'] = result.message.content
        df.at[index, 'doc_id'] = ingested_text_doc_id
        
        print("-" * 50)
        # Wait for user input to continue
        # input("\nPress Enter to continue to next job description...")
    
    # Export DataFrame to Excel with KSAs
    output_filename = filename.replace('.xlsx', ' with degree.xlsx')
    df.to_excel(output_filename, index=False)
    print(f"\nProcessing complete. Results saved to {output_filename}")

def main():
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=600000)
    
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Manually removed couple of phrases in KSA column
    input_file = 'combined_output_20250116_191158_unduplicated_with_KSA v2.xlsx'
    
    process_job_descriptions(input_file, client)

if __name__ == "__main__":
    main()
