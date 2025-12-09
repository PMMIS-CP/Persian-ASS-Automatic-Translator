# rtl_fixer.py (UPDATED VERSION)

import re
import os

def fix_rtl_punctuation(text):
    """
    Swaps specific punctuation marks (period, ellipsis, Persian comma, exclamation mark)
    from the end of the sentence to the beginning to resolve LTR issues in Persian text.
    
    Example: "سلام!!" is converted to "!!سلام" (Hello!!)
    """
    
    # 1. Define the necessary punctuation marks to move (without semicolon and with Persian comma)
    # Marks include: period (.), ellipsis (...), Persian comma (،), and exclamation mark (!)
    # Note: Ellipsis (.{3}) must be placed before the regular period (.) in the pattern to be correctly identified.
    PUNCTUATIONS_TO_MOVE_GROUP = r"(\.{3}|،|\.|!)"
    
    # 2. Define the Pattern to detect **one or more repetitions** of marks at the end of the string
    # (.*?) - Group 1: The main text before the punctuation
    # (\s*) - Group 2: Zero or more whitespaces (optional)
    # (PUNCTUATIONS_TO_MOVE_GROUP + r"+") - Group 3: One or more repetitions of the defined marks (Example: !!!)
    # $ - End of string
    # "?" and ";" have been omitted.
    
    # We use a more general structure instead of PUNCTUATIONS_TO_MOVE_GROUP to support repetition
    # [Main Change]: Use the repeating pattern (PUNCTUATIONS_TO_MOVE_GROUP) +
    
    # Building the punctuation group:
    # ((\.{3})|،|\.|!)+  <- This ensures one or more occurrences of these marks exist.
    # We must be careful that '.' and '...' do not conflict.
    
    # Pattern:
    pattern_string = r"(.*?)(\s*)((\.{3})|،|\.|!)+"
    pattern = re.compile(pattern_string + r"$")

    match = pattern.search(text)

    if match:
        # Group 1: Main text before punctuation (Example: "سلام! خوبی؟! اونو")
        # Group 2: Whitespace before punctuation (optional)
        # Group 3: The entire punctuation string (Example: "!!!")
        
        # To extract the entire punctuation string, we should use match.group(3), but since the repetition structure (pattern_string)
        # might generate more groups, extracting the trailing mark is slightly more complex.
        # A simpler and more reliable solution is to use a manual check from the end of the string:
        
        # First, separate all trailing punctuation.
        stripped_text = text.rstrip()
        trailing_punctuation = ""
        main_text = stripped_text
        
        # Loop over characters from the end to collect punctuation
        for char in reversed(stripped_text):
            # If the character is a space or not one of our allowed marks, break the loop.
            if char.isspace() or (char not in ['.', '،', '!'] and char != '؛' and char != '?'):
                break
                
            # If ellipsis is present, it must be separated as a whole unit
            if stripped_text.endswith("..."):
                trailing_punctuation = "..." + trailing_punctuation
                main_text = stripped_text[:-3].rstrip()
                break # Finished collection
            
            # If the mark is allowed
            if char in ['.', '،', '!']:
                trailing_punctuation = char + trailing_punctuation
                main_text = main_text[:-1].rstrip()
            else:
                break # Irrelevant character found
        
        # If punctuation was found and the main text was not empty
        if trailing_punctuation: # and main_text:
            return trailing_punctuation + main_text
    
    # If no pattern was found, return the text unchanged
    return text

def process_rtl_file(input_file_path):
    """
    Main reader and processor for the text file (TXT) to apply RTL correction.
    """
    
    print(f"Loading file for RTL correction: {input_file_path}")
    
    if not os.path.exists(input_file_path):
        return f"ERROR: Input file not found at: {input_file_path}"
        
    try:
        # 1. Read all lines from the input file
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
            
        fixed_lines = []
        for line in lines:
            # Remove leading/trailing whitespace and then apply correction
            clean_line = line.strip()
            if clean_line:
                # Replace English comma with Persian comma before applying RTL correction
                line_with_persian_comma = clean_line.replace(',', '،')
                
                fixed_line = fix_rtl_punctuation(line_with_persian_comma)
                fixed_lines.append(fixed_line)
            else:
                # Preserve empty lines
                fixed_lines.append("")
        
        # 2. Determine the path and name of the output file (format: filename_RTL.txt)
        base_name, ext = os.path.splitext(input_file_path)
        output_file_path = base_name + "_RTL" + ext
        
        # 3. Save the output
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            # Add a newline after each line
            # We remove the extra trailing \n character so the file conforms to a standard text line format
            outfile.write('\n'.join(fixed_lines))
            
        return output_file_path
        
    except Exception as e:
        return f"ERROR: Failed during file processing or saving: {e}"

if __name__ == '__main__':
    # This section is for manual testing only and is not used in CLI.
    pass