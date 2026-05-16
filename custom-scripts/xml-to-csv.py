import csv
import os
import sys
import xml.etree.ElementTree as ET

def convert_credentials(xml_path, csv_path):
    try:
        # Parse the XML structure
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Define the target columns matching the elements
        headers = ['url', 'name', 'username', 'password']
        
        # Open the output file for writing with proper formatting
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers) # Write the column headers
            
            # Look for any parent element containing the credential tags
            count = 0
            for parent in root.iter():
                server = parent.findtext('url')
                if server is not None:
                    username = parent.findtext('username', '')
                    password = parent.findtext('password', '')
                    data = parent.findtext('name', '')
                    
                    # Append the clean row to the CSV file
                    writer.writerow([server, username, password, data])
                    count += 1
            
            print(f"Successfully converted {count} records and saved to: {csv_path}")
            
    except ET.ParseError:
        print("Error: The file provided is not valid XML.")
    except Exception as e:
        print(f"An unexpected error occurred during parsing: {e}")

if __name__ == "__main__":
    # Get the source XML file path
    input_file = input("Enter the path to the XML file: ").strip()
    
    # Expand tilde (~) if the user typed it
    input_file = os.path.expanduser(input_file)
    
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        sys.exit(1)
        
    # Get the target CSV name
    output_name = input("Enter the name for the output CSV file (e.g., credentials.csv): ").strip()
    
    # Force the .csv extension if missing
    if not output_name.lower().endswith('.csv'):
        output_name += '.csv'
        
    # Ensure target destination points to ~/Documents safely
    documents_dir = os.path.expanduser("~/Documents")
    os.makedirs(documents_dir, exist_ok=True)
    final_output_path = os.path.join(documents_dir, output_name)
    
    # Run the processing module
    convert_credentials(input_file, final_output_path)
