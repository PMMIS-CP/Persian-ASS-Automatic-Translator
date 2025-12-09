# prefix_remover.py

import re
import os

def remove_line_prefixes(input_file_path):
    """
    Removes sequential prefixes (e.g., '1-', '10-', '100-') from the beginning 
    of each line in a text file.

    Args:
        input_file_path (str): The full path to the input TXT file.

    Returns:
        str: The path to the newly created output file or an ERROR message.
    """
    
    # Regular expression to match one or more digits at the start of a line, 
    # followed by a hyphen ('-') and optional spaces.
    # The pattern is: ^\d+- *
    # ^ : start of the line
    # \d+ : one or more digits
    # - : a literal hyphen
    # * : zero or more spaces (in case of '1- text' or '1-  text')
    PREFIX_PATTERN = re.compile(r'^\d+- *')
    
    # 1. Determine output file path
    base_name, ext = os.path.splitext(input_file_path)
    if ext.lower() != '.txt':
        return f"ERROR: Input file must be a .txt file. Received extension: {ext}"
    
    output_file_path = base_name + "_no_prefix.txt"
    
    try:
        # Read the entire content
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        
        # 2. Process lines and remove prefixes
        processed_lines = []
        for line in lines:
            # Use the regex pattern to substitute the prefix with an empty string
            clean_line = PREFIX_PATTERN.sub('', line)
            processed_lines.append(clean_line)
            
        # 3. Write the cleaned content to the new output file
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(processed_lines)
        
        return output_file_path

    except FileNotFoundError:
        return f"ERROR: File not found at {input_file_path}"
    except Exception as e:
        return f"ERROR processing file: {e}"