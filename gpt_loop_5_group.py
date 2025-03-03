import json
import sys
from openpyxl import load_workbook
import json
import sys
from time import sleep
from pgpt_python.client import PrivateGPTApi
from collections import Counter

import json
from datetime import datetime
# from time import sleep   # uncomment if you want to include delays

def main(json_file, client):
    """
    Read JSON file containing a list of values and classify each value into groups.
    Groups are dynamically created/updated based on AI's prompt_completion response.
    """
    # Read JSON file (assumed to contain a list of values)
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Count the occurrences of each element in the list
    occurrences = dict(Counter(data))

    
    # Create the output file name by replacing '.json' with '_counts.json'
    output_file = json_file.replace('.json', '_counts.json')
    with open(output_file, 'w') as file:
        json.dump(occurrences, file, indent=4)  # indent=4 for pretty formatting




if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gpt_loop_5_group.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    # Initialize PGPT client with default settings
    client = PrivateGPTApi(base_url="http://localhost:8001", timeout=600000)
    main(json_file, client)
