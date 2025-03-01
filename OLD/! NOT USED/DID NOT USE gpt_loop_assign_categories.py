import pandas as pd
import sys
from pgpt_python.client import PrivateGPTApi

def process_job_descriptions(filename, client):
    """
    Read Excel file and process job descriptions with delay
    """
    # Read Excel file
    df = pd.read_excel(filename)
    
    # Add new Category column
    df['Category'] = ''
    
    # Loop through each row
    for index, row in df.iterrows():
        # Get job description
        ksa = row['KSA']
        
        # Print to console
        print(f"\nKSA #{index + 1}:")
        print("-" * 50)
        print(ksa)

        
        # Ingestion of Text:
        ingested_text_doc_id = (
            client.ingestion.ingest_text(file_name=str(index + 1), text=ksa)
            .data[0]
            .doc_id
        )
        print("Ingested text doc id: ", ingested_text_doc_id)
        

        
        # Contextual Completion:
        result = client.contextual_completions.prompt_completion(
            prompt="""
                Categorize text as one of these:
                Technical Skills, Soft Skills, Domain Knowledge, Educational Background & Certifications, Experience .
                Return only category. Do not make any comments. 
            """,
            use_context=True,
            context_filter={"docs_ids": [ingested_text_doc_id]},
            include_sources=True,
        ).choices[0]

        print("\n>Contextual completion:")
        print(result.message.content)
        print(f" # Source: {result.sources[0].document.doc_metadata['file_name']}")
        
        # Save Category to DataFrame
        df.at[index, 'Category'] = result.message.content
        
        print("-" * 50)
        # Wait for user input to continue
        # input("\nPress Enter to continue to next description...")
    
    # Export DataFrame to Excel with Categories
    output_filename = filename.replace('ksa_frequencies_v11_from_privategpt.xlsx')
    df.to_excel(output_filename, index=False)
    print(f"\nProcessing complete. Results saved to {output_filename}")

def main():
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=60000)
    
    sys.stdout.reconfigure(encoding='utf-8')
    input_file = 'ksa_frequencies_v10_manual.xlsx'
    process_job_descriptions(input_file, client)

if __name__ == "__main__":
    main()
