import anthropic
import pandas as pd
import os
import json
from datetime import datetime

def analyze_job_description(description):
    """Analyze a job description using Anthropic's Claude API"""
    
    # Configure the model
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Create the prompt
    prompt = f"""
    Analyze this job description and answer the following questions:
    
    Job Description:
    {description}
    
    Questions:
    Line 1: Is this position related to Trustworthy AI (Yes/No)?
    Line 2: What evidence supports this classification?
    Line 3: Is this an internship position (Yes/No)?
    Line 4: What evidence supports this internship classification?
    Line 5: JSON object containing three arrays - knowledge, skills, and abilities. Format:
    {{
        "knowledge": ["knowledge1", "knowledge2", ...],
        "skills": ["skill1", "skill2", ...],
        "abilities": ["ability1", "ability2", ...]
    }}
    
    Respond with exactly 5 lines, no additional text.
    """
    
    # Generate response using Claude
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        system="You are a helpful assistant that analyzes job descriptions. Always respond with exactly 5 lines as requested.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Split response into lines
    lines = response.content[0].text.strip().split('\n')
    
    if len(lines) != 5:
        raise ValueError(f"Expected 5 lines in response, got {len(lines)}")

    # Parse the response
    trustworthy_ai = lines[0].strip()
    evidence_ai = lines[1].strip()
    internship = lines[2].strip()
    evidence_internship = lines[3].strip()
    
    try:
        ksa = json.loads(lines[4].strip())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse KSA JSON from response")

    return pd.DataFrame([{
        'Trustworthy_AI': trustworthy_ai,
        'Trustworthy_AI_Evidence': evidence_ai,
        'Internship': internship,
        'Internship_Evidence': evidence_internship,
        'KSA': json.dumps(ksa)
    }])

def process_excel_file(input_file):
    """Process job descriptions from an Excel file"""
    
    # Read the Excel file
    df = pd.read_excel(input_file)
    
    # Ensure required column exists
    if 'Job Description' not in df.columns:
        raise ValueError("Excel file must contain a 'Job Description' column")
    
    # Initialize empty lists for results
    results = []
    
    # Process each job description
    for desc in df['Job Description']:
        if pd.isna(desc):
            continue
            
        try:
            result = analyze_job_description(desc)
            results.append(result)
        except Exception as e:
            print(f"Error processing description: {str(e)}")
            continue
    
    # Combine all results
    if not results:
        raise ValueError("No job descriptions were successfully processed")
        
    final_df = pd.concat(results, ignore_index=True)
    
    # Add timestamp column
    final_df['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Generate output filename
    input_base = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"{input_base}_analyzed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Save to Excel
    final_df.to_excel(output_file, index=False)
    print(f"Analysis complete. Results saved to {output_file}")
    
    return output_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python llm_anthropic.py <input_excel_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
        
    try:
        output_file = process_excel_file(input_file)
        print(f"Successfully processed {input_file}")
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
