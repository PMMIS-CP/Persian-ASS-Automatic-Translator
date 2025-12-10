import os
import re

RLE_CHAR = '\u202b'

def add_rle_to_text(text: str) -> str:
    """
    Adds the RLE (Right-to-Left Embedding) character to the beginning of the text.
    
    This function is intended for use with plain TXT files.
    """
    if text.strip():
        # Check if the text already starts with RLE
        if not text.startswith(RLE_CHAR):
            return RLE_CHAR + text
    return text

def add_rle_to_srt_line(line: str) -> str:
    """
    Adds the RLE character to the beginning of dialogue lines in an SRT file.
    
    It ignores timestamp lines, sequence number lines, and empty lines.
    """
    # Skip empty lines, timestamp lines, and sequence number lines
    if not line.strip() or re.match(r'^\s*\d+$', line) or re.match(r'^\s*\d{2}:\d{2}:\d{2}', line):
        return line
    
    # Add RLE to the beginning of dialogue lines
    return add_rle_to_text(line)

def add_rle_to_ass_dialogue(line: str) -> str:
    """
    Intelligently adds the RLE character to the dialogue text section of an ASS line.
    
    It applies the following logic:
    1. Locates the dialogue text section (after the 9th comma).
    2. Places RLE immediately after any styling codes (e.g., {\i1}, {\b1}, etc.).
    3. Places RLE after every line break separator (\ N).
    """
    
    # 1. Split the line by comma to isolate the dialogue text
    parts = line.split(',', 9)
    if len(parts) < 10 or not parts[0].strip().lower().startswith('dialogue'):
        return line # Return non-dialogue or incomplete lines untouched

    prefix = ','.join(parts[:9]) + ','
    text_content = parts[9]
    
    # Pattern to find styling codes at the start of the text (like {\i1})
    # Uses non-greedy matching to capture only the first style block
    style_match = re.match(r'^(\{.*?\})', text_content)
    
    if style_match:
        # 2. If a style code exists, place RLE after it
        style_code = style_match.group(1)
        remaining_text = text_content[len(style_code):]
        
        # 3. Add RLE after the style codes and also after every \N
        processed_text = style_code + RLE_CHAR + remaining_text.replace(r'\N', r'\N' + RLE_CHAR)
    else:
        # 3. Add RLE at the very beginning and also after every \N
        processed_text = RLE_CHAR + text_content.replace(r'\N', r'\N' + RLE_CHAR)
        
    return prefix + processed_text


# The main function process_rtl_file, called in cli_tool.py
def process_rtl_file(file_path: str, fix_words_flag: bool = False) -> str:
    """
    Opens the input file and fixes RTL texts (using RLE).
    This function supports TXT, SRT, and ASS file formats.
    
    :param file_path: The full path to the input file.
    :param fix_words_flag: Flag to enable/disable word order fixing.
      (This feature is currently not implemented in this function, but the parameter is kept for CLI compatibility)
    :return: The path to the output file or an error string.
    """
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found at {file_path}"

    base, ext = os.path.splitext(file_path)
    output_path = base + "_RLE_fixed" + ext
    
    # Determine file type and the corresponding processing function
    ext = ext.lower()
    
    if ext == '.txt':
        process_line_func = add_rle_to_text
    elif ext == '.srt':
        process_line_func = add_rle_to_srt_line
    elif ext == '.ass':
        process_line_func = add_rle_to_ass_dialogue
    else:
        return f"ERROR: Unsupported file type: {ext}. Only .txt, .srt, and .ass are supported."

    # Simple implementation logic for fix_words_flag (in case new logic needs to be added)
    if fix_words_flag:

        pass

    try:
        with open(file_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                # Apply the RLE fix only to lines that require it
                if ext == '.txt':
                    # In TXT files, all lines are processed
                    new_line = process_line_func(line.rstrip('\n')) + '\n'
                else:
                    # For SRT and ASS, only dialogue lines (and not empty lines/timestamps in SRT) are processed
                    new_line = process_line_func(line.rstrip('\n')) + '\n'
                
                outfile.write(new_line)
                
        return output_path

    except Exception as e:
        return f"ERROR: An error occurred during file processing: {e}"