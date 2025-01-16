import os
import pandas as pd
import google.generativeai as genai

# Configure the Gemini API
GEMINI_API_KEY = 'AIzaSyA0-UU_294arcyvdVIEHQct0_I7edoBpoI'
genai.configure(api_key=GEMINI_API_KEY)

def analyze_job_description(description):
    """
    Analyze job description using Gemini to determine if it's entry-level
    Returns tuple of (yes/no answer, evidence)
    """
    # Configure the model
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Analyze this job description and determine if it's an entry-level position.
    Format your response exactly as follows:
    First line: Either "Yes" or "No"
    Second line: If Yes, explain why in 1-2 sentences. If No, explain why not in 1-2 sentences.
    
    Job Description:
    {description}
    """
    
    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n', 1)
        answer = lines[0].strip()
        evidence = lines[1].strip() if len(lines) > 1 else "No evidence provided"
        return answer, evidence
    except Exception as e:
        return "Error", f"Error analyzing description: {str(e)}"

def process_excel_file(filename):
    """
    Process Excel file and add entry-level analysis
    """
    try:
        # Read the Excel file
        df = pd.read_excel(filename)
        
        # Check if 'Job Description' column exists
        if 'Job Description' not in df.columns:
            raise ValueError("Excel file must contain a 'Job Description' column")
            
        # Create new columns for analysis
        df['Is Entry Level?'], df['Is Entry Level - Evidence'] = zip(*df['Job Description'].apply(
            lambda x: analyze_job_description(str(x)) if pd.notna(x) else ("No", "No description provided")
        ))
        
        # Save updated file
        output_filename = filename.replace('.xlsx', '_analyzed.xlsx')
        df.to_excel(output_filename, index=False)
        print(f"Analysis complete. Results saved to: {output_filename}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def main():
    input_file = os.path.join('xlsx', 'Accountability_AI_intern_20250108_151747.xlsx')
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return
        
    process_excel_file(input_file)

if __name__ == "__main__":
    main()
