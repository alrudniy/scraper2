import pandas as pd

def capitalize_ksa():
    # Read the Excel file
    df = pd.read_excel('ksa_frequencies_v7_manual.xlsx')
    
    # Function to capitalize first letter of each word if it's lowercase
    def capitalize_if_lowercase(text):
        # Convert to string if not already
        text = str(text)
        words = text.split()
        capitalized_words = []
        for word in words:
            if word[0].islower():
                word = word.capitalize()
            capitalized_words.append(word)
        return ' '.join(capitalized_words)
    
    # Apply capitalization to KSA column
    df['KSA'] = df['KSA'].apply(capitalize_if_lowercase)
    
    # Export to Excel
    output_file = 'ksa_frequencies_v8.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Processed KSA frequencies have been exported to '{output_file}'")
    print(f"Total KSAs processed: {len(df)}")

if __name__ == "__main__":
    capitalize_ksa()
