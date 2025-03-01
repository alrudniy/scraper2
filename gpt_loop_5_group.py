import json
import sys
from openpyxl import load_workbook
import json
import sys
from time import sleep
from pgpt_python.client import PrivateGPTApi

def main(json_file, client):
    """
    Read JSON file and assign each list value to a broader group
    """
    # Read JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Initialize an empty dictionary to store the grouped data
    grouped_data = {}


    context = """'Mathematics & Physics', 'Engineering Principles', 'Computational Tools & Programming', 'Industry-Specific Standards & Regulations', 'System & Product Design', 'Analytical Reasoning', 'Creative Thinking & Innovation', 'Prototyping & Testing', 'Planning & Scheduling', 'Risk Assessment & Mitigation', 'Budgeting & Cost Management', 'Documentation & Reporting', 'Teamwork & Interdisciplinary Coordination', 'Mentorship & Coaching', 'Conflict Resolution', 'Influencing & Negotiation', 'Technical Writing', 'Presentations & Public Speaking', 'Listening & Interpersonal Skills', 'Visualization & Data Storytelling', 'Standards & Compliance', 'Testing & Validation', 'Lean / Six Sigma Principles', 'Root Cause Analysis', 'Industry 4.0 / Digital Transformation', 'Sustainability & Green Engineering', 'Data Analytics & AI', 'Cybersecurity (for Digital Systems)', 'Safety & Regulatory Compliance', 'Ethical Decision-Making', 'Lifelong Learning & Certifications', 'Inclusivity & Social Impact'	
              """
    ingested_text_doc_id = (
        client.ingestion.ingest_text(file_name='engineering_categories', text=context)
        .data[0]
        .doc_id
    )
    print("Ingested text doc id: ", ingested_text_doc_id)

    # Loop through each value in the list
    for value in data:

        # Send the prompt to the AI model
        prompt_result = client.contextual_completions.prompt_completion(
                        prompt =f"""Assign the following value to most appropriate group in the context. 
                                    Do not return any comments only group name:{value}""",
                        use_context=True,
                        context_filter={"docs_ids": [ingested_text_doc_id]},
                        include_sources=True,
                        ).choices[0]
        broader_group = prompt_result.message.content

        print(f"{value} --> {broader_group}")

        # Add the value to the corresponding group in the dictionary
        if broader_group in grouped_data:
            grouped_data[broader_group].append(value)
        else:
            grouped_data[broader_group] = [value]

        # Delay to avoid hitting rate limits
        # sleep(3)

    # Generate the output JSON file name
    output_filename = json_file.replace('.json', '_grouped.json')

    # Save the grouped data to a JSON file
    with open(output_filename, 'w') as json_file:
        json.dump(grouped_data, json_file, indent=2)

    print(f"Grouped data saved to {output_filename}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gpt_loop_5_group.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=600000)
    main(json_file, client)
