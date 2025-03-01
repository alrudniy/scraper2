import pandas as pd
import sys
from pgpt_python.client import PrivateGPTApi

def process_job_descriptions(filename, client):
    """
    Read Excel file and clean KSA
    """
    # Read Excel file
    df = pd.read_excel(filename)
    
    # Add new KSA column
    df['KSA Cleaned'] = ''
    
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
            # prompt="""Remove comment that appears in the end similar to this: 
            # Let me know if you'd like me to reformat this list for you!""",
            
            prompt="""Remove comment that appears in the end similar to this: 
            I included "English Read Write Speak" since it's mentioned as a language proficiency requirement. 
            Output must be just cleaned text, no additional comments such as Here is revised text.
            """,
            
            use_context=True,
            context_filter={"docs_ids": [ingested_text_doc_id]},
            include_sources=True,
        ).choices[0]

        print("\n>Contextual completion:")
        print(result.message.content)
        print(f" # Source: {result.sources[0].document.doc_metadata['file_name']}")
        
        # Save KSAs to DataFrame
        df.at[index, 'KSA Cleaned'] = result.message.content
        
        print("-" * 50)
        # Wait for user input to continue
        # input("\nPress Enter to continue to next job description...")
    
    # Export DataFrame to Excel with KSAs
    output_filename = filename.replace('.xlsx', ' v3.xlsx')
    df.to_excel(output_filename, index=False)
    print(f"\nProcessing complete. Results saved to {output_filename}")

def main():
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=60000)
    
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Manually removed couple of phrases in KSA column
    input_file = 'combined_output_20250116_191158_unduplicated_with_KSA v2.xlsx'
    
    process_job_descriptions(input_file, client)

if __name__ == "__main__":
    main()
