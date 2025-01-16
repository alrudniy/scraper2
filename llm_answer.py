import os
import pandas as pd
import google.generativeai as genai

# Configure the Gemini API
GEMINI_API_KEY = 'AIzaSyA0-UU_294arcyvdVIEHQct0_I7edoBpoI'
genai.configure(api_key=GEMINI_API_KEY)

def analyze_job_description(description):
    """
    Analyze job description using Gemini to determine if it's entry-level, minimum degree required,
    if it's an engineering position, if it's an administrative position, and if it's a trustworthy AI position
    Returns tuple of (yes/no answer, evidence, minimum degree, is_engineering, engineering_evidence, is_admin, admin_evidence, is_trustworthy_ai, trustworthy_ai_evidence)
    """
    # Configure the model
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Analyze this job description and provide seven pieces of information:
    1. Is this an entry-level position?
    2. What is the minimum degree required?
    3. Is this an engineering position?
    4. Is this an administrative position?
    5. Is this a trustworthy AI position?
    6. Is this an internship position?
    7. What are the required Knowledge, Skills, and Abilities (KSAs)?

    Format your response exactly as follows:
    Line 1: Either "Yes" or "No" (for entry-level)
    Line 2: If Yes, explain why in 1-2 sentences. If No, explain why not in 1-2 sentences.
    Line 3: Minimum degree required (e.g., "Bachelor's", "Master's", "PhD", "None Required", or "Not Specified")
    Line 4: Either "Yes" or "No" (for engineering position)
    Line 5: Explain why this is or isn't an engineering position in 1-2 sentences.
    Line 6: Either "Yes" or "No" (for administrative position)
    Line 7: Explain why this is or isn't an administrative position in 1-2 sentences.
    Line 8: Either "Yes" or "No" (for trustworthy AI position)
    Line 9: Explain why this is or isn't a trustworthy AI position in 1-2 sentences.
    Line 10: Either "Yes" or "No" (for internship position)
    Line 11: Explain why this is or isn't an internship position in 1-2 sentences.
    Line 12: JSON object containing three arrays - knowledge, skills, and abilities. Format:
    {{
        "knowledge": ["knowledge1", "knowledge2", ...],
        "skills": ["skill1", "skill2", ...],
        "abilities": ["ability1", "ability2", ...]
    }}
    
    Job Description:
    {description}
    """
    
    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n', 4)
        answer = lines[0].strip()
        evidence = lines[1].strip() if len(lines) > 1 else "No evidence provided"
        degree = lines[2].strip() if len(lines) > 2 else "Not Specified"
        is_engineering = lines[3].strip() if len(lines) > 3 else "No"
        engineering_evidence = lines[4].strip() if len(lines) > 4 else "No evidence provided"
        is_admin = lines[5].strip() if len(lines) > 5 else "No"
        admin_evidence = lines[6].strip() if len(lines) > 6 else "No evidence provided"
        is_trustworthy_ai = lines[7].strip() if len(lines) > 7 else "No"
        trustworthy_ai_evidence = lines[8].strip() if len(lines) > 8 else "No evidence provided"
        is_internship = lines[9].strip() if len(lines) > 9 else "No"
        internship_evidence = lines[10].strip() if len(lines) > 10 else "No evidence provided"
        ksa_json = lines[11].strip() if len(lines) > 11 else '{"knowledge":[],"skills":[],"abilities":[]}'
        return answer, evidence, degree, is_engineering, engineering_evidence, is_admin, admin_evidence, is_trustworthy_ai, trustworthy_ai_evidence, is_internship, internship_evidence, ksa_json
    except Exception as e:
        return "Error", f"Error analyzing description: {str(e)}", "Not Specified", "No", "Error analyzing description", "No", "Error analyzing description", "No", "Error analyzing description", "No", "Error analyzing description", '{"knowledge":[],"skills":[],"abilities":[]}'

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
        df['Is Entry Level?'], df['Is Entry Level - Evidence'], df['Minimum Degree Required'], df['Is Engineering Position?'], df['Is Engineering Position - Evidence'], df['Is Administrative Position?'], df['Is Administrative Position - Evidence'], df['Is Trustworthy AI Position?'], df['Is Trustworthy AI Position - Evidence'], df['Is Internship Position?'], df['Is Internship Position - Evidence'], df['KSA_json'] = zip(*df['Job Description'].apply(
            lambda x: analyze_job_description(str(x)) if pd.notna(x) else ("No", "No description provided", "Not Specified", "No", "No description provided", "No", "No description provided", "No", "No description provided", "No", "No description provided", '{"knowledge":[],"skills":[],"abilities":[]}')
        ))
        
        # Save updated file
        output_filename = filename.replace('.xlsx', '_analyzed.xlsx')
        df.to_excel(output_filename, index=False)
        print(f"Analysis complete. Results saved to: {output_filename}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Error: Input Excel file path is required")
        print("Usage: python llm_answer.py <path_to_excel_file>")
        print("Example: python llm_answer.py xlsx/job_listings.xlsx")
        return
        
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return
        
    process_excel_file(input_file)

if __name__ == "__main__":
    main()
