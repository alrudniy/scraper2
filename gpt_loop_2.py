import pandas as pd
import sys
from pgpt_python.client import PrivateGPTApi

def process_job_descriptions(filename, client):
    """
    Read Excel file and process job descriptions with delay
    """
    # Read Excel file
    df = pd.read_excel(filename)
    # remove rows with missing job description
    df = df[df['KSA'].notna()]

    # Add new KSA2 column
    df['KSA2'] = ''
    
    # Loop through each row
    for index, row in df.iterrows():
        # Get KSA
        job_desc = row['KSA']
        
        # Print to console
        print(f"\nKSA #{index + 1}:")
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
            prompt="""From the text in context, extract only knowledge, skills and abilities.
                      Return them as a simple comma-separated list. Remove any other comments. Do not add any comments.""",
            use_context=True,
            context_filter={"docs_ids": [ingested_text_doc_id]},
            include_sources=True,
        ).choices[0]

        print("\n>Contextual completion:")
        print(result.message.content)
        print(f" # Source: {result.sources[0].document.doc_metadata['file_name']}")
        
        # Save KSAs to DataFrame
        df.at[index, 'KSA2'] = result.message.content
        
        print("-" * 50)
        # Wait for user input to continue
        # input("\nPress Enter to continue to next job description...")
    
    # Export DataFrame to Excel with KSAs
    output_filename = filename.replace('.xlsx', '_with_KSA_2.xlsx')
    df.to_excel(output_filename, index=False)
    print(f"\nProcessing complete. Results saved to {output_filename}")

def main():
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=600000)
    
    sys.stdout.reconfigure(encoding='utf-8')
    #input_file = 'combined_output_20250116_191158_unduplicated.xlsx'
    # input_file = 'compound_semiconductors_jobs_20250226_224938.xlsx'
    # input_file = 'radiation_hardening_jobs_20250226_222300.xlsx'
    # input_file = 'system_on_chip_jobs_20250226_223206.xlsx'
    input_file = 'radiation_hardening_jobs_20250226_222300_with_KSA.xlsx'
    process_job_descriptions(input_file, client)

if __name__ == "__main__":
    main()
