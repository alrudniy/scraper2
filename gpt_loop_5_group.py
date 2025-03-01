import json
import sys
from openpyxl import load_workbook
import json
import sys
from time import sleep
import anthropic

def main(json_file):
    """
    Read JSON file and assign each list value to a broader group
    """
    # Read JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Initialize an empty dictionary to store the grouped data
    grouped_data = {}

    # Initialize the Anthropic client
    client = anthropic.Client(api_key="your-api-key")

    # Loop through each value in the list
    for value in data:
        # Prepare the prompt
        prompt = f"Assign the following value to a broader group:\n\n{value}\n\nBroader group:"

        # Send the prompt to the AI model
        response = client.completion(
            prompt=prompt,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            max_tokens_to_sample=50,
            model="claude-v1",
        )

        # Extract the broader group from the response
        broader_group = response["completion"].strip()

        # Add the value to the corresponding group in the dictionary
        if broader_group in grouped_data:
            grouped_data[broader_group].append(value)
        else:
            grouped_data[broader_group] = [value]

        # Delay to avoid hitting rate limits
        sleep(3)

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
    main(json_file)
