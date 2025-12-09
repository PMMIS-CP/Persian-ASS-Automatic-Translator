# ass_parser.py

import re

def extract_dialogue_text_from_ass(ass_file_path):
    """
    Extracts dialogue texts from an ASS/SSA file and returns them as a list.

    Args:
        ass_file_path (str): The full path to the ASS file.

    Returns:
        list: A list of strings, where each string is a clean dialogue line.
    """
    dialogue_texts = []
    
    try:
        # Open the file with UTF-8 encoding
        with open(ass_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('Dialogue:'):
                    # Standard ASS/SSA format: text is the 10th part (index 9)
                    # after splitting by comma, allowing commas in the text itself.
                    parts = line.split(',', 9)
                    
                    if len(parts) == 10:
                        raw_text = parts[9].strip()
                        
                        # Remove ASS formatting tags (e.g., {\an5}, {\b1})
                        # which are enclosed in curly braces {}.
                        clean_text = re.sub(r'\{[^}]*\}', '', raw_text)
                        
                        if clean_text:
                            dialogue_texts.append(clean_text)
        
        return dialogue_texts

    except FileNotFoundError:
        return [f"ERROR: File not found at {ass_file_path}"]
    except Exception as e:
        return [f"ERROR processing file: {e}"]